#!/bin/bash
cd /ft_transcendence

python manage.py makemigrations backend pong authservice

python manage.py migrate

# should only run once
DJANGO_SUPERUSER_PASSWORD="$(cat /run/secrets/web_adm_psw)" python manage.py createsuperuser \
	--noinput \
	--username "$(cat /run/secrets/web_adm)" \
	--email "$(cat /run/secrets/web_adm)"@transcendence.com


python manage.py runserver 0.0.0.0:8080
