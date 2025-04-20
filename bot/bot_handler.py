from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
import requests
from decouple import config
from googletrans import Translator
import openai
import asyncio
import random

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        delay = int(context.args[0])
        message = " ".join(context.args[1:])
        await update.message.reply_text(f"Нагадування через {delay} секунд: {message}")
        await asyncio.sleep(delay)
        await update.message.reply_text(f"НАГАДУЮ: {message}")
    except (IndexError, ValueError):
        await update.message.reply_text("Використання: /remind <час_у_секундуах> <повідомлення>")



TOKEN = config('TELEGRAM_TOKEN')
WEATHER_API_KEY = config('WEATHER_API_KEY')
NEWS_API_KEY = config('NEWS_API_KEY')
openai.api_key = config('OPENAI_API_KEY')

translator = Translator()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Привіт, {update.effective_user.first_name}! Я твій Telegram-бот.')


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = ' '.join(context.args)
    if not city:
        await update.message.reply_text('Введіть місто, щоб я міг надати прогноз погоди: /weather Київ')
        return

    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric'
    response = requests.get(url).json()
    if response.get('main'):
        temp = response['main']['temp']
        description = response['weather'][0]['description']
        await update.message.reply_text(f'Погода у {city}: {temp}°С, {description}.')
    else:
        await update.message.reply_text('Не вдалося знайти місто.')


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f'https://newsapi.org/v2/top-headlines?country=ua&apiKey={NEWS_API_KEY}'
    response = requests.get(url).json()
    if response['status'] == 'ok':
        articles = response['articles'][:3]  # Топ-3 новини
        news_msg = '\n\n'.join([f"{article['title']} - {article['url']}" for article in articles])
        await update.message.reply_text(news_msg)
    else:
        await update.message.reply_text('Не вдалося отримати новини.')


def translate(update, context):
    try:
        text = " ".join(context.args)
        translated = translator.translate(text, dest="en")
        context.bot.send_message(chat_id=update.effective_chat.id, text=translated.text)
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")




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
        message = "\n".join([f"{currency}: {rate}" for currency, rate in rates.items()])
        await update.message.reply_text(f"Курс валют ({base_currency}):\n{message}")
    else:
        await update.message.reply_text("Не вдалося отримати курс валют.")


async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.quotable.io/random"
    response = requests.get(url).json()
    if "content" in response:
        await update.message.reply_text(f'"{response["content"]}" - {response["author"]}')
    else:
        await update.message.reply_text("Не вдалося отримати цитату.")


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
    file = await update.message.document.get_file()
    file_content = await file.download_as_bytearray()  # Завантажуємо файл
    text = file_content.decode("utf-8")  # Розпізнаємо текст
    word_count = len(text.split())
    await update.message.reply_text(f"У вашому файлі {word_count} слів.")



def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('translate', translate))
    app.add_handler(CommandHandler('weather', weather))
    app.add_handler(CommandHandler('news', news))
    app.add_handler(CommandHandler('chat', chatgpt))
    app.add_handler(CommandHandler('currency', currency))
    app.add_handler(CommandHandler('quote', quote))
    app.add_handler(CommandHandler('remind', remind))
    app.add_handler(CommandHandler('guess', guess_number))
    app.add_handler(CommandHandler('processfile', process_file))

    print('Бот запущений...')
    app.run_polling()