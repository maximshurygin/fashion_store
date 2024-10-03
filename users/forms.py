from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordResetForm, \
    SetPasswordForm, PasswordChangeForm
from django.core.exceptions import ValidationError


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class LoginUserForm(StyleFormMixin, AuthenticationForm):
    pass


class RegisterUserForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2')


class ProfileUserForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'fullname', 'phone', 'address')
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True


class PasswordResetCustomForm(StyleFormMixin, PasswordResetForm):
    pass


class SetPasswordCustomForm(StyleFormMixin, SetPasswordForm):
    pass

class UserPasswordChangeForm(StyleFormMixin, PasswordChangeForm):
    pass