from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView
from django.urls import path, reverse_lazy

from store.views import index, about, contact, ProductList, ProductDetail
from users.apps import UsersConfig
from users.forms import PasswordResetCustomForm, SetPasswordCustomForm, UserPasswordChangeForm
from users.views import UserLoginView, RegisterView, activate, email_sent_success, ProfileView, UserPasswordChange

# from users.views import RegisterView, UserLoginView

app_name = UsersConfig.name

urlpatterns = [
    path('', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('email_sent/', email_sent_success, name='email_sent'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password_reset/',
         PasswordResetView.as_view(
             email_template_name='users/password_reset_email.html',
             template_name='users/password_reset_form.html',
             form_class=PasswordResetCustomForm,
             success_url=reverse_lazy('users:password_reset_done')
         ), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             form_class=SetPasswordCustomForm,
             template_name='users/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete')
         ), name='password_reset_confirm'),
    path('password_reset/complete/',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
    path('password_change/', UserPasswordChange.as_view(), name='password_change'),
    path('password_change_done/', PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done')
]
