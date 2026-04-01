from django.contrib import admin

from .models import DailyTarget, MealEntry


@admin.register(DailyTarget)
class DailyTargetAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_target', 'updated_at')
    search_fields = ('user__username', 'user__email')


@admin.register(MealEntry)
class MealEntryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'meal_type', 'calories', 'quantity', 'unit', 'consumed_at')
    list_filter = ('meal_type', 'consumed_at')
    search_fields = ('name', 'notes', 'user__username')
