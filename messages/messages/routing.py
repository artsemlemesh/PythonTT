from django.urls import re_path
from myapp.consumers import EmailProgressConsumer

websocket_urlpatterns = [
    re_path(r'ws/messages/$', EmailProgressConsumer.as_asgi()),
]