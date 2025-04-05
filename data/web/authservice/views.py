from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_backends
from backend.models import User
from django_otp.util import random_hex
from django_otp.plugins.otp_totp.models import TOTPDevice
from backend.forms import UserRegistrationForm
import json, requests, logging
import qrcode
import base64
from io import BytesIO


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
		#implement 2FA check here
		if user.two_factor_enable:
			return JsonResponse({
				'autenticated': '2fa enabled',
				'user': {
					'uuid': str(user.uuid),
					'username': str(user.username),
					'profile_pic': str(user.profile_pic),
				}}, status=201)
		login(request, user)
		return JsonResponse({
			'message': 'Login successful',
			'user': {
				'uuid': str(user.uuid),
				'username': str(user.username),
				'profile_pic': str(user.profile_pic),
			}
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

@login_required
def twoFactor(request):
	user = request.user
	if user.is_42_user:
		return JsonResponse({'error': '42 users cannot enable 2FA'}, status=403)
	
	if user.two_factor_enable:
		return JsonResponse({'error': '2FA is already enabled'}, status=403)
	
	device, created = TOTPDevice.objects.get_or_create(user=user, name='default')

	if created:
		device.save()

	# Generate otp uri
	issuer = 'transcendence'
	secret = base64.b32encode(bytes.fromhex(device.key)).decode('utf-8')
	algorithm = 'SHA1'
	digits = 6
	period = 30
	otp_uri = (
        f"otpauth://totp/{issuer}:{user.username}"
        f"?secret={secret}&issuer={issuer}&algorithm={algorithm}&digits={digits}&period={period}"
    )

	# Generate QR code
	qr = qrcode.make(otp_uri)
	buffer = BytesIO()
	qr.save(buffer, format='PNG')
	qr_image = buffer.getvalue()

	qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

	return JsonResponse({ 
		'success': True,
		'qr_image': qr_base64,
		'otp_uri': otp_uri,
	})


@require_http_methods(["POST"])
@login_required
def verify_2fa_enable(request):
	try:
		data = json.loads(request.body)
		opt_token = data.get('otp_token')


		if not opt_token:
			return JsonResponse({'error': 'OTP token is required'}, status=400)
		
		user = request.user

		if user.two_factor_enable:
			return JsonResponse({'error': '2FA is already enabled'}, status=403)

		device = TOTPDevice.objects.filter(user=user, name='default').first()
		if not device:
			return JsonResponse({'error': 'Device not found'}, status=404)
		
		logger.debug(f"Verifying OTP token: {opt_token}")
		if device.verify_token(opt_token):
			logger.debug(f"OTP token verified successfully for user: {user.username}")
			user.two_factor_enable = True
			user.save()
			return JsonResponse({'success': True, 'message': '2FA enabled successfully'})
		else:
			return JsonResponse({'error': 'Invalid OTP token'}, status=400)
		
	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	except Exception as e:
		logger.error(f"Error verifying OTP token: {str(e)}")
		return JsonResponse({'error': 'An error occurred while verifying the OTP token'}, status=500)

@require_http_methods(["POST"])
@login_required
def disable_2fa(request):
	user = request.user
	if user.two_factor_enable:
		user.two_factor_enable = False
		device = TOTPDevice.objects.filter(user=user, name='default').first()
		if device:
			device.delete()
		else:
			return JsonResponse({'error': 'Device not found'}, status=404)
		user.save()
		return JsonResponse({'success': True, 'message': '2FA disabled successfully'})
	else:
		return JsonResponse({'error': '2FA is already disabled'}, status=400)

@require_http_methods(["POST"])
def verify_2fa_login(request):
	data = json.loads(request.body)
	logger.debug(f"Received data for 2FA login: {data}")
	opt_token = data.get('code')
	username = data.get('username')
	user = User.objects.filter(username=username).first()
	if not user:
		logger.debug(f"User not found for 2FA login: {username}")
		return JsonResponse({'error': 'User not found'}, status=404)
	logger.debug(f"User for 2FA login: {user.username}")
	
	if not opt_token:
		logger.debug("OTP token is missing for 2FA login")
		return JsonResponse({'error': 'OTP token is required'}, status=400)
	device = TOTPDevice.objects.filter(user=user, name='default').first()
	if not device:
		return JsonResponse({'error': 'Device not found'}, status=404)
	if device.verify_token(opt_token):
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		login(request, user)
		return JsonResponse({
				'message': 'Login successful',
				'user': {
					'uuid': str(user.uuid),
					'username': str(user.username),
					'profile_pic': str(user.profile_pic),
				}
			})
	else:
		return JsonResponse({'error': 'Invalid OTP token'}, status=400)