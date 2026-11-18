import random

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.shortcuts import render

from users.models import Tag
from works.models import Work

User = get_user_model()

PER_PAGE = 10


def creators_list_view(request):
    # Базовый queryset: только «могу брать заказы», без суперюзеров и себя
    qs = User.objects.filter(
        is_superuser=False,
        available_for_orders=True,
    )
    if request.user.is_authenticated:
        qs = qs.exclude(pk=request.user.pk)

    # Поиск по юзернейму
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(username__icontains=q)

    # Чекбокс «готов к сотрудничеству»
    collab_checked = request.GET.get('collab') == 'on'
    if collab_checked:
        qs = qs.filter(open_to_collaboration=True)

    # Фильтр по тегам
    tag_ids_str = request.GET.getlist('tags')
    selected_tag_ids = [int(x) for x in tag_ids_str if x.isdigit()]
    if selected_tag_ids:
        qs = qs.filter(tags__id__in=selected_tag_ids).distinct()

    # Аннотации: количество одобренных работ + общее число лайков
    qs = qs.annotate(
        approved_works_count=Count(
            'works',
            filter=Q(works__status='approved'),
            distinct=True,
        ),
        total_likes=Count(
            'works__likes',
            filter=Q(works__status='approved'),
            distinct=True,
        ),
    )

    # Prefetch закреплённых работ
    pinned_works_qs = (
        Work.objects
        .filter(status='approved', is_pinned=True)
        .order_by('-created_at')
    )
    qs = qs.prefetch_related(
        'tags',
        Prefetch('works', queryset=pinned_works_qs, to_attr='pinned_works_list'),
    )

    # Сортировка
    sort = request.GET.get('sort', 'random')
    try:
        page_num = max(1, int(request.GET.get('page', 1)))
    except (TypeError, ValueError):
        page_num = 1

    if sort == 'new':
        qs = qs.order_by('-date_joined')
        page_obj = Paginator(qs, PER_PAGE).get_page(page_num)
        creators = list(page_obj.object_list)
    elif sort == 'popular':
        qs = qs.order_by('-total_likes', '-approved_works_count', '-date_joined')
        page_obj = Paginator(qs, PER_PAGE).get_page(page_num)
        creators = list(page_obj.object_list)
    elif sort == 'active':
        qs = qs.order_by('-approved_works_count', '-total_likes', '-date_joined')
        page_obj = Paginator(qs, PER_PAGE).get_page(page_num)
        creators = list(page_obj.object_list)
    else:
        # Случайный порядок с seed в сессии
        seed = request.session.get('creators_seed')
        if not seed:
            seed = random.randint(1, 10 ** 9)
            request.session['creators_seed'] = seed

        all_ids = list(qs.values_list('id', flat=True))
        random.Random(seed).shuffle(all_ids)

        total = len(all_ids)
        start = (page_num - 1) * PER_PAGE
        end = start + PER_PAGE
        page_ids = all_ids[start:end]

        if page_ids:
            fetched = list(qs.filter(pk__in=page_ids))
            by_id = {u.pk: u for u in fetched}
            creators = [by_id[pk] for pk in page_ids if pk in by_id]
        else:
            creators = []

        page_obj = _make_page(creators, page_num, total)

    # Для сохранения фильтров в пагинации
    params = request.GET.copy()
    params.pop('page', None)
    filter_query = params.urlencode()

    return render(request, 'creators/creators_list.html', {
        'creators': creators,
        'page_obj': page_obj,
        'all_tags': Tag.objects.all().order_by('name'),
        'q': q,
        'selected_tag_ids': selected_tag_ids,
        'selected_sort': sort,
        'collab_checked': collab_checked,
        'filter_query': filter_query,
    })


class _FakePaginator:
    def __init__(self, count, per_page):
        self.count = count
        self.per_page = per_page
        self.num_pages = max(1, (count + per_page - 1) // per_page)
        self.page_range = range(1, self.num_pages + 1)


class _FakePage:
    def __init__(self, object_list, number, total, per_page):
        self.object_list = object_list
        self.number = number
        self.paginator = _FakePaginator(total, per_page)

    def has_previous(self):
        return self.number > 1

    def has_next(self):
        return self.number < self.paginator.num_pages

    def has_other_pages(self):
        return self.paginator.num_pages > 1

    def previous_page_number(self):
        return self.number - 1

    def next_page_number(self):
        return self.number + 1


def _make_page(object_list, number, total):
    return _FakePage(object_list, number, total, PER_PAGE)