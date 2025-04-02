from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_backends
from backend.models import User
from backend.forms import UserRegistrationForm
import json, requests, logging

logger = logging.getLogger('pong')

@require_http_methods(["POST"])
def register_request(request):
	if request.user.is_authenticated:
		return JsonResponse({'error': 'Already authenticated'}, status=403)
	data = json.loads(request.body)
	form = UserRegistrationForm(data)
	if form.is_valid():
		user = form.save(commit=False)
		user.set_password(form.cleaned_data['password'])
		user.save()
		return JsonResponse({'message': 'Registration successful'})
	return JsonResponse(form.errors, status=400)


@require_http_methods(["POST"])
def login_request(request):
	if request.user.is_authenticated:
		return JsonResponse({'error': 'Already authenticated'}, status=403)
	data = json.loads(request.body)
	username = data.get('username')
	password = data.get('password')
	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		return JsonResponse({
			'message': 'Login successful',
		})
	return JsonResponse({'error': 'Invalid credentials'}, status=401)


@login_required
@require_http_methods(["POST"])
def logout_request(request):
	if request.user.is_authenticated:
		logout(request)
		return JsonResponse({'message': 'Logout successful'})
	return JsonResponse({'error': 'Not authenticated'}, status=403)


@require_http_methods(["GET"])
def check_auth(request):
	if request.user.is_authenticated:
		return JsonResponse({
			'isAuthenticated': True,
			'user': {
				'uuid': str(request.user.uuid),
				'username': str(request.user.username),
				'profile_pic': str(request.user.profile_pic),
			}
		})
	return JsonResponse({'isAuthenticated': False})

@login_required
@require_http_methods(["POST"])
def change_password(request):
	try:
		data = json.loads(request.body)
		user : User = request.user

		current_password = data.get('current_password')
		new_password = data.get('new_password')
		if not current_password or not new_password:
			return JsonResponse({'error': 'Both current and new passwords are required'}, status=400)

		if len(new_password) < 8:
					return JsonResponse({'error': 'New password must be at least 8 characters long'}, status=400)

		if not user.check_password(current_password):
			return JsonResponse({'error': 'Current password is incorrect'}, status=400)

		user.set_password(new_password)
		user.save()

		update_session_auth_hash(request, user)

		return JsonResponse({'success': True, 'message': 'Password changed successfully'})

	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	except Exception as e:
		logger.error(f"Error changing password: {str(e)}")
		return JsonResponse({'error': 'An error occurred while changing the password'}, status=500)

@require_http_methods(["GET"])
def get_host(request):
	host = settings.WEB_HOST
	return JsonResponse({
		'host': host,
	})

@login_required 
@require_http_methods(["POST"])
def update_2fa(request):
    try:
        data = json.loads(request.body)
        two_factor_enable = data.get('two_factor_enable', False)

        # Update the user's two_factor_enable field
        request.user.two_factor_enable = two_factor_enable
        request.user.save()

        return JsonResponse({
            'success': True,
            'message': f"Two-factor authentication {'enabled' if two_factor_enable else 'disabled'}"
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': "Invalid request format"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)	


# @require_http_methods(["POST"])
def get_user_42(request):
	if request.user.is_authenticated:
		return JsonResponse({
			'isAuthenticated': True,
			'user': {
				'uuid': str(request.user.uuid),
				'username': request.user.username,
				'email': request.user.email,
				'first_name': request.user.first_name,
				'last_name': request.user.last_name,
			}
		})
	return JsonResponse({'isAuthenticated': False})


# @require_http_methods(["POST"])
def oauth_callback(request):
	code = request.GET.get('code')
	if not code:
		return redirect('login')

	host = settings.WEB_HOST

	token_url = 'https://api.intra.42.fr/oauth/token'
	redirect_uri = f'https://{host}/oauth/callback/'

	token_data = {
		'grant_type': 'authorization_code',
		'client_id': settings.SOCIALACCOUNT_PROVIDERS['42school']['APP']['client_id'],
		'client_secret': settings.SOCIALACCOUNT_PROVIDERS['42school']['APP']['secret'],
		'code': code,
		'redirect_uri': redirect_uri,
	}
	token_response = requests.post(token_url, data=token_data)
	token_json = token_response.json()
	access_token = token_json.get('access_token')

	if not access_token:
		logger.error('Access token not found in token response')
		return JsonResponse({'error': 'Invalid request'}, status=400)

	user_info_url = 'https://api.intra.42.fr/v2/me'
	headers = {'Authorization': f'Bearer {access_token}'}
	user_info_response = requests.get(user_info_url, headers=headers)
	user_info = user_info_response.json()

	username = user_info.get('login')
	email = user_info.get('email')
	user_id = user_info.get('id')
	profile_pic_url = user_info.get('image', {}).get('link')

	# Create user if not exists
	try:
		user = User.objects.get(username=username)
		if not user.is_42_user:
			# Handle username conflict by generating a new username
			for i in range(1, 10000):
				new_username = f'{username}_{i}'
				if not User.objects.filter(username=new_username).exists():
					username = new_username
					break

	except User.DoesNotExist:
		# If the user does not exist, create a new user
		user = User(username=username, email=email, id_42=user_id, is_42_user=True)
		user.set_unusable_password()
		user.profile_pic = profile_pic_url
		user.is_42_user = True
		user.save()

	# Get the authentication backends configured in Django settings
	backends = get_backends()
	user.backend = f'{backends[0].__module__}.{backends[0].__class__.__name__}'

	login(request, user)
	return redirect('/#/home')


def twoFactor(request):
	return redirect('/#/profile')