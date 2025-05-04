from .models import UserSettings
from telegram import Update
from telegram.ext import ContextTypes
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import os
import logging

logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")

@csrf_exempt
async def telegram_webhook(request):
    """ Django-based обробник webhook для Telegram."""
    if request.method == "POST":
        try:
            from .bot_handler import application
            body = request.body.decode('utf-8')
            logger.info(f"Received Telegram Webhook: {body}")

            update = Update.de_json(json.loads(body), application.bot)
            await application.process_update(update)

            return JsonResponse({"ok": True})

        except Exception as e:
            logger.error(f"Error while handling Telegram webhook: {e}")
            return JsonResponse({"ok": False, "error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

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
