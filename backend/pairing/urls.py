from django.urls import path
from .views import AvailablePartnersView, PairSessionListView, PairSessionDetailView

urlpatterns = [
    path('available/', AvailablePartnersView.as_view(), name='available_partners'),
    path('sessions/', PairSessionListView.as_view(), name='pair_sessions'),
    path('sessions/<int:pk>/', PairSessionDetailView.as_view(), name='pair_session_detail'),
]
