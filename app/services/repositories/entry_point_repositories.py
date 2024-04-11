from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from app.models import EntriesPoint


class EntriesPointRepository:
    @staticmethod
    @sync_to_async
    def add_entries_point(asset_name, entry_point):
        entries_point = EntriesPoint(asset_name=asset_name, entry_point=entry_point)
        entries_point.save()

    @staticmethod
    @sync_to_async
    def get_entries_point_by_asset_name(asset_name):
        try:
            entry_point = EntriesPoint.objects.get(asset_name=asset_name)
            return entry_point
        except ObjectDoesNotExist:
            print(f"Запись с asset_name '{asset_name}' не найдена.")
            return None  # Или выполните другие действия по вашему усмотрению

    @staticmethod
    @sync_to_async
    def get_all_entries_points():
        entry_point = None
        entry_points = [(inst.asset_name, inst.entry_point) for inst in EntriesPoint.objects.all()]
        if len(entry_points) > 0:
            entry_point = entry_points[0][0]
        return entry_point

    @staticmethod
    @sync_to_async
    def update_entries_point_age(asset_name, entry_point):
        entries_point = EntriesPoint.objects.get(asset_name=asset_name)
        entries_point.age = entry_point
        entries_point.save()

    @staticmethod
    @sync_to_async
    def delete_entries_point(asset_name):
        entries_point = EntriesPoint.objects.get(asset_name=asset_name)
        entries_point.delete()
