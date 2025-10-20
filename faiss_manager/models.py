"""
Database models for FAISS index management
"""
import uuid
from django.db import models
from django.utils import timezone


class FAISSIndex(models.Model):
    """Model for FAISS index metadata"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    index_name = models.CharField(max_length=255, unique=True)
    index_file_path = models.CharField(max_length=500)
    metadata_file_path = models.CharField(max_length=500)
    dimension = models.IntegerField(
        default=384,
        help_text="Embedding dimension (384 for MiniLM)"
    )
    total_vectors = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    documents_included = models.JSONField(
        default=list,
        blank=True,
        help_text="Array of Document IDs included in this index"
    )
    
    class Meta:
        db_table = 'faiss_indexes'
        ordering = ['-last_updated']
        indexes = [
            models.Index(fields=['index_name']),
            models.Index(fields=['-last_updated']),
        ]
    
    def __str__(self):
        return f"FAISS Index: {self.index_name} ({self.total_vectors} vectors)"
