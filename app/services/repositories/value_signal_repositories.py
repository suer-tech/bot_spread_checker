from asgiref.sync import sync_to_async

from app.models import ValueSignal


class ValueSignalRepository:
    @staticmethod
    @sync_to_async
    def add_value_signal(asset_name, value_signal):
        new_value_signal = ValueSignal(asset_name=asset_name, value_signal=value_signal)
        new_value_signal.save()

    @staticmethod
    @sync_to_async
    def get_value_signal_by_asset_name(asset_name):
        return ValueSignal.objects.get(asset_name=asset_name)

    @staticmethod
    @sync_to_async
    def get_all_value_signals():
        return [(inst.asset_name, inst.value_signal) for inst in ValueSignal.objects.all()]

    @staticmethod
    @sync_to_async
    def update_value_signal_age(asset_name, new_signal):
        value_signal = ValueSignal.objects.get(asset_name=asset_name)
        value_signal.age = new_signal
        value_signal.save()

    @staticmethod
    @sync_to_async
    def delete_value_signal(asset_name):
        value_signal = ValueSignal.objects.get(asset_name=asset_name)
        value_signal.delete()
