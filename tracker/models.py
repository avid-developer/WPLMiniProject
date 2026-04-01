from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class DailyTarget(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_target_profile',
    )
    daily_target = models.PositiveIntegerField(default=2200, validators=[MinValueValidator(1200)])
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f'{self.user.username} target: {self.daily_target} kcal'


class MealEntry(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = 'breakfast', 'Breakfast'
        LUNCH = 'lunch', 'Lunch'
        DINNER = 'dinner', 'Dinner'
        SNACK = 'snack', 'Snack'
        DRINK = 'drink', 'Drink'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='meal_entries',
    )
    name = models.CharField(max_length=120)
    meal_type = models.CharField(max_length=20, choices=MealType.choices, default=MealType.SNACK)
    quantity = models.DecimalField(max_digits=5, decimal_places=2, default=1, validators=[MinValueValidator(0.25)])
    unit = models.CharField(max_length=30, default='serving')
    calories = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    consumed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-consumed_at', '-created_at']

    def __str__(self):
        return f'{self.name} ({self.calories} kcal)'
