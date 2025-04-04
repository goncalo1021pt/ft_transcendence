from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('home-view/', views.home_view, name='home-view'),
	# path('profile-view/', views.profile_view, name='profile-view'),
	path('pong-view/', views.pong_view, name='pong-view'),
	path('login-view/', views.login_view, name='login-view'),
	path('register-view/', views.register_view, name='register-view'),
	path('tournament-view/', views.tournament_view, name='tournament-view'),
	path('nav-menu/', views.nav_menu, name='nav-menu'),
	path('login-menu/', views.login_menu, name='login-menu'),
	path('two-factor-view/', views.twoFactor_view, name='twofactor-view'),
]


