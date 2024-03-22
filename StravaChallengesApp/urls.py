# strava_integration/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('login/', views.login, name='login'),
    path('auth/callback/', views.auth_callback, name='auth_callback'),
    path('get_stats/', views.get_stats, name='get_stats'),
    path('main_page/', views.main_page, name='main_page'),
    path('confirmation_page/', views.confirmation_page, name='confirmation_page'),
    path('y5k_results_page/', views.y5k_results_page, name='y5k_results_page'),
    path('get_athlete_and_stats', views.get_athlete_and_stats, name='get_athlete_and_stats'),
    
]
