"""
Admin interface for voice models
"""
from django.contrib import admin
from .models import VoiceInteraction


@admin.register(VoiceInteraction)
class VoiceInteractionAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'voice_model', 'duration_seconds', 'created_at']
    list_filter = ['voice_model', 'created_at']
    search_fields = ['message__content']
    readonly_fields = ['id', 'created_at', 'duration_seconds']
    
    fieldsets = (
        ('Interaction Information', {
            'fields': ('id', 'message', 'voice_model', 'created_at')
        }),
        ('Audio Files', {
            'fields': ('input_audio_path', 'output_audio_path', 'duration_seconds')
        }),
    )
