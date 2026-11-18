from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Like, FriendRequest, Message


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Добавляем поле avatar в форму редактирования
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('avatar', 'contact_count', 'friends')}),
    )


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id')


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'text', 'timestamp', 'is_read')