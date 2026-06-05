from django.contrib import admin
from .models import BrailleCharacter, BrailleSentence, PracticeSession


@admin.register(BrailleCharacter)
class BrailleCharacterAdmin(admin.ModelAdmin):
    list_display = ('character', 'dots', 'unicode_repr', 'grade')
    list_filter = ('grade',)
    search_fields = ('character',)


@admin.register(BrailleSentence)
class BrailleSentenceAdmin(admin.ModelAdmin):
    list_display = ('text', 'difficulty_level', 'created_by', 'created_at')
    list_filter = ('difficulty_level',)


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_type', 'accuracy', 'started_at', 'ended_at')
    list_filter = ('session_type',)
