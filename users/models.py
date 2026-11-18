from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models


class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True)
    contact_count = models.PositiveIntegerField(default=0)

    # Друзья (симметричная связь)
    friends = models.ManyToManyField('self', blank=True)

    # Лайки, поставленные ЭТОМУ пользователю (на его профиль)
    profile_likes = GenericRelation(
        'Like',
        related_query_name='user_profile',
    )
    bio = models.TextField(blank=True, verbose_name="О себе")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    contact_method = models.CharField(max_length=100, blank=True, verbose_name="Способ связи (Telegram, Discord и т.д.)")
    github_url = models.URLField(blank=True, verbose_name="GitHub")
    website_url = models.URLField(blank=True, verbose_name="Личный сайт / Портфолио")
    open_to_collaboration = models.BooleanField(default=False, verbose_name="Готов к сотрудничеству")
    available_for_orders = models.BooleanField(default=False, verbose_name="Могу брать заказы")
    def __str__(self):
        return self.username


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_likes',
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        return f'{self.user} → {self.content_object}'


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_requests',
        on_delete=models.CASCADE,
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_requests',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.from_user} → {self.to_user}'


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_messages',
        on_delete=models.CASCADE,
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_messages',
        on_delete=models.CASCADE,
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} → {self.receiver}: {self.text[:30]}'