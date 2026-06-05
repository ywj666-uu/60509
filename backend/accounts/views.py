from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, UserProfileSerializer
from .models import UserProfile, CharacterProficiency

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProficiencyStatsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        from braille.models import PracticeSession
        from audio.models import AudioRecording

        sessions = PracticeSession.objects.filter(user=user)
        recordings = AudioRecording.objects.filter(user=user, processing_status='completed')

        total_sessions = sessions.count()
        total_recordings = recordings.count()
        correct_count = recordings.filter(is_correct=True).count()

        # Per-character proficiency (the real source of truth)
        char_profs = CharacterProficiency.objects.filter(user=user).select_related('character')
        char_data = []
        for cp in char_profs:
            char_data.append({
                'character': cp.character.character,
                'unicode_repr': cp.character.unicode_repr,
                'accuracy': round(cp.accuracy * 100, 1),
                'weighted_score': round(cp.weighted_score * 100, 1),
                'total_attempts': cp.total_attempts,
                'recent_attempts': cp.recent_attempts,
            })

        # Overall accuracy from per-character weighted scores
        if char_profs.exists():
            overall_accuracy = sum(cp.weighted_score for cp in char_profs) / char_profs.count()
        else:
            overall_accuracy = correct_count / total_recordings if total_recordings > 0 else 0.0

        return Response({
            'proficiency_level': user.proficiency_level,
            'total_practice_minutes': user.total_practice_minutes,
            'accuracy_rate': round(overall_accuracy * 100, 2),
            'total_sessions': total_sessions,
            'total_recordings': total_recordings,
            'correct_count': correct_count,
            'character_proficiency': char_data,
        })


class ProficiencyHistoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        from braille.models import PracticeSession
        sessions = (PracticeSession.objects
                    .filter(user=request.user, accuracy__isnull=False)
                    .order_by('started_at')
                    .values('id', 'started_at', 'accuracy', 'session_type'))
        return Response(list(sessions))
