from django.core.management.base import BaseCommand

from app.telegram.bot import start_bot


class Command(BaseCommand):
    help = 'Starts the Telegram bot'

    def handle(self, *args, **options):
        start_bot()