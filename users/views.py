from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, get_user_model
from django.utils import timezone
from datetime import timedelta
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import Q, Max
from .models import Chat, Message, QuizQuestion, QuizOption

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
def get_or_create_chat(user1, user2, is_collab=False):
    # Сортируем пользователей по ID, чтобы не было дублей чатов (А-Б и Б-А)
    if user1.id > user2.id:
        user1, user2 = user2, user1
    chat, created = Chat.objects.get_or_create(user1=user1, user2=user2)
    if is_collab and not chat.is_collaboration:
        chat.is_collaboration = True
        chat.save()
    return chat

# --- ЧАТЫ ---
@login_required
def chat_list_view(request):
    chats = Chat.objects.filter(Q(user1=request.user) | Q(user2=request.user)).annotate(
        last_msg_time=Max('messages__timestamp')
    ).order_by('-last_msg_time')
    
    chat_data = []
    for chat in chats:
        other_user = chat.user2 if chat.user1 == request.user else chat.user1
        last_msg = chat.messages.order_by('-timestamp').first()
        unread_count = chat.messages.filter(is_read=False).exclude(sender=request.user).count()
        chat_data.append({
            'chat': chat,
            'other_user': other_user,
            'last_msg': last_msg,
            'unread_count': unread_count
        })
    
    return render(request, 'users/chat_list.html', {'chat_data': chat_data})

@login_required
def chat_detail_view(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in [chat.user1, chat.user2]:
        return redirect('profile')
    
    chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Message.objects.create(chat=chat, sender=request.user, text=text)
        return redirect('chat_detail', chat_id=chat.id)
        
    messages = chat.messages.order_by('timestamp')
    other_user = chat.user2 if chat.user1 == request.user else chat.user1
    
    return render(request, 'users/chat_detail.html', {
        'chat': chat,
        'messages': messages,
        'other_user': other_user
    })

@login_required
def start_chat_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        return redirect('profile')
    
    is_collab = request.GET.get('collab') == 'true'
    chat = get_or_create_chat(request.user, target_user, is_collab=is_collab)
    return redirect('chat_detail', chat_id=chat.id)

@login_required
def get_new_messages_api(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in [chat.user1, chat.user2]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    chat.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    messages = chat.messages.order_by('timestamp')
    
    msg_list = []
    for msg in messages:
        # Берем аватарку напрямую из User
        avatar_url = ''
        if msg.sender.avatar:
            avatar_url = msg.sender.avatar.url
            
        msg_list.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'sender_name': msg.sender.username,
            'avatar_url': avatar_url,
            'is_mine': msg.sender == request.user,
            'text': msg.text,
            'timestamp': msg.timestamp.strftime('%H:%M')
        })
        
    return JsonResponse({'messages': msg_list})

# --- КВИЗ ---
@login_required
def quiz_view(request, user_id):
    author = get_object_or_404(User, id=user_id)
    questions = author.quiz_questions.prefetch_related('options')
    
    # Если у автора нет вопросов, сразу кидаем в чат
    if not questions.exists():
        return redirect('start_chat', user_id=author.id)
        
    if request.method == 'POST':
        is_correct_all = True
        for q in questions:
            answer_id = request.POST.get(f'question_{q.id}')
            if not answer_id:
                is_correct_all = False
                break
            option = q.options.filter(id=answer_id).first()
            if not option or not option.is_correct:
                is_correct_all = False
                break
                
        if is_correct_all:
            # Если ответил правильно, кидаем в чат через имя маршрута
            return redirect('start_chat', user_id=author.id)
        else:
            return render(request, 'users/quiz_result.html', {'author': author})
            
    return render(request, 'users/quiz.html', {'author': author, 'questions': questions})

# --- УПРАВЛЕНИЕ КВИЗОМ (ДЛЯ КРЕАТОРА) ---
@login_required
def manage_quiz_view(request):
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        if question_text:
            q = QuizQuestion.objects.create(author=request.user, text=question_text)
            options = request.POST.getlist('option_text')
            correct_idx = request.POST.get('correct_option')
            for i, opt_text in enumerate(options):
                if opt_text:
                    QuizOption.objects.create(
                        question=q, 
                        text=opt_text, 
                        is_correct=(str(i) == correct_idx)
                    )
        return redirect('manage_quiz')
        
    questions = request.user.quiz_questions.prefetch_related('options')
    return render(request, 'users/manage_quiz.html', {'questions': questions})
