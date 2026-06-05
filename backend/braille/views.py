from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import BrailleCharacter, BrailleSentence, PracticeSession
from .serializers import (
    BrailleCharacterSerializer, BrailleSentenceSerializer, PracticeSessionSerializer
)


class BrailleCharacterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BrailleCharacter.objects.all()
    serializer_class = BrailleCharacterSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        grade = self.request.query_params.get('grade')
        if grade:
            qs = qs.filter(grade=grade)
        return qs


class BrailleSentenceViewSet(viewsets.ModelViewSet):
    queryset = BrailleSentence.objects.all()
    serializer_class = BrailleSentenceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = super().get_queryset()
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            qs = qs.filter(difficulty_level=difficulty)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PracticeSessionViewSet(viewsets.ModelViewSet):
    serializer_class = PracticeSessionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return PracticeSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        session = self.get_object()
        if session.ended_at:
            return Response({'error': '会话已结束'}, status=status.HTTP_400_BAD_REQUEST)

        from audio.models import AudioRecording
        recordings = AudioRecording.objects.filter(
            session=session, processing_status='completed'
        )
        total = recordings.count()
        correct = recordings.filter(is_correct=True).count()

        session.ended_at = timezone.now()
        session.accuracy = correct / total if total > 0 else 0.0
        session.save()

        # Update user-level accuracy from per-character proficiency (lightweight)
        from accounts.models import CharacterProficiency
        user = request.user
        char_profs = CharacterProficiency.objects.filter(user=user)
        if char_profs.exists():
            user.accuracy_rate = sum(p.accuracy for p in char_profs) / char_profs.count()
            user.proficiency_level = min(10, max(1, int(user.accuracy_rate * 10) + 1))
            user.save(update_fields=['accuracy_rate', 'proficiency_level'])

        return Response(PracticeSessionSerializer(session).data)
