from django import forms
from django.contrib.admin.widgets import AdminTextInputWidget
from .models import Instrument
from .views import get_base_price, get_future_price


class PriceInputWidget(AdminTextInputWidget):
    def __init__(self, *args, **kwargs):
        kwargs['attrs'] = {'class': 'price-input'}
        super().__init__(*args, **kwargs)


class InstrumentForm(forms.ModelForm):
    base = forms.CharField(label='Base', widget=PriceInputWidget)
    future = forms.CharField(label='Future', widget=PriceInputWidget)

    class Meta:
        model = Instrument
        fields = ['name', 'base', 'future']
        exclude = ['base', 'future']

    def save(self, commit=True):
        instrument = super().save(commit=False)

        # Получение цены базового актива и фьючерса из введенных пользователем данных
        name = self.fields['name']
        base_price = get_base_price(self.cleaned_data['base'])
        future_price = get_future_price(self.cleaned_data['future'])

        # Сохранение цен в базу данных
        instrument.name = name
        instrument.base = base_price
        instrument.future = future_price

        if commit:
            instrument.save()
        return instrument
