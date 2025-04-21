from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .models import UserSettings
from telegram import Update
from telegram.ext import ContextTypes
from django.http import HttpResponse


def home(request):
    return HttpResponse("Welcome to my Telegram Bot!")


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обробляє команду /settings. Відправляє меню для змін налаштувань.
    """
    keyboard = [
        [InlineKeyboardButton("🔤 Language / Мова", callback_data='settings_language')],
        [InlineKeyboardButton("🎨 Theme / Тема", callback_data='settings_theme')],
        [InlineKeyboardButton("📲 Notifications / Сповіщення", callback_data='settings_notifications')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Виберіть налаштування:", reply_markup=reply_markup)


async def get_response_text(user, message_type):
    """
    Вертає текст повідомлення залежно від мови, обраної користувачем.
    """
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
