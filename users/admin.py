from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Like, FriendRequest, Message, Chat, QuizQuestion, QuizOption

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('avatar', 'bio', 'phone', 'contact_method', 'github_url', 'website_url', 'open_to_collaboration', 'available_for_orders', 'tags')}),
    )

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'is_collaboration', 'created_at')
    list_filter = ('is_collaboration',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    # ВОТ ЗДЕСЬ БЫЛА ОШИБКА. Заменили 'receiver' на 'get_receiver'
    list_display = ('sender', 'get_receiver', 'text', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')

    def get_receiver(self, obj):
        if not obj.chat:
            return "-"
        # Вычисляем получателя через объект чата
        return obj.chat.user2 if obj.chat.user1 == obj.sender else obj.chat.user1
    get_receiver.short_description = 'Получатель'

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'text')

@admin.register(QuizOption)
class QuizOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text', 'is_correct')
    list_filter = ('is_correct',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id')

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'created_at')