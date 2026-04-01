from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import SignInForm
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('history/', views.history, name='history'),
    path('meals/<int:pk>/edit/', views.meal_edit, name='meal_edit'),
    path('meals/<int:pk>/delete/', views.meal_delete, name='meal_delete'),
    path('accounts/signup/', views.signup_view, name='signup'),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True,
            authentication_form=SignInForm,
        ),
        name='login',
    ),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/weekly-stats/', views.weekly_stats_api, name='weekly_stats_api'),
]
