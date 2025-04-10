from django.urls import path
from . import views
from . import frequests

urlpatterns = [
	path('profile-view/<str:username>/', views.profile_view, name='profile-view'),
	path('profile-view/', views.profile_view, name='profile-view-self'),
	path('profile/update/', views.update_profile, name='profile-update'),

    path('friends/send-request/', frequests.send_friend_request, name='send_friend_request'),
    path('friends/cancel-request/', frequests.cancel_friend_request, name='cancel_friend_request'),
    path('friends/accept-request/', frequests.accept_friend_request, name='accept_friend_request'),
    path('friends/reject-request/', frequests.reject_friend_request, name='reject_friend_request'),
    path('friends/remove-friend/', frequests.remove_friend, name='remove_friend'),

	path('friends/find-user/', views.find_user, name='find_user'),
]
