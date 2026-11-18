from .models import Message

def unread_messages(request):
    if request.user.is_authenticated:
        # Считаем все непрочитанные сообщения, где пользователь не отправитель
        count = Message.objects.filter(
            chat__in=request.user.chats_as_user1.all() | request.user.chats_as_user2.all(),
            is_read=False
        ).exclude(sender=request.user).count()
        return {'unread_messages_count': count}
    return {'unread_messages_count': 0}