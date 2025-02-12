from django.urls import path
from .pong import SinglePongConsumer, MultiPongConsumer, QuickLobby

websocket_urlpatterns = [
    path('ws/spong/', SinglePongConsumer.as_asgi()),
    path('ws/mpong/', QuickLobby.as_asgi()),
	path('ws/mpong/game/<str:game_id>/', MultiPongConsumer.as_asgi())
]