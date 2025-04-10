from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from backend.models import User
from pong.models import OngoingGame
from tournaments.models import Tournament
from backend.signals import profile_updated_signal
from .models import (
    get_user, user_about, user_status, user_stats, user_matches, 
	format_matches, user_friends, user_pending_sent, 
	user_pending_received, friendship_status
)
import os, json, logging


logger = logging.getLogger('pong')

@require_http_methods(["GET"])
def profile_view(request, username=None):
	if not request.user.is_authenticated:
		return HttpResponseForbidden('Not authenticated')

	if username is None or not get_user(username):
		target_user = request.user
		is_own_profile = True
		username = request.user.username
	else:
		target_user = get_user(username)
		is_own_profile = (request.user.username == username)

	matches_data = user_matches(username)
	formatted_matches = format_matches(matches_data)

	context = {
		'user': target_user,
		'own_profile': is_own_profile,
		'rank': target_user.rank,
		'status': user_status(target_user),
		'about': user_about(target_user),
		'stats': user_stats(username),
		'matches': formatted_matches,
		'friends': {
			'friendship_status': friendship_status(request.user, target_user),
			'list': user_friends(target_user),
			'pending_sent': user_pending_sent(target_user),
			'pending_received': user_pending_received(target_user)
		},
		'profile_pic': target_user.profile_pic
	}

	if is_own_profile:
		context['account'] = {
			'username': target_user.username,
			'email': target_user.email,
			'profile_pictures': pic_selection(), # should be settings.PPIC_SELECTION
		}
	return render(request, 'views/profile-view.html', context)

def pic_selection(): # should be the value in settings.PPIC_SELECTION
	profile_pics_dir = os.path.join(settings.MEDIA_ROOT, 'profile-pics')
	if os.path.exists(profile_pics_dir):
		return sorted(os.listdir(profile_pics_dir))

@login_required
@require_http_methods(["PUT"])
def update_profile(request):
	try:
		data = json.loads(request.body)
		user : User = request.user
		user_uuid = str(user.uuid)
		
		if OngoingGame.player_in_game(user_uuid):
			return JsonResponse({'error': 'Cannot update profile while in an active game'}, status=400)

		if Tournament.player_in_tournament(user_uuid):
			return JsonResponse({'error': 'Cannot update profile while in a tournament'}, status=400)
		
		if 'username' in data and data['username'] != user.username:
			if User.objects.filter(username=data['username']).exists():
				return JsonResponse({'error': 'Username already taken'}, status=400)
			user.username = data['username']

		if 'email' in data and data['email'] != user.email:
			if User.objects.filter(email=data['email']).exists():
				return JsonResponse({'error': 'Email already registered'}, status=400)
			user.email = data['email']

		if 'about_me' in data:
			user.about_me = data['about_me']

		if 'profile_pic' in data:
			profile_pic_path = os.path.join('media/profile-pics', data['profile_pic'])
			user.profile_pic = profile_pic_path

		user.save()
		profile_updated_signal.send(sender=update_profile, user=user)
		return JsonResponse({'message': 'Profile updated successfully'})

	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	except Exception as e:
		logger.error(f"Error updating profile: {str(e)}")
		return JsonResponse({'error': 'An error occurred while updating the profile'}, status=500)



@require_http_methods(["GET"])
def find_user(request):
	if not request.user.is_authenticated:
		return HttpResponseForbidden('Not authenticated')
		
	query = request.GET.get('q', '').strip()
	if not query or len(query) < 2:
		return JsonResponse({'results': []})

	matching_users = User.objects.filter(
		username__icontains=query
	).values('username', 'profile_pic')[:10]
	
	results = list(matching_users)
	return JsonResponse({'results': results})