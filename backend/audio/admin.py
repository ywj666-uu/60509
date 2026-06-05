from django.contrib import admin
from .models import AudioRecording


@admin.register(AudioRecording)
class AudioRecordingAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_character', 'predicted_character',
                    'is_correct', 'confidence', 'processing_status', 'created_at')
    list_filter = ('processing_status', 'is_correct')
    readonly_fields = ('predicted_character', 'confidence', 'is_correct', 'processing_status')
