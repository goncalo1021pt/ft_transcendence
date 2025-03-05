FROM nginx:latest

RUN apt-get update && apt-get upgrade -y

RUN apt-get install -y openssl

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -subj "/C=PT/L=LISBOA/O=42/OU=student/CN=rlandolt"

COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]