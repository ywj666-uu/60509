from django.db import models
from django.conf import settings


class BrailleCharacter(models.Model):
    character = models.CharField(max_length=1, unique=True)
    dots = models.CharField(max_length=6)
    unicode_repr = models.CharField(max_length=1)
    grade = models.IntegerField(default=1)
    description = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'braille_characters'
        ordering = ['character']

    def __str__(self):
        return f'{self.character} (dots: {self.dots})'


class BrailleSentence(models.Model):
    text = models.TextField()
    braille_text = models.TextField()
    difficulty_level = models.IntegerField(default=1)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_sentences'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'braille_sentences'
        ordering = ['difficulty_level', 'id']

    def __str__(self):
        return self.text[:50]


class PracticeSession(models.Model):
    SESSION_TYPES = [
        ('solo', '独立练习'),
        ('pair', '结对练习'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sessions'
    )
    sentence = models.ForeignKey(
        BrailleSentence, on_delete=models.SET_NULL, null=True, blank=True
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='solo')

    class Meta:
        db_table = 'practice_sessions'
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user.username} - {self.session_type} - {self.started_at}'
