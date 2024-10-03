from store.models import Cart, FavouriteItem
from store.views import get_or_create_cart
from django.db.models import Sum


# def cart_context(request):
#     cart = get_or_create_cart(request)
#     cart_items = cart.items.select_related(
#         'product_inventory__product',
#         'product_inventory__size'
#     )
#     return {
#         'header_cart': cart,
#         'header_cart_items': cart_items,
#     }

def cart_context(request):
    cart = get_or_create_cart(request)
    # Предзагрузка изображений продуктов через prefetch_related
    cart_items = cart.items.select_related(
        'product_inventory__product__category',
        'product_inventory__product__brand',
        'product_inventory__size',
        'product_inventory__color'
    ).prefetch_related('product_inventory__product__images')  # Предзагрузка изображений

    return {
        'header_cart': cart,
        'header_cart_items': cart_items,
    }



# def cart_item_count(request):
#     if request.user.is_authenticated:
#         cart = Cart.objects.filter(user=request.user).first()
#     else:
#         cart_id = request.session.get('cart_id')
#         cart = Cart.objects.filter(id=cart_id, user__isnull=True).first()
#
#     cart_items_count = cart.items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] if cart else 0
#     return {
#         'cart_items_count': cart_items_count or 0
#     }

def cart_item_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).select_related('user').first()
    else:
        cart_id = request.session.get('cart_id')
        cart = Cart.objects.filter(id=cart_id, user__isnull=True).first()

    cart_items_count = cart.items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] if cart else 0
    return {
        'cart_items_count': cart_items_count or 0
    }


def favorites_count(request):
    if request.user.is_authenticated:
        favorite_count = FavouriteItem.objects.filter(user=request.user).count()
    else:
        favorite_count = 0
    return {'favorites_count': favorite_count}


# def user_favourites(request):
#     if request.user.is_authenticated:
#         favorites = FavouriteItem.objects.filter(user=request.user)
#         user_favourite_items = [favorite.product for favorite in favorites]
#     else:
#         user_favourite_items = []
#     return {'user_favorites': user_favourite_items}

def user_favourites(request):
    if request.user.is_authenticated:
        # Используем select_related для подгрузки связанных продуктов
        favorites = FavouriteItem.objects.filter(user=request.user).select_related('product__category',
                                                                                   'product__brand')
        user_favourite_items = [favorite.product for favorite in favorites]
    else:
        user_favourite_items = []
    return {'user_favorites': user_favourite_items}
