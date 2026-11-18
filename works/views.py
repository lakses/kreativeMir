from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from .models import Work, Comment
from users.models import Like

@login_required
def upload_work(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        audio = request.FILES.get('audio')
        thumbnail = request.FILES.get('thumbnail') # <-- Ловим обложку

        if title and (image or video or audio):
            work = Work(
                author=request.user,
                title=title,
                description=description,
                status='pending'
            )
            
            if image:
                work.image = image
            elif video:
                work.video = video
                if thumbnail: work.thumbnail = thumbnail # <-- Сохраняем обложку для видео
            elif audio:
                work.audio = audio
                if thumbnail: work.thumbnail = thumbnail # <-- Сохраняем обложку для аудио
                
            work.save()
            return redirect('profile')
            
    return render(request, 'works/upload.html')

@login_required
def delete_work(request, pk):
    # Ищем работу. Важно: только автор может её удалить, и только если она отклонена
    work = get_object_or_404(Work, pk=pk, author=request.user, status='rejected')
    
    if request.method == 'POST':
        work.delete()
        
    return redirect('profile')

@login_required
def work_detail(request, pk):
    work = get_object_or_404(Work, pk=pk)
    
    # Логика лайков
    if request.method == 'POST' and 'like' in request.POST:
        ct = ContentType.objects.get_for_model(work)
        like, created = Like.objects.get_or_create(
            user=request.user, 
            content_type=ct, 
            object_id=work.id
        )
        if not created:
            like.delete() # Если лайк уже был, убираем его (дизлайк)
        return redirect('work_detail', pk=work.pk)

    # Логика комментариев
    if request.method == 'POST' and 'comment' in request.POST:
        text = request.POST.get('text')
        if text:
            Comment.objects.create(work=work, author=request.user, text=text)
        return redirect('work_detail', pk=work.pk)

    # Проверяем, лайкнул ли текущий юзер эту работу
    ct = ContentType.objects.get_for_model(work)
    is_liked = Like.objects.filter(user=request.user, content_type=ct, object_id=work.id).exists()

    context = {
        'work': work,
        'comments': work.comments.all().order_by('-created_at'),
        'is_liked': is_liked,
    }
    return render(request, 'works/work_detail.html', context)

@login_required
@login_required
def delete_work(request, pk):
    # Ищем работу по ID и проверяем, что она принадлежит текущему пользователю
    work = get_object_or_404(Work, pk=pk, author=request.user)
    
    if request.method == 'POST':
        work.delete()
        
    return redirect('profile')