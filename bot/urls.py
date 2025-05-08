from django.urls import path
from . import views
from bot.bot_handler import telegram_webhook
urlpatterns = [
    path('', views.bot_home, name='home'),
    path('webhook/', telegram_webhook, name='telegram_webhook'),
]