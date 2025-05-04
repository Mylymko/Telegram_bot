from telegram import Update
from telegram.ext import (Application, CommandHandler,
                          ContextTypes, CallbackContext, MessageHandler, filters)
import requests
from libretranslatepy import LibreTranslateAPI
import openai
import asyncio
import random
from .models import BotLog
import os
from bs4 import BeautifulSoup
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TOKEN = os.environ.get('TELEGRAM_TOKEN')
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
openai.api_key = os.environ.get('OPENAI_API_KEY')

application = Application.builder().token(TOKEN).build()

translator = LibreTranslateAPI("https://libretranslate.com")


def run_webhook():
    """Функція для запуску Telegram-бота через вебхук."""
    PORT = int(os.environ.get("PORT", 8443))
    WEBHOOK_URL = f"https://myalhelperbot-8b53fda80b6e.herokuapp.com/webhook/"
    async def start(update, context):
        await update.message.reply_text("Телеграм-бот запущено через вебхук!")

    application.add_handler(CommandHandler('start', start))

    logger.info("Запуск Telegram-бота через вебхук...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook/",
        webhook_url=WEBHOOK_URL
    )


def log_bot_command(user: str, command: str):
    """ Логує виконану команду в базу даних.
    Args:
        user (str): Ідентифікатор користувача.
        command (str): Назва команди."""
    BotLog.objects.create(user=user, command=command)



async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        delay = int(context.args[0])
        message = " ".join(context.args[1:])
        await update.message.reply_text(f"Нагадування через {delay} секунд: {message}")
        await asyncio.sleep(delay)
        await update.message.reply_text(f"НАГАДУЮ: {message}")
    except (IndexError, ValueError):
        await update.message.reply_text("Використання: /remind <час_у_секундуах> <повідомлення>")


async def start(update: Update, context: CallbackContext):
    """
    Команда /start
    """
    await update.message.reply_text("Привіт! Я твій бот. Як я можу допомогти?")


async def help_command(update: Update, context: CallbackContext):
    """
    Команда /help
    """
    help_text = "\n".join([f"{cmd}: {desc}" for cmd, desc in {
        '/start': 'Почати роботу з ботом',
        '/translate': 'Перекласти текст',
        '/weather': 'Дізнатися прогноз погоди',
        '/news': 'Останні новини',
        '/chat': 'Поговорити з ChatGPT',
        '/currency': 'Отримати курс валют',
        '/quote': 'Отримати випадкову цитату',
        '/remind': 'Створити нагадування',
        '/guess': 'Гра "Вгадай число"',
        '/processfile': 'Обробити файл (наприклад, аналіз)',
        '/settings': 'Налаштувати параметри',
    }.items()])
    await update.message.reply_text(help_text)


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _log_bot_command(update, context)
    city = ' '.join(context.args)
    if not city:
        await update.message.reply_text('Введіть місто: /weather Київ')
        return

    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric'
    try:
        response = await asyncio.to_thread(requests.get, url)
        data = response.json()
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        await update.message.reply_text(f"У {city}: {temp}°C, {description}")
    except Exception as e:
        await update.message.reply_text(f"Не вдалося отримати прогноз: {e}")


async def _fetch_bbc_news():
    url = "https://www.bbc.com/ukrainian"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8"
    }
    try:
        response = await asyncio.to_thread(requests.get, url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        news_items = soup.find_all("a", class_="ssrcss-11uk9hy-PromoLink e1f5wbog0", limit=5)

        if not news_items:
            return "Новини не знайдені. Можливо, структура сайту змінилася."

        return "\n\n".join([f"{item.text.strip()} - https://www.bbc.com{item['href']}" for item in news_items])
    except Exception as e:
        logger.error(f"Помилка отримання новин: {e}")
        return "Сталася помилка під час отримання новин."


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _log_bot_command(update, context)
    news = await _fetch_bbc_news()
    await update.message.reply_text(news)


def translate_text(text, target_language):
    try:
        result = translator.translate(text, target=target_language)
        return result
    except Exception as e:
        return f"Помилка перекладу: {e}"


async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Використання: /translate <цільова_мова> <текст>")
        return

    target_language = context.args[0]
    text_to_translate = " ".join(context.args[1:])
    translated_text = translate_text(text_to_translate, target_language)
    await update.message.reply_text(f"Переклад: {translated_text}")


async def chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = " ".join(context.args)
    if not user_message:
        await update.message.reply_text("Введіть текст для спілкування зі ШІ.")
        return

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ти помічник."},
            {"role": "user", "content": user_message}
        ]
    )
    bot_response = response['choices'][0]['message']['content']
    await update.message.reply_text(bot_response)


