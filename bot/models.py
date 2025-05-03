from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ExampleModel(models.Model):
    """ Модель для прикладу. Може використовуватись для збереження шаблонів або текстів команд."""
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class BotLog(models.Model):
    """ Журнал команд бота."""
    command = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logs")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.command} - {self.user}"


class TelegramUser(models.Model):
    """ Зберігає дані користувачів Telegram."""
    chat_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username or f"Chat ID: {self.chat_id}"


class RequestLog(models.Model):
    """ Логування запитів до бота."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    command = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.command} ({self.user.username})"


class UserSettings(models.Model):
    """ Налаштування користувача."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    language = models.CharField(max_length=10, default='en')
    theme = models.CharField(max_length=20, default='classical')
    notifications_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Settings for {self.user}"



