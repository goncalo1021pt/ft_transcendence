from django.urls import path
from .pong import pong

websocket_urlpatterns = [
    path('ws/pong/', pong.SinglePongConsumer.as_asgi()),
]