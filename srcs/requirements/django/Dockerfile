FROM python:latest

RUN apt-get update && apt-get upgrade -y

RUN pip install --root-user-action=ignore django

RUN pip install --root-user-action=ignore psycopg2

RUN pip install --root-user-action=ignore channels

RUN pip install --root-user-action=ignore daphne[http2]

RUN django-admin startproject ft_transcendence

COPY entry.sh /

RUN chmod +x entry.sh

# RUN python /ft_transcendence/manage.py startapp backend /ft_transcendence

CMD ["./entry.sh"]