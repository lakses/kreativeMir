from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType

# Импортируем модели для подсчета лайков
from works.models import Work
from users.models import Like

from .forms import UserProfileForm, UserRegisterForm


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    # --- АВТОУДАЛЕНИЕ СТАРЫХ ОТКЛОНЕННЫХ РАБОТ ---
    seven_days_ago = timezone.now() - timedelta(days=7)
    request.user.works.filter(status='rejected', created_at__lt=seven_days_ago).delete()
    # ---------------------------------------------

    approved_works = request.user.works.filter(status='approved')
    pending_works = request.user.works.filter(status='pending')
    rejected_works = request.user.works.filter(status='rejected')

    # --- ПОДСЧЕТ ЛАЙКОВ СО ВСЕХ РАБОТ ---
    # Получаем тип контента для модели Work
    work_ct = ContentType.objects.get_for_model(Work)
    
    # Считаем лайки, которые привязаны к нашим одобренным работам
    total_likes = Like.objects.filter(
        content_type=work_ct,
        object_id__in=approved_works.values_list('id', flat=True)
    ).count()
    # ------------------------------------

    context = {
        'form': form,
        'approved_works': approved_works,
        'pending_works': pending_works,
        'rejected_works': rejected_works,
        'profile_likes_count': total_likes, # Передаем сумму лайков работ
    }
    return render(request, 'users/profile.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')
    else:
        form = UserRegisterForm()
        
    return render(request, 'registration/register.html', {'form': form})
