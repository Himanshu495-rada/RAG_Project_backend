"""
Database models for document management
"""
import uuid
from django.db import models
from django.utils import timezone


class Document(models.Model):
    """Model for uploaded PDF documents"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100, default='application/pdf')
    page_count = models.IntegerField(default=0)
    upload_timestamp = models.DateTimeField(default=timezone.now)
    processing_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    processing_error = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'documents'
        ordering = ['-upload_timestamp']
        indexes = [
            models.Index(fields=['-upload_timestamp']),
            models.Index(fields=['processing_status']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} ({self.processing_status})"
    
    @property
    def chunk_count(self):
        """Get total number of chunks for this document"""
        return self.chunks.count()


class Chunk(models.Model):
    """Model for document text chunks"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    chunk_index = models.IntegerField(help_text="Order within document")
    page_number = models.IntegerField()
    chunk_text = models.TextField()
    chunk_token_count = models.IntegerField(default=0)
    start_char_index = models.IntegerField(default=0)
    end_char_index = models.IntegerField(default=0)
    embedding_vector_id = models.CharField(
        max_length=100,
        help_text="Maps to FAISS index position",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'chunks'
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
            models.Index(fields=['embedding_vector_id']),
        ]
        unique_together = ['document', 'chunk_index']
    
    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.document.filename}"
