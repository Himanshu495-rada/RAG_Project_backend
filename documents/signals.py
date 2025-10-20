"""
Signals for document processing
"""
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Document
import os
import logging

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Document)
def delete_document_file(sender, instance, **kwargs):
    """
    Delete the physical PDF file when document is deleted
    """
    if instance.file_path and os.path.exists(instance.file_path):
        try:
            os.remove(instance.file_path)
            logger.info(f"Deleted file: {instance.file_path}")
        except Exception as e:
            logger.error(f"Error deleting file {instance.file_path}: {e}")
