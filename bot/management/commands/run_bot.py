from django.core.management.base import BaseCommand
from bot.bot_handler import run_bot
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_telegram_bot.settings')

class Command(BaseCommand):
    help = 'Запускає Telegram-бот'

    def handle(self, *args, **kwargs):
        run_bot()