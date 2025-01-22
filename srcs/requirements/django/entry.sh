#!/bin/bash

python /runtime/manage.py makemigrations backend

python /runtime/manage.py migrate

# should only run once
DJANGO_SUPERUSER_PASSWORD="$(cat /run/secrets/web_adm_psw)" python /runtime/manage.py createsuperuser \
	--noinput \
	--username "$(cat /run/secrets/web_adm)" \
	--email "$(cat /run/secrets/web_adm)"@transcendence.com


python /runtime/manage.py runserver 0.0.0.0:8080
