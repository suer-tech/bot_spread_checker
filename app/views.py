from django.shortcuts import render, redirect, get_object_or_404

from .api.find_ticker import find_share, find_future
from .api.tinkoff_api import subscribe_price
from .models import Instrument


def get_base_price(value):
    asset = find_share(value)
    processed_price = subscribe_price(asset)
    return processed_price


def get_future_price(value):
    asset = find_future(value)
    processed_price = subscribe_price(asset)
    return processed_price


def instrument_list(request):
    instruments = Instrument.objects.all()
    return render(request, 'instrument_list.html', {'instruments': instruments})
