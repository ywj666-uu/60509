from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrailleCharacterViewSet, BrailleSentenceViewSet, PracticeSessionViewSet

router = DefaultRouter()
router.register('characters', BrailleCharacterViewSet)
router.register('sentences', BrailleSentenceViewSet)
router.register('sessions', PracticeSessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
]
