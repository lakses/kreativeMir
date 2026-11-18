from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from users.models import Like

class Work(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='works')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='works/images/%Y/%m/', blank=True, null=True)
    video = models.FileField(upload_to='works/videos/%Y/%m/', blank=True, null=True)
    audio = models.FileField(upload_to='works/audio/%Y/%m/', blank=True, null=True)
    
    thumbnail = models.ImageField(upload_to='works/thumbnails/%Y/%m/', blank=True, null=True, verbose_name="Обложка")

    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    # НОВОЕ ПОЛЕ: Обратная связь от модератора
    moderator_feedback = models.TextField(blank=True, null=True, verbose_name="Комментарий модератора")
    created_at = models.DateTimeField(auto_now_add=True)

    likes = GenericRelation(Like, related_query_name='work_likes')
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='collaborative_works', blank=True)
    
    def __str__(self):
        return self.title

# НОВАЯ МОДЕЛЬ: Комментарии
class Comment(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Комментарий от {self.author.username} к {self.work.title}'