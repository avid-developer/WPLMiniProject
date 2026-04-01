from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import DailyTarget, MealEntry


class TrackerViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dhruv', password='securepass123')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_signup_creates_target_profile(self):
        response = self.client.post(
            reverse('signup'),
            {
                'first_name': 'Dhruv',
                'username': 'newuser',
                'email': 'dhruv@example.com',
                'password1': 'StrongerPass456',
                'password2': 'StrongerPass456',
            },
        )

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(DailyTarget.objects.filter(user__username='newuser').exists())

    def test_dashboard_can_add_meal(self):
        self.client.login(username='dhruv', password='securepass123')

        response = self.client.post(
            reverse('dashboard'),
            {
                'action': 'add_meal',
                'meal-name': 'Paneer Wrap',
                'meal-meal_type': 'lunch',
                'meal-quantity': '1',
                'meal-unit': 'wrap',
                'meal-calories': '520',
                'meal-consumed_at': timezone.localtime().strftime('%Y-%m-%dT%H:%M'),
                'meal-notes': 'Post-lab lunch',
            },
        )

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(MealEntry.objects.filter(user=self.user, name='Paneer Wrap').exists())

    def test_weekly_stats_api_returns_json(self):
        MealEntry.objects.create(
            user=self.user,
            name='Smoothie',
            meal_type='drink',
            quantity='1',
            unit='glass',
            calories=240,
        )
        self.client.login(username='dhruv', password='securepass123')

        response = self.client.get(reverse('weekly_stats_api'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload['labels']), 7)
        self.assertEqual(len(payload['totals']), 7)
