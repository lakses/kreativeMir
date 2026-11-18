from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType

from works.models import Work
from users.models import Like

from .forms import UserProfileForm, UserRegisterForm

User = get_user_model()


@login_required
def profile_view(request, username=None):
    # Кого показываем
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user

    is_own_profile = (profile_user.pk == request.user.pk)

    # Форма редактирования — только для своего профиля
    form = None
    if is_own_profile:
        if request.method == 'POST':
            form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('profile')
        else:
            form = UserProfileForm(instance=request.user)

    # Автоудаление отклонённых — только для своего
    if is_own_profile:
        seven_days_ago = timezone.now() - timedelta(days=7)
        request.user.works.filter(status='rejected', created_at__lt=seven_days_ago).delete()

    approved_works = profile_user.works.filter(status='approved').order_by('-is_pinned', '-created_at')

    if is_own_profile:
        pending_works = profile_user.works.filter(status='pending')
        rejected_works = profile_user.works.filter(status='rejected')
    else:
        # Пустые queryset'ы — чтобы шаблон не падал на .count
        pending_works = profile_user.works.none()
        rejected_works = profile_user.works.none()

    # Лайки со всех одобренных работ
    work_ct = ContentType.objects.get_for_model(Work)
    total_likes = Like.objects.filter(
        content_type=work_ct,
        object_id__in=approved_works.values_list('id', flat=True),
    ).count()

    context = {
        'user': profile_user,           # переопределяем переменную user в шаблоне
        'form': form,
        'is_own_profile': is_own_profile,
        'approved_works': approved_works,
        'pending_works': pending_works,
        'rejected_works': rejected_works,
        'profile_likes_count': total_likes,
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