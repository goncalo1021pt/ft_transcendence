from django.shortcuts import render, redirect
<<<<<<< HEAD
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from backend.forms import UserRegistrationForm
import json
import uuid
=======
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_backends
from backend.models import User
from backend.forms import UserRegistrationForm
import json
import uuid
import requests
import logging

logger = logging.getLogger('pong')
>>>>>>> refs/remotes/origin/goncalo


def register_request(request):
	if request.user.is_authenticated:
		return JsonResponse({'error': 'Already authenticated'}, status=403)
	if request.method == 'POST':
		data = json.loads(request.body)
		form = UserRegistrationForm(data)
		if form.is_valid():
			user = form.save(commit=False)
			user.set_password(form.cleaned_data['password'])
			user.save()
			return JsonResponse({'message': 'Registration successful'})
		return JsonResponse(form.errors, status=400)
	return JsonResponse({'error': 'Invalid request'}, status=400)


def login_request(request): 
	if request.user.is_authenticated:
		return JsonResponse({'error': 'Already authenticated'}, status=403)
	if request.method == 'POST':
		data = json.loads(request.body)
		username = data.get('username')
		password = data.get('password')
		
		user = authenticate(request, username=username, password=password)
		if user is not None:
			if user.uuid is None:
				user.uuid = uuid.uuid4()
				user.save()
			login(request, user) 
			return JsonResponse({ 
				'message': 'Login successful',
				'user': {
					'uuid': str(user.uuid),
				}
			})
		return JsonResponse({'error': 'Invalid credentials'}, status=401)
	return JsonResponse({'error': 'Invalid request'}, status=400)


def logout_request(request): 
<<<<<<< HEAD
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({'message': 'Logged out successfully'})
    return JsonResponse({'message': 'Already logged out'}, status=200)
=======
	if request.user.is_authenticated:
		logout(request)
		return JsonResponse({'message': 'Logged out successfully'})
	return JsonResponse({'message': 'Already logged out'}, status=200)
>>>>>>> refs/remotes/origin/goncalo


def check_auth(request):
	if request.user.is_authenticated:
		return JsonResponse({ 
			'isAuthenticated': True,
			'user': {
				'uuid': str(request.user.uuid),
			}
		})
	return JsonResponse({'isAuthenticated': False})

<<<<<<< HEAD
=======
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

def oauth_callback(request):
	logger.debug(request)
	code = request.GET.get('code')
	if not code:
		return redirect('login')

	token_url = 'https://api.intra.42.fr/oauth/token'
	token_data = {
		'grant_type': 'authorization_code',
		'client_id': settings.SOCIALACCOUNT_PROVIDERS['42school']['APP']['client_id'],
		'client_secret': settings.SOCIALACCOUNT_PROVIDERS['42school']['APP']['secret'],
		'code': code,
		'redirect_uri': 'https://localhost/oauth/callback/',
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
		if user.uuid is None:
			user.uuid = uuid.uuid4()
			user.save()
	except User.DoesNotExist:
		# If the user does not exist, create a new user
		user = User(username=username, email=email, id_42=user_id, is_api_user=True)
		user.set_unusable_password()
		user.uuid = uuid.uuid4()
		user.save()


	# Get the authentication backends configured in Django settings
	backends = get_backends()
	user.backend = f'{backends[0].__module__}.{backends[0].__class__.__name__}'

	login(request, user)
	return redirect('/#/profile')
>>>>>>> refs/remotes/origin/goncalo
