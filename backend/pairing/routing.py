from django.urls import path
from .consumers import PairPracticeConsumer

websocket_urlpatterns = [
    path('ws/pair/<int:session_id>/', PairPracticeConsumer.as_asgi()),
]
