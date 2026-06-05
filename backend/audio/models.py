from django.db import models
from django.conf import settings


class AudioRecording(models.Model):
    PROCESSING_STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recordings'
    )
    session = models.ForeignKey(
        'braille.PracticeSession', on_delete=models.CASCADE, related_name='recordings'
    )
    audio_file = models.FileField(upload_to='recordings/%Y/%m/%d/')
    target_character = models.ForeignKey(
        'braille.BrailleCharacter', on_delete=models.SET_NULL, null=True, blank=True
    )
    predicted_character = models.CharField(max_length=1, blank=True, default='')
    confidence = models.FloatField(null=True, blank=True)
    is_correct = models.BooleanField(null=True)
    processing_status = models.CharField(
        max_length=20, choices=PROCESSING_STATUS_CHOICES, default='pending'
    )
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audio_recordings'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.target_character} - {self.processing_status}'
