FROM python:latest

RUN apt-get update && apt-get upgrade -y

RUN pip install --root-user-action=ignore django

RUN pip install --root-user-action=ignore psycopg2

RUN pip install --root-user-action=ignore channels

RUN pip install --root-user-action=ignore daphne[http2]

RUN django-admin startproject runtime

COPY entry.sh /

RUN chmod +x entry.sh

RUN python /runtime/manage.py startapp backend

CMD ["./entry.sh"]