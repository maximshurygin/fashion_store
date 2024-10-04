from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView, UpdateView

from store.models import Order
from users.forms import RegisterUserForm, LoginUserForm, ProfileUserForm, UserPasswordChangeForm

from django.contrib.auth.views import LoginView, PasswordChangeView

from users.models import User
from users.task import send_user_email
from users.utils import account_activation_token


# Create your views here.

class ProfileView(UpdateView):
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    form_class = ProfileUserForm
    extra_context = {'title': 'Мой аккаунт'}

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        orders = Order.objects.filter(user=user).order_by('-created_at')
        context['orders'] = orders
        context['title'] = 'Профиль пользователя'
        return context


class UserLoginView(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Вход'}


class RegisterView(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    extra_context = {'title': 'Регистрация'}

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Делаем пользователя неактивным до подтверждения email
        user.save()

        # Генерируем токен и ссылку для активации
        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = self.request.build_absolute_uri(
            reverse('users:activate', kwargs={'uidb64': uid, 'token': token})
        )

        # HTML-сообщение
        html_message = f'''
        <p>Спасибо за регистрацию! Для активации вашего аккаунта, пожалуйста, перейдите по следующей ссылке:</p>
        <p><a href="{activation_link}">Подтвердить email</a></p>
        <p>Если вы не регистрировались на нашем сайте, проигнорируйте это письмо.</p>
        '''

        # Отправляем письмо
        send_user_email.delay(
            subject='Подтверждение регистрации',
            message=f'Перейдите по следующей ссылке для подтверждения: {activation_link}',
            # Текстовое сообщение на случай, если HTML не поддерживается
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message  # HTML-версия письма
        )

        return redirect('users:email_sent')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True  # Активируем пользователя
        user.save()
        return redirect('users:login')
    else:
        return render(request, 'users/activation_failed.html')


def email_sent_success(request):
    return render(request, 'users/email_sent_success.html')


class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'
