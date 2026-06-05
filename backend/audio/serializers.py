from rest_framework import serializers
from .models import AudioRecording


class AudioRecordingSerializer(serializers.ModelSerializer):
    target_character_name = serializers.CharField(
        source='target_character.character', read_only=True, default=None
    )

    class Meta:
        model = AudioRecording
        fields = (
            'id', 'user', 'session', 'audio_file', 'target_character',
            'target_character_name', 'predicted_character', 'confidence',
            'is_correct', 'processing_status', 'error_message', 'created_at'
        )
        read_only_fields = (
            'user', 'predicted_character', 'confidence', 'is_correct',
            'processing_status', 'error_message', 'created_at'
        )


class AudioUploadSerializer(serializers.Serializer):
    audio_file = serializers.FileField()
    session_id = serializers.IntegerField()
    target_character_id = serializers.IntegerField(required=False)
