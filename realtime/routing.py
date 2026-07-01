from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/test/$", consumers.TestConsumer.as_asgi()),
    re_path(r"ws/slots/(?P<charger_id>\d+)/$", consumers.SlotConsumer.as_asgi()),
]
