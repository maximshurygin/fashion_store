from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, FormView, TemplateView

from store.forms import OrderCreateForm, ContactForm
from store.models import Product, ProductInventory, Cart, CartItem, FavouriteItem, Category, OrderItem, Order
from store.task import send_email


def index(request):
    return render(request, 'store/index.html', context={'title': 'Главная страница'})


def about(request):
    return render(request, 'store/about.html', context={'title': 'О нас'})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            send_email.delay(
                subject=f'Сообщение от {email}',
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
            )

            return redirect('store:contact_success')
    else:
        form = ContactForm()

    return render(request, 'store/contact.html', context={'title': 'Контакты', 'form': form})


def returns(request):
    return render(request, 'store/returns.html')


def info(request):
    return render(request, 'store/info.html', context={'title': 'Помощь'})


class ProductList(ListView):
    model = Product
    template_name = 'store/product_list.html'
    context_object_name = 'object_list'  # Соответствует вашему шаблону
    extra_context = {'title': 'Товары'}
    paginate_by = 12

    def get_queryset(self):
        # Получение gender из kwargs (URL) или из GET-параметров
        gender = self.kwargs.get('gender') or self.request.GET.get('gender')
        category = self.request.GET.get('category')

        # Создание уникального ключа для кэша на основе фильтров
        cache_key = f'product_list_{gender}_{category}'
        queryset = cache.get(cache_key)
        if not queryset:
            queryset = super().get_queryset().select_related('category', 'brand')
            if gender in ['M', 'F']:
                queryset = queryset.filter(gender__in=[gender, 'U'])
            elif gender in ['U']:
                queryset = queryset.filter(gender='U')
            if category:
                queryset = queryset.filter(category__slug=category)
            cache.set(cache_key, queryset, 600)  # Правильное использование
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gender = self.kwargs.get('gender') or self.request.GET.get('gender')

        if gender:
            # Фильтруем категории, которые имеют товары для выбранного пола
            categories = Category.objects.filter(products__gender__in=[gender, 'U']).distinct()
        else:
            # Если пол не выбран, показываем все категории, которые имеют товары
            categories = Category.objects.filter(products__isnull=False).distinct()

        context['categories'] = categories
        context['current_gender'] = gender or ''
        context['current_category'] = self.request.GET.get('category', '')
        return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['categories'] = Category.objects.all()
    #     context['current_gender'] = self.kwargs.get('gender') or self.request.GET.get('gender', '')
    #     context['current_category'] = self.request.GET.get('category', '')
    #     return context


class ProductDetail(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    extra_context = {'title': 'Информация о товаре'}

    def get_queryset(self):
        return Product.objects.select_related('category', 'brand').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        cache_key = f'product_inventories_{product.id}'
        product_inventories = cache.get(cache_key)

        if not product_inventories:
            product_inventories = ProductInventory.objects.filter(product=product, stock__gt=0).select_related('size',
                                                                                                               'color').prefetch_related(
                'product__images')
            cache.set(cache_key, product_inventories, 60)
        context['product_inventories'] = product_inventories
        return context


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart = request.session.get('cart_id')
        if cart:
            cart = Cart.objects.filter(id=cart, user__isnull=True).first()
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    return cart


class AddFavouriteView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Вы должны быть авторизованы для добавления в избранное')
            return redirect('users:login')

        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        favourite, created = FavouriteItem.objects.get_or_create(user=request.user, product=product)
        if created:
            messages.success(request, 'Товар добавлен в избранное')
        else:
            messages.info(request, 'Товар уже находится в избранном')
        return redirect(request.META.get('HTTP_REFERER', 'store:index'))


class RemoveFavouriteView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        try:
            favourite = FavouriteItem.objects.get(user=request.user, product=product)
            favourite.delete()
            messages.success(request, 'Товар удален из избранного')
        except FavouriteItem.DoesNotExist:
            messages.error(request, 'Товар отсутствует в избранном')
        return redirect(request.META.get('HTTP_REFERER', 'store:index'))


class FavouriteList(ListView):
    model = FavouriteItem
    template_name = 'store/favourites.html'
    extra_context = {'title': 'Избранное'}


class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Вы должны быть авторизованы для добавления в корзину')
            return redirect('users:login')

        product_inventory_id = request.POST.get('product_inventory_id')
        quantity = int(request.POST.get('quantity', 1))

        product_inventory = get_object_or_404(ProductInventory, id=product_inventory_id)
        cart = get_or_create_cart(request)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_inventory=product_inventory,
        )

        if not created:
            cart_item.quantity = F('quantity') + quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()
        messages.success(request, 'Товар добавлен в корзину.')

        # Перенаправление на ту же страницу, с которой был отправлен запрос
        referer = request.META.get('HTTP_REFERER', '/')
        return HttpResponseRedirect(referer)


