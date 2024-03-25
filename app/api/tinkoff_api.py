from tinkoff.invest.services import MarketDataStreamManager

from tinkoff.invest import (
    CandleInstrument,
    Client,
    InfoInstrument,
    SubscriptionInterval,
)

from .api_config import tinkoff_token

TOKEN = tinkoff_token


def subscribe_price(asset):
    print(asset)
    with Client(TOKEN) as client:
        market_data_stream: MarketDataStreamManager = client.create_market_data_stream()
        market_data_stream.candles.waiting_close().subscribe(
            [
                CandleInstrument(
                    figi=asset.figi,
                    interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                )
            ]
        )

        for marketdata in market_data_stream:
            if marketdata.candle:
                last_price = marketdata.candle.close
                print(last_price)

                last_price_units = last_price.units
                last_price_nano = last_price.nano

                # Преобразование в число с учетом nano
                numeric_value = float(f"{last_price_units}.{last_price_nano}")
                return numeric_value

