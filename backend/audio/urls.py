from django.urls import path
from .views import AudioUploadView, AudioRecordingListView, AudioRecordingDetailView

urlpatterns = [
    path('upload/', AudioUploadView.as_view(), name='audio_upload'),
    path('recordings/', AudioRecordingListView.as_view(), name='audio_list'),
    path('recordings/<int:pk>/', AudioRecordingDetailView.as_view(), name='audio_detail'),
]
