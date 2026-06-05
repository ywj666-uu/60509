from django.db import models
from django.conf import settings


class PairSession(models.Model):
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('active', '进行中'),
        ('completed', '已完成'),
    ]

    initiator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='initiated_pairs'
    )
    partner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='joined_pairs'
    )
    practice_session = models.ForeignKey(
        'braille.PracticeSession', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pair_sessions'
    )
    sentence = models.ForeignKey(
        'braille.BrailleSentence', on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pair_sessions'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.initiator.username} & {self.partner.username} - {self.status}'


class PairMessage(models.Model):
    MESSAGE_TYPES = [
        ('text', '文本'),
        ('braille_challenge', '盲文挑战'),
        ('audio_result', '识别结果'),
        ('system', '系统消息'),
    ]

    pair_session = models.ForeignKey(
        PairSession, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pair_messages'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.username}: {self.message_type}'
