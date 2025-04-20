from django.db import models


class BotLog(models.Model):
    command = models.CharField(max_length=100)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="logs")
    timestamp = models.DateTimeField(auto_now_add=True)

class User(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class RequestLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    command = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.command} by {self.user.first_name}'