"""
Database models for voice interactions
"""
import uuid
from django.db import models
from django.utils import timezone
from chat.models import Message


class VoiceInteraction(models.Model):
    """Model for voice TTS/STT interactions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='voice_interactions',
        null=True,
        blank=True
    )
    input_audio_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Path to input audio file (for STT)"
    )
    output_audio_path = models.CharField(
        max_length=500,
        help_text="Path to output audio file (for TTS)"
    )
    voice_model = models.CharField(
        max_length=50,
        default='alloy',
        help_text="Voice model used (alloy, nova, etc.)"
    )
    duration_seconds = models.FloatField(
        default=0.0,
        help_text="Audio duration in seconds"
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'voice_interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['message']),
        ]
    
    def __str__(self):
        return f"Voice interaction {self.id}"
