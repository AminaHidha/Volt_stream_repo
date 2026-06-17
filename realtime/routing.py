"""
realtime/routing.py

This is like urls.py, but for WebSocket connections instead of
normal page/API URLs. It tells Django: "if someone connects to
ws/test/, hand them over to TestConsumer."
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/test/$', consumers.TestConsumer.as_asgi()),
]