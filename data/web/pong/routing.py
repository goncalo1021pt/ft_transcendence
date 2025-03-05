from django.urls import path
from .consumers import SinglePongConsumer, MultiPongConsumer
from .lobby import QuickLobby

websocket_urlpatterns = [
    path('wss/spong/', SinglePongConsumer.as_asgi()),
    path('wss/mpong/', QuickLobby.as_asgi()),
	path('wss/mpong/game/<str:game_id>/', MultiPongConsumer.as_asgi())
]