class CartDetailView(View):
    def get(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        items = cart.items.select_related(
            'product_inventory__product__category',  # Добавляем категорию продукта
            'product_inventory__product__brand',  # Добавляем бренд продукта
            'product_inventory__size',
            'product_inventory__color'
        )
        total_price = cart.total_price
        context = {
            'cart': cart,
            'items': items,
            'total_price': total_price,
        }
        return render(request, 'store/cart_detail.html', context)


class UpdateCartItemView(View):
    def post(self, request, *args, **kwargs):
        cart_item_id = request.POST.get('cart_item_id')
        quantity = int(request.POST.get('quantity', 1))

        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Количество товара обновлено.')
        else:
            cart_item.delete()
            messages.success(request, 'Товар удален из корзины.')

        return redirect('store:cart_detail')  # Используйте двоеточие вместо слеша


class RemoveFromCartView(View):
    def post(self, request, *args, **kwargs):
        cart_item_id = request.POST.get('cart_item_id')

        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart=cart)
        cart_item.delete()

        messages.success(request, 'Товар удален из корзины.')
        return redirect('store:cart_detail')


class CreateOrderView(LoginRequiredMixin, FormView):
    template_name = 'store/order_create.html'
    form_class = OrderCreateForm
    success_url = reverse_lazy('store:order_success')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем корзину пользователя
        cart = Cart.objects.filter(user=self.request.user).first()
        context['cart'] = cart
        return context

    def form_valid(self, form):
        cart = Cart.objects.filter(user=self.request.user).first()
        if not cart or not cart.items.exists():
            form.add_error(None, 'Ваша корзина пуста')
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                order = form.save(commit=False)
                order.user = self.request.user
                order.save()

                for item in cart.items.select_related('product_inventory__product'):
                    OrderItem.objects.create(
                        order=order,
                        product_inventory=item.product_inventory,
                        quantity=item.quantity,
                        price=item.product_inventory.product.price
                    )

                order.calculate_total_price()
                order.save(update_fields=['total_price'])

                cart.items.all().delete()

                messages.success(self.request, 'Ваш заказ успешно оформлен!')

                self.send_order_confirmation_email(order)

                return redirect('store:order_detail', order_id=order.id)

        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception:
            import traceback
            print(traceback.format_exc())
            form.add_error(None, 'Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже.')
            return self.form_invalid(form)

    def send_order_confirmation_email(self, order):
        subject = f'Подтверждение заказа #{order.id}'
        message = (
            f'Здравствуйте, {order.user.fullname}!\n\n'
            f'Ваш заказ #{order.id} был успешно оформлен.\n'
            f'Дата заказа: {order.created_at}\n'
            f'Общая стоимость: {order.total_price} ₽\n\n'
            f'Адрес доставки:\n{order.delivery_address}\n\n'
            f'Спасибо за покупку!'
        )
        recipient_list = [order.user.email]
        send_email.delay(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'store/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'store/order_success.html'


class CancelOrderView(LoginRequiredMixin, View):
    def post(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status in ['C', 'F']:
            messages.error(request, 'Этот заказ уже завершен или отменен.')
            return redirect('store:order_detail', order_id=order.id)

        try:
            with transaction.atomic():
                order.cancel_order()
                messages.success(request, 'Ваш заказ был успешно отменен.')
        except Exception as e:
            messages.error(request, 'Произошла ошибка при отмене заказа. Пожалуйста, попробуйте позже.')

        return redirect('store:order_detail', order_id=order.id)
