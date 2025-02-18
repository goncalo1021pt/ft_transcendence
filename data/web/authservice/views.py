from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from backend.forms import UserRegistrationForm
import json
import uuid


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

