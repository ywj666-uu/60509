from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from .models import AudioRecording
from .serializers import AudioRecordingSerializer, AudioUploadSerializer
from .tasks import process_audio_recording
from braille.models import PracticeSession, BrailleCharacter


class AudioUploadView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def post(self, request):
        serializer = AudioUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data['session_id']
        try:
            session = PracticeSession.objects.get(id=session_id, user=request.user)
        except PracticeSession.DoesNotExist:
            return Response(
                {'error': '练习会话不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        target_character = None
        target_char_id = serializer.validated_data.get('target_character_id')
        if target_char_id:
            try:
                target_character = BrailleCharacter.objects.get(id=target_char_id)
            except BrailleCharacter.DoesNotExist:
                return Response(
                    {'error': '目标字符不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )

        recording = AudioRecording.objects.create(
            user=request.user,
            session=session,
            audio_file=serializer.validated_data['audio_file'],
            target_character=target_character,
        )

        process_audio_recording.delay(recording.id)

        return Response(
            AudioRecordingSerializer(recording).data,
            status=status.HTTP_202_ACCEPTED
        )


class AudioRecordingListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        recordings = AudioRecording.objects.filter(user=request.user)
        session_id = request.query_params.get('session_id')
        if session_id:
            recordings = recordings.filter(session_id=session_id)
        serializer = AudioRecordingSerializer(recordings[:50], many=True)
        return Response(serializer.data)


class AudioRecordingDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            recording = AudioRecording.objects.get(id=pk, user=request.user)
        except AudioRecording.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(AudioRecordingSerializer(recording).data)
