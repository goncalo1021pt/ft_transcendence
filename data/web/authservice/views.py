from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from backend.forms import UserRegistrationForm
import json
import uuid
import requests


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
	if request.user.is_authenticated:
		logout(request)
		return JsonResponse({'message': 'Logged out successfully'})
	return JsonResponse({'message': 'Already logged out'}, status=200)


def check_auth(request):
	if request.user.is_authenticated:
		return JsonResponse({ 
			'isAuthenticated': True,
			'user': {
				'uuid': str(request.user.uuid),
			}
		})
	return JsonResponse({'isAuthenticated': False})

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
	code = request.GET.get('code')
	if not code:
		return redirect('login')
	
	token_url = 'https://api.intra.42.fr/oauth/token'
	token_data = {
		'grant_type': 'authorization_code',
		'client_id': settings.SOCIALACCOUNT_PROVIDERS['42school']['APP']['client_id'],
		'client_secret': settings.SOCIALACCOUNT_PROVIDERS['42school']['APP']['secret'],
		'code': code,
		'redirect_uri': 'http://localhost:8080/oauth/callback/',
	}
	json_token = requests.post(token_url, data=token_data).json()
	acces_token = json_token['access_token']

	if not acces_token:
		return redirect('login')
	
	user_info_url = 'https://api.intra.42.fr/v2/me'
	headers = {'Authorization': f'Bearer {acces_token}',}
	user_info = requests.get(user_info_url, headers=headers).json()

	username = user_info['login']
	email = user_info['email']
	
	user, created = User.objects.get_or_create(username=username, defaults={'email': email})
	if created:
		user.set_unusable_password()
		user.save()

	login(request, user)
	return redirect('home-view')