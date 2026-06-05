from rest_framework import serializers
from .models import BrailleCharacter, BrailleSentence, PracticeSession


class BrailleCharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrailleCharacter
        fields = ('id', 'character', 'dots', 'unicode_repr', 'grade', 'description')


class BrailleSentenceSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True, default=None)

    class Meta:
        model = BrailleSentence
        fields = ('id', 'text', 'braille_text', 'difficulty_level',
                  'created_by', 'created_by_username', 'created_at')
        read_only_fields = ('created_by', 'created_at')


class PracticeSessionSerializer(serializers.ModelSerializer):
    sentence_text = serializers.CharField(source='sentence.text', read_only=True, default=None)

    class Meta:
        model = PracticeSession
        fields = ('id', 'user', 'sentence', 'sentence_text', 'started_at',
                  'ended_at', 'accuracy', 'session_type')
        read_only_fields = ('user', 'started_at')
