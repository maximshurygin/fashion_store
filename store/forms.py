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
