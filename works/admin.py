from django.contrib import admin
from django.utils.html import format_html
from .models import Work, Comment

@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'author', 'media_type', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'author__username')
    
    readonly_fields = ('image_preview_detail', 'media_preview_detail')

    fieldsets = (
        ('Основная информация', {'fields': ('author', 'title', 'description')}),
        ('Медиафайлы', {'fields': ('image', 'video', 'audio', 'thumbnail')}),
        ('Предпросмотр', {'fields': ('image_preview_detail', 'media_preview_detail')}),
        ('Модерация', {'fields': ('status', 'moderator_feedback')}),
    )

    def image_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="height: 60px; width: 60px; border-radius: 4px; object-fit: cover;" />', obj.thumbnail.url)
        elif obj.image:
            return format_html('<img src="{}" style="height: 60px; width: 60px; border-radius: 4px; object-fit: cover;" />', obj.image.url)
        return "Нет обложки"
    image_preview.short_description = 'Обложка'

    def media_type(self, obj):
        if obj.image: return "🖼️ Картинка"
        if obj.video: return "🎬 Видео"
        if obj.audio: return "🎵 Аудио"
        return "Нет файла"
    media_type.short_description = 'Тип файла'

    def image_preview_detail(self, obj):
        url = None
        if obj.thumbnail:
            url = obj.thumbnail.url
        elif obj.image:
            url = obj.image.url
            
        if url:
            # Добавляем жесткие размеры width и height, чтобы браузер её точно отрисовал
            return format_html(
                '<div style="margin-bottom: 10px;">'
                '<img src="{}" style="width: 250px; height: auto; border-radius: 8px; border: 2px solid #ccc;" />'
                '</div>'
                '<a href="{}" target="_blank" style="font-weight: bold; color: #417690;">🔍 Открыть картинку в полном размере</a>',
                url, url
            )
        return "❌ Обложка/Картинка не загружена"
    image_preview_detail.short_description = 'Превью картинки'

    def media_preview_detail(self, obj):
        if obj.video:
            return format_html(
                '<video src="{}" controls style="max-width: 400px; max-height: 300px; border-radius: 8px;"></video>'
                '<br><a href="{}" target="_blank" style="font-weight: bold; color: #417690;">🔍 Открыть видео в новой вкладке</a>',
                obj.video.url, obj.video.url
            )
        elif obj.audio:
            return format_html(
                '<audio src="{}" controls style="width: 100%; max-width: 400px; margin-bottom: 10px;"></audio>'
                '<br><a href="{}" target="_blank" style="font-weight: bold; color: #417690;">🔍 Открыть аудио в новой вкладке</a>',
                obj.audio.url, obj.audio.url
            )
        return "❌ Видео или аудио не загружено"
    media_preview_detail.short_description = 'Плеер'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('work', 'author', 'text', 'created_at')