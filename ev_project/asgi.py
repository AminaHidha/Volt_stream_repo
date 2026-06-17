"""
ASGI config for ev_project.

This file decides: "is this incoming connection a normal webpage/API
request (HTTP), or is it a WebSocket (live connection)?" and sends it
to the right place.
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ev_project.settings')

# This MUST be created before importing anything that touches models,
# which is why django_asgi_app is set up first.
django_asgi_app = get_asgi_application()

from realtime.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    # Normal Django views, DRF APIs, admin panel — all unchanged.
    "http": django_asgi_app,

    # WebSocket connections go through this list of routes instead.
    "websocket": URLRouter(websocket_urlpatterns),
})