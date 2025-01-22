"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'runtime.settings') 

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from backend.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
	"http": get_asgi_application(),
	"websocket": URLRouter(websocket_urlpatterns),
})


# # 1. Simple (no auth)
# from channels.routing import ProtocolTypeRouter, URLRouter
# application = ProtocolTypeRouter({
#     "websocket": URLRouter(websocket_urlpatterns),
# })

# # 2. Session-only
# from channels.sessions import SessionMiddlewareStack
# application = ProtocolTypeRouter({
#     "websocket": SessionMiddlewareStack(
#         URLRouter(websocket_urlpatterns)
#     ),
# })

# # 3. Cookie-only
# from channels.sessions import CookieMiddlewareStack
# application = ProtocolTypeRouter({
#     "websocket": CookieMiddlewareStack(
#         URLRouter(websocket_urlpatterns)
#     ),
# })

# # 4. Token-based
# from channels.auth import TokenAuthMiddlewareStack
# application = ProtocolTypeRouter({
#     "websocket": TokenAuthMiddlewareStack(
#         URLRouter(websocket_urlpatterns)
#     ),
# })
