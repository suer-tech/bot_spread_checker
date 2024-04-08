import asyncio

from django.shortcuts import render, redirect, get_object_or_404

from app.api.find_ticker import find_share, find_future
from app.api.tinkoff_api import subscribe_price
from app.models import Instrument


async def get_base_price(value):
    asset = await find_share(value)
    processed_price = await subscribe_price(asset)
    print(processed_price)
    return processed_price


async def get_future_price(value):
    asset = await find_future(value)
    processed_price = await subscribe_price(asset)
    return processed_price


def instrument_list(request):
    instruments = Instrument.objects.all()
    return render(request, 'instrument_list.html', {'instruments': instruments})

