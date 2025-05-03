from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserSettings, BotLog, TelegramUser, RequestLog

admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["id", "username", "first_name", "last_name"]


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ["user", "language", "theme", "notifications_enabled"]
    search_fields = ('user__first_name', 'user__last_name')


@admin.register(BotLog)
class BotLogAdmin(admin.ModelAdmin):
    list_display = ["user", "command", "timestamp"]
    list_filter = ("command", "timestamp")
    search_fields = ("user__username", "command")


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ["chat_id", "username", "first_name", "last_name"]
    search_fields = ("username", "first_name", "last_name")
    list_filter = ("username",)


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ["user", "command", "created_at"]
    search_fields = ("user__username", "command")
    list_filter = ("created_at",)
