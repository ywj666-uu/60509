from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, ProficiencyStatsView, ProficiencyHistoryView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('proficiency/stats/', ProficiencyStatsView.as_view(), name='proficiency_stats'),
    path('proficiency/history/', ProficiencyHistoryView.as_view(), name='proficiency_history'),
]
