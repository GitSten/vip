from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'gift', 'comment']  # Add 'comment' to the list of fields
        labels = {
            'product': 'Toode',
            'gift': 'Vali toode, seejärel vajuta kasti linnuke, et muuta merch staatus ja seejärel salvesta!  ',
            'comment': 'Kommentaar/Lisainfo',  # Add label for the 'comment' field
        }