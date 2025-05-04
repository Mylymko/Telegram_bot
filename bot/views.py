from .models import UserSettings
from django.http import HttpResponse
import os
import logging

logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
def bot_home(request):
    """ Ендпоінт для перевірки роботи бота."""
    return HttpResponse("Welcome to my Telegram Bot!")


async def get_response_text(user, message_type):
    """
    Вертає текст повідомлення залежно від мови, обраної користувачем.

    Args:
        user (об'єкт): Користувач, для якого береться мова.
        message_type (str): Тип повідомлення (наприклад, welcome, settings_updated).

    Returns:
        str: Відповідний текст повідомлення.
    """
    try:
        user_settings = UserSettings.objects.get(user=user)

        responses = {
            'en': {
                'welcome': "Welcome to the bot! How can I assist you?",
                'settings_updated': "Your settings have been updated.",
            },
            'uk': {
                'welcome': "Ласкаво просимо до бота! Чим я можу допомогти?",
                'settings_updated': "Ваші налаштування було оновлено.",
            },
        }

        return responses.get(user_settings.language, responses['en']).get(message_type, "Unknown message.")

    except UserSettings.DoesNotExist:
        logger.warning(f"No settings found for user {user}. Using default language.")
        responses = {
            'en': {
                'welcome': "Welcome to the bot! How can I assist you?",
                'settings_updated': "Your settings have been updated.",
            },
        }
        return responses['en'].get(message_type, "Unknown message.")
