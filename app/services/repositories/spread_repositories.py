from asgiref.sync import sync_to_async

from app.models import Spread


class SpreadRepository:
    @staticmethod
    @sync_to_async
    def add_spread(asset_name, spread):
        new_spread = Spread(asset_name=asset_name, spread=spread)
        new_spread.save()

    @staticmethod
    @sync_to_async
    def get_spread_by_asset_name(asset_name):
        asset = Spread.objects.get(asset_name=asset_name)
        return asset.spread

    @staticmethod
    @sync_to_async
    def get_all_spreads():
        return [spread.value for spread in Spread.objects.all()]

    @staticmethod
    @sync_to_async
    def update_spread(asset_name, spread):
        current_spread = Spread.objects.get(asset_name=asset_name)
        current_spread.spread = spread
        current_spread.save()

    @staticmethod
    @sync_to_async
    def delete_spread(asset_name):
        spread = Spread.objects.get(asset_name=asset_name)
        spread.delete()