async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    base_currency = context.args[0] if len(context.args) > 0 else "USD"
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"

    response = requests.get(url).json()
    if "rates" in response:
        rates = response["rates"]
        message = "\n".join([f"{currency_code}: {rate}" for currency_code, rate in rates.items()])
        await update.message.reply_text(f"Курс валют ({base_currency}):\n{message}")
    else:
        await update.message.reply_text("Не вдалося отримати курс валют.")


async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()[0]
            quote_text = data['q']
            author = data['a']
            await update.message.reply_text(f'“{quote_text}” — {author}')
        else:
            await update.message.reply_text("Сервер цитат тимчасово недоступний. Спробуйте пізніше.")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Сталася помилка під час підключення до цитат API: {e}")



async def guess_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "game_number" not in context.user_data:
        context.user_data["game_number"] = random.randint(1, 100)
        await update.message.reply_text("Я задумав число від 1 до 100. Спробуй відгадати!")
    else:
        try:
            user_guess = int(context.args[0])
            number = context.user_data["game_number"]
            if user_guess < number:
                await update.message.reply_text("Занадто мало!")
            elif user_guess > number:
                await update.message.reply_text("Занадто багато!")
            else:
                await update.message.reply_text("Вітаю, ти вгадав!")
                del context.user_data["game_number"]
        except (IndexError, ValueError):
            await update.message.reply_text("Введи число для спроби!")


async def process_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("Будь ласка, надішліть файл для обробки.")
        return

    file = await update.message.document.get_file()
    file_content = await file.download_as_bytearray()
    text = file_content.decode("utf-8")
    word_count = len(text.split())
    await update.message.reply_text(f"У вашому файлі {word_count} слів.")

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔤 Мова", callback_data='settings_language')],
        [InlineKeyboardButton("🎨 Тема", callback_data='settings_theme')],
    ]
    await update.message.reply_text("Виберіть налаштування:", reply_markup=InlineKeyboardMarkup(keyboard))


async def _log_bot_command(update: Update, context: CallbackContext):
    """
    Логування виконаної команди в базу даних.

    Args:
        update (Update): Телеграм-об'єкт оновлення з інформацією про команду.
        context (CallbackContext): Контекст команди.
    """
    try:
        user_id = update.effective_user.id
        command_text = update.message.text

        BotLog.objects.create(user=user_id, command=command_text)
        logger.info(f"Command logged: user={user_id}, command={command_text}")
    except Exception as e:
        logger.error(f"Error while logging command: {e}")


def add_handlers():
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('translate', translate_command))
    application.add_handler(CommandHandler('weather', weather))
    application.add_handler(CommandHandler('news', news_command))
    application.add_handler(CommandHandler('chat', chatgpt))
    application.add_handler(CommandHandler('currency', currency))
    application.add_handler(CommandHandler('quote', quote))
    application.add_handler(CommandHandler('remind', remind))
    application.add_handler(CommandHandler('guess', guess_number))
    application.add_handler(CommandHandler('processfile', process_file))
    application.add_handler(CommandHandler('settings', settings))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _log_bot_command))

def run_bot():
    logger.info("Запуск Telegram бота...")
    add_handlers()
    application.run_polling()

