from django.urls import re_path
from myapp.consumers import EmailProgressConsumer

websocket_urlpatterns = [
    re_path(r'ws/email_progress/$', EmailProgressConsumer.as_asgi()),
]