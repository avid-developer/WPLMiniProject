from datetime import datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncDate, TruncWeek
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DailyTargetForm, HistoryFilterForm, MealEntryForm, SignUpForm
from .models import DailyTarget, MealEntry


QUICK_PRESETS = [
    {'label': 'Oats Bowl', 'meal_type': MealEntry.MealType.BREAKFAST, 'quantity': '1', 'unit': 'bowl', 'calories': '320'},
    {'label': 'Veg Thali', 'meal_type': MealEntry.MealType.LUNCH, 'quantity': '1', 'unit': 'plate', 'calories': '640'},
    {'label': 'Fruit Snack', 'meal_type': MealEntry.MealType.SNACK, 'quantity': '1', 'unit': 'cup', 'calories': '180'},
    {'label': 'Protein Shake', 'meal_type': MealEntry.MealType.DRINK, 'quantity': '1', 'unit': 'glass', 'calories': '220'},
]


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tracker/landing.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        DailyTarget.objects.get_or_create(user=user)
        login(request, user)
        messages.success(request, 'Your account is ready. Start logging your meals.')
        return redirect('dashboard')

    return render(request, 'registration/signup.html', {'form': form})


def get_or_create_target(user):
    return DailyTarget.objects.get_or_create(user=user, defaults={'daily_target': 2200})[0]


def get_day_bounds(current_date):
    current_timezone = timezone.get_current_timezone()
    start_of_day = timezone.make_aware(datetime.combine(current_date, time.min), current_timezone)
    end_of_day = timezone.make_aware(datetime.combine(current_date, time.max), current_timezone)
    return start_of_day, end_of_day


def build_weekly_stats(user):
    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=6)
    daily_totals = (
        MealEntry.objects.filter(user=user, consumed_at__date__range=(start_date, end_date))
        .annotate(day=TruncDate('consumed_at'))
        .values('day')
        .annotate(total=Sum('calories'))
        .order_by('day')
    )

    totals_by_day = {item['day']: item['total'] for item in daily_totals}
    labels = []
    totals = []

    for index in range(7):
        day = start_date + timedelta(days=index)
        labels.append(day.strftime('%d %b'))
        totals.append(int(totals_by_day.get(day, 0) or 0))

    return labels, totals


@login_required
def dashboard(request):
    target = get_or_create_target(request.user)
    meal_form = MealEntryForm(prefix='meal')
    goal_form = DailyTargetForm(prefix='goal', instance=target)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_meal':
            meal_form = MealEntryForm(request.POST, prefix='meal')
            if meal_form.is_valid():
                meal = meal_form.save(commit=False)
                meal.user = request.user
                meal.save()
                messages.success(request, 'Meal added successfully.')
                return redirect('dashboard')
        elif action == 'update_goal':
            goal_form = DailyTargetForm(request.POST, prefix='goal', instance=target)
            if goal_form.is_valid():
                goal_form.save()
                messages.success(request, 'Daily calorie target updated.')
                return redirect('dashboard')

    today = timezone.localdate()
    start_of_day, end_of_day = get_day_bounds(today)
    todays_meals = request.user.meal_entries.filter(consumed_at__range=(start_of_day, end_of_day))
    total_calories = todays_meals.aggregate(total=Sum('calories'))['total'] or 0
    remaining_calories = target.daily_target - total_calories
    progress_percent = int((total_calories / target.daily_target) * 100) if target.daily_target else 0
    labels, totals = build_weekly_stats(request.user)

    context = {
        'active_page': 'dashboard',
        'goal_form': goal_form,
        'meal_form': meal_form,
        'progress_percent': progress_percent,
        'progress_percent_capped': min(progress_percent, 100),
        'quick_presets': QUICK_PRESETS,
        'remaining_calories': abs(remaining_calories),
        'target': target,
        'today': today,
        'todays_meals': todays_meals,
        'total_calories': total_calories,
        'weekly_average': round(sum(totals) / len(totals), 1) if totals else 0,
        'weekly_total': sum(totals),
        'is_over_target': remaining_calories < 0,
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def history(request):
    meals = request.user.meal_entries.all()
    filter_form = HistoryFilterForm(request.GET or None)

    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')

        if start_date:
            meals = meals.filter(consumed_at__date__gte=start_date)
        if end_date:
            meals = meals.filter(consumed_at__date__lte=end_date)

    summary = meals.aggregate(
        total_calories=Sum('calories'),
        meal_count=Count('id'),
        average_calories=Avg('calories'),
    )
    weekly_summary = (
        meals.annotate(week=TruncWeek('consumed_at'))
        .values('week')
        .annotate(total=Sum('calories'), meals=Count('id'))
        .order_by('-week')[:6]
    )
    strongest_day = (
        meals.annotate(day=TruncDate('consumed_at'))
        .values('day')
        .annotate(total=Sum('calories'))
        .order_by('-total')
        .first()
    )

    formatted_weekly_summary = []
    for item in weekly_summary:
        week_value = item['week']
        week_start = week_value.date() if hasattr(week_value, 'date') else week_value
        formatted_weekly_summary.append(
            {
                'week_start': week_start,
                'total': item['total'],
                'meals': item['meals'],
            }
        )

    context = {
        'active_page': 'history',
        'filter_form': filter_form,
        'meals': meals,
        'summary': {
            'total_calories': int(summary['total_calories'] or 0),
            'meal_count': summary['meal_count'] or 0,
            'average_calories': round(summary['average_calories'] or 0, 1),
        },
        'strongest_day': strongest_day,
        'weekly_summary': formatted_weekly_summary,
    }
    return render(request, 'tracker/history.html', context)


@login_required
def meal_edit(request, pk):
    meal = get_object_or_404(MealEntry, pk=pk, user=request.user)
    form = MealEntryForm(request.POST or None, instance=meal)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Meal updated.')
        return redirect('history')

    return render(
        request,
        'tracker/meal_form.html',
        {
            'form': form,
            'meal': meal,
            'page_title': 'Edit meal',
            'page_description': 'Adjust quantity, calories, or timing for this entry.',
        },
    )


@login_required
def meal_delete(request, pk):
    meal = get_object_or_404(MealEntry, pk=pk, user=request.user)

    if request.method == 'POST':
        meal.delete()
        messages.success(request, 'Meal deleted.')
        return redirect('history')

    return render(request, 'tracker/meal_confirm_delete.html', {'meal': meal})


@login_required
def weekly_stats_api(request):
    labels, totals = build_weekly_stats(request.user)
    target = get_or_create_target(request.user)

    return JsonResponse(
        {
            'labels': labels,
            'totals': totals,
            'target': target.daily_target,
        }
    )
