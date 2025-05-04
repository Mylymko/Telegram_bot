"""
WSGI config for my_telegram_bot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_telegram_bot.settings')

application = get_wsgi_application()

async def post_wsgi_initialization():
    from bot.bot_handler import initialize_application
    await initialize_application()

import asyncio

asyncio.run(post_wsgi_initialization())