from django.contrib import admin
from .models import PairSession, PairMessage


@admin.register(PairSession)
class PairSessionAdmin(admin.ModelAdmin):
    list_display = ('initiator', 'partner', 'status', 'created_at', 'ended_at')
    list_filter = ('status',)


@admin.register(PairMessage)
class PairMessageAdmin(admin.ModelAdmin):
    list_display = ('pair_session', 'sender', 'message_type', 'created_at')
    list_filter = ('message_type',)
