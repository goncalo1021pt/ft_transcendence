"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
from authservice.config import SOCIALACCOUNT_PROVIDERS as FORTY_TWO_PROVIDERS

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'verbose': {
			'format': '[{levelname}] {message}',
			'style': '{'
		}
	},
	'handlers': {
		'console': {
			'class': 'logging.StreamHandler',
			'formatter': 'verbose',
			'level': 'DEBUG',
		},
	},
	'loggers': {
		'pong': {
			'handlers': ['console'],
			'level': 'DEBUG',
			'propagate': False,
		},
	}
}
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-r3%a9xhfwbm8+2bq(%%_r77)%(-7s3xq_$$4g@0q9=%03xd(za'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '*',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

def generate_trusted_origins(base_ip, start, end, port):
    origins = []
    for j in range(start, end + 1):  # Third octet
        for i in range(start, end + 1):  # Fourth octet
            origins.append(f"https://{base_ip}.{j}.{i}:{port}")
    return origins



CSRF_TRUSTED_ORIGINS = [
	'https://localhost:4443',
]

CSRF_TRUSTED_ORIGINS.extend(generate_trusted_origins('10.195', 1, 255, 4443))

#CSRF_TRUSTED_ORIGINS.extend(generate_trusted_origins('10.12', 1, 255, 4443))

SECURE_SSL_REDIRECT = True

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

# Application definition

SITE_ID = 1

INSTALLED_APPS = [
	'daphne',
	'channels',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.sites',
	'django.contrib.postgres',
	'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.oauth2',
	'backend',
	'pong',
	'tournaments',
	'authservice',
	'dashboard',
]

AUTH_USER_MODEL = 'backend.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]
ROOT_URLCONF = 'runtime.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'templates', 'views',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'runtime.wsgi.application'

ASGI_APPLICATION = 'runtime.asgi.application'

CHANNEL_LAYERS = {
	"default": {
		"BACKEND": "channels.layers.InMemoryChannelLayer"
	}
}

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

def read_secret(secret_name):
	try:
		with open('/run/secrets/' + secret_name) as f:
			return f.read().strip()
	except IOError:
		return None

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': read_secret('db_name'),
		'USER': read_secret('db_user'),
		'PASSWORD': read_secret('db_user_psw'),
		'HOST': 'postgres',
		'PORT': '5432',
	}
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static',]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
	'42school': {
		'SCOPE': [
			'email',
			'profile',
		],
		'AUTH_PARAMS': {
			'access_type': 'online',
		},
		'APP': {
			'client_id': read_secret('42_uid'),
			'secret': read_secret('42_secret'),
			'key': '',
		},
	}
}

WEB_HOST = read_secret('web_host')