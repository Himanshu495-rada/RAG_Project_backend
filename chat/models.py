"""
Database models for chat and conversations
"""
import uuid
from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    """Model for chat conversation sessions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'conversations'
        ordering = ['-last_updated']
        indexes = [
            models.Index(fields=['-last_updated']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Conversation {self.session_id}"
    
    @property
    def message_count(self):
        """Get total number of messages in conversation"""
        return self.messages.count()


class Message(models.Model):
    """Model for chat messages"""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    source_chunks = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of Chunk IDs used for this response"
    )
    audio_file_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Path to audio file for voice messages"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Stores citations, confidence scores, etc."
    )
    
    class Meta:
        db_table = 'messages'
        ordering = ['conversation', 'timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.role} message in {self.conversation.session_id}"
