from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PairSession, PairMessage

User = get_user_model()


class PairSessionSerializer(serializers.ModelSerializer):
    initiator_name = serializers.CharField(source='initiator.username', read_only=True)
    partner_name = serializers.CharField(source='partner.username', read_only=True)
    sentence_text = serializers.CharField(source='sentence.text', read_only=True, default=None)

    class Meta:
        model = PairSession
        fields = (
            'id', 'initiator', 'initiator_name', 'partner', 'partner_name',
            'practice_session', 'sentence', 'sentence_text', 'status',
            'created_at', 'ended_at'
        )
        read_only_fields = ('initiator', 'status', 'created_at', 'ended_at')


class PairMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = PairMessage
        fields = ('id', 'pair_session', 'sender', 'sender_name',
                  'message_type', 'content', 'created_at')
        read_only_fields = ('sender', 'created_at')


class AvailablePartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'proficiency_level')
