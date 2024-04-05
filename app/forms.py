from asgiref.sync import sync_to_async
from django import forms
from django.contrib.admin.widgets import AdminTextInputWidget
from .models import Instrument
from .services.repositories.spread_repositories import SpreadRepository
from .services.services import calculate_spread
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
        base_price = get_base_price(self.cleaned_data['base'])
        future_price = get_future_price(self.cleaned_data['future'])

        # Сохранение цен в базу данных
        instrument.name = self.cleaned_data['name']
        instrument.base = base_price
        instrument.future = future_price

        spread = calculate_spread(instrument)
        SpreadRepository.add_spread(instrument.name, spread)

        if commit:
            instrument.save()
        return instrument
