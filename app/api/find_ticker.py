import asyncio

from tinkoff.invest import (
    Client
)

from app.api.api_config import tinkoff_token


async def find_share(isin):
    with Client(tinkoff_token) as client:
        inst = client.instruments.find_instrument(query=isin)
        for cur in inst.instruments:
            if cur.class_code == 'TQBR' and cur.isin == isin:
                print('')
                print(f'find_share: {cur}')
                print('')
                return cur


async def find_future(ticker):
    with Client(tinkoff_token) as client:
        inst = client.instruments.find_instrument(query=ticker)
        for cur in inst.instruments:
            if cur.class_code == 'SPBFUT' and cur.ticker == ticker:
                print('')
                print(f'find_future: {cur}')
                print('')
                return cur


