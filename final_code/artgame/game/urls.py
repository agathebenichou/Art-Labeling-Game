# this is the game/urls.py

from django.contrib.auth import views as auth_views

from django.urls import path, include
from game import views

# Define application name
app_name = 'game'

# Define URL links such that path(link, associated views method, name)
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('initgame/', views.initgame, name='initgame'),
    path('game/', views.game, name='game'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
]
