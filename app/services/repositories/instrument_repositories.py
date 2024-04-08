from asgiref.sync import sync_to_async
from app.models import Instrument
from app.services.repositories.spread_repositories import SpreadRepository
from app.services.services import calculate_spread


class InstrumentRepository:
    @staticmethod
    @sync_to_async
    def add_instrument(asset_name, base, future):
        instrument = Instrument(asset_name=asset_name, base=base, future=future)
        instrument.save()

    @staticmethod
    @sync_to_async
    def get_instrument_by_asset_name(asset_name):
        return Instrument.objects.get(asset_name=asset_name)

    @staticmethod
    @sync_to_async
    def get_all_instruments():
        return [inst.name for inst in Instrument.objects.all()]

    @staticmethod
    @sync_to_async
    def update_instrument_age(asset_name, new_age):
        user = Instrument.objects.get(asset_name=asset_name)
        user.age = new_age
        user.save()

    @staticmethod
    @sync_to_async
    def delete_instrument(asset_name):
        user = Instrument.objects.get(asset_name=asset_name)
        user.delete()
