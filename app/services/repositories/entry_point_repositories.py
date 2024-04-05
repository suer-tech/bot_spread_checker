from asgiref.sync import sync_to_async

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
        return EntriesPoint.objects.get(asset_name=asset_name)

    @staticmethod
    @sync_to_async
    def get_all_entries_points():
        entry_point = None
        entry_points = EntriesPoint.objects.all()
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
