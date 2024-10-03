from django import forms

from store.models import Order


class OrderCreateForm(forms.ModelForm):
    delivery_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Адрес доставки', required=True)

    class Meta:
        model = Order
        fields = ['delivery_address']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.address:
            self.fields['delivery_address'].initial = user.address


class ContactForm(forms.Form):
    email = forms.EmailField(label='Ваш E-mail', max_length=100, widget=forms.EmailInput(attrs={
        'class': 'stext-111 cl2 plh3 size-116 p-l-62 p-r-30'}))
    message = forms.CharField(label='Чем мы можем помочь?',
                              widget=forms.Textarea(attrs={'class': 'stext-111 cl2 plh3 size-120 p-lr-28 p-tb-25'
                                                           }))
