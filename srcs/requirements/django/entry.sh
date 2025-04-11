#!/bin/bash

python manage.py makemigrations backend pong authservice tournaments dashboard

python manage.py migrate

# should only run once
DJANGO_SUPERUSER_PASSWORD="$(cat /run/secrets/web_adm_psw)" python manage.py createsuperuser \
	--noinput \
	--username "$(cat /run/secrets/web_adm)" \
	--email "$(cat /run/secrets/web_adm)"@transcendence.com


python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="Banana").exists():
    User.objects.create_user(
        username="Banana",
        email="banana_null@noway.net",
        password="12345"
    )
EOF

python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="Jonas").exists():
    User.objects.create_user(
        username="Jonas",
        email="jonas_null@noway.net",
        password="12345"
    )
EOF

python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="Roger").exists():
    User.objects.create_user(
        username="Roger",
        email="roger_null@noway.net",
        password="12345"
    )
EOF

python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="Sam").exists():
    User.objects.create_user(
        username="Sam",
        email="sam_null@noway.net",
        password="12345"
    )
EOF

python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="Bilbo").exists():
    User.objects.create_user(
        username="Bilbo",
        email="bilbo_null@noway.net",
        password="12345"
    )
EOF

python manage.py runserver 0.0.0.0:8080
