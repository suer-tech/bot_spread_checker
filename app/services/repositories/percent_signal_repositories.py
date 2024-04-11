from asgiref.sync import sync_to_async

from app.models import PercentSignal


class PercentSignalRepository:
    @staticmethod
    @sync_to_async
    def add_percent_signal(asset_name, percent_signal):
        new_percent_signal = PercentSignal(asset_name=asset_name, percent_signal=percent_signal)
        new_percent_signal.save()

    @staticmethod
    @sync_to_async
    def get_percent_signal_by_asset_name(asset_name):
        return PercentSignal.objects.get(asset_name=asset_name)

    @staticmethod
    @sync_to_async
    def get_all_percent_signals():
        return [(inst.asset_name, inst.percent_signal) for inst in PercentSignal.objects.all()]

    @staticmethod
    @sync_to_async
    def update_percent_signal_percent_signal(asset_name, new_percent_signal):
        percent_signal = PercentSignal.objects.get(asset_name=asset_name)
        percent_signal.percent_signal = new_percent_signal
        percent_signal.save()

    @staticmethod
    @sync_to_async
    def delete_percent_signal(asset_name):
        percent_signal = PercentSignal.objects.get(asset_name=asset_name)
        percent_signal.delete()
