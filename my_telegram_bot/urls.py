"""
URL configuration for my_telegram_bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.http import HttpResponse
from django.urls import path, include
from bot.views import telegram_webhook, bot_home
from django.contrib import admin


def home(request):
    return HttpResponse("Hello, this is the homepage for the Telegram bot!")

urlpatterns = [
    path("", bot_home, name="home"),
    path('admin/', admin.site.urls),

    path('bot/', include('bot.urls')),
    path("webhook/", telegram_webhook, name="telegram_webhook"),
]

