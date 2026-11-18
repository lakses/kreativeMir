from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView  # <-- добавили импорт

urlpatterns = [
    # Редирект с главной страницы (/) сразу в профиль
    path('', RedirectView.as_view(url='/users/profile/', permanent=False)),
    
    path('admin/', admin.site.urls),
    
    # Встроенные страницы входа и выхода Django
    path('accounts/', include('django.contrib.auth.urls')), 
    
    path('users/', include('users.urls')),
    path('works/', include('works.urls')),
]

# Раздача медиафайлов (аватарки, работы) в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)