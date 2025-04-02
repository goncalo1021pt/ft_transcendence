from django.urls import path
from . import views

urlpatterns = [
	path('register/', views.register_request, name='register'),
	path('login/', views.login_request, name='login'),
	path('logout/', views.logout_request, name='logout'),
	path('check-auth/', views.check_auth, name='check-auth'),
    path('oauth/callback/', views.oauth_callback, name='oauth-callback'),
	path('get-host/', views.get_host, name='get-host'),
	path('update-2fa/', views.update_2fa, name='update_2fa'),
	path('change-password/', views.change_password, name='change-password'),
	path('twoFactor/', views.twoFactor, name='twoFactor'),

]
