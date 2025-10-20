"""
Admin interface for document models
"""
from django.contrib import admin
from .models import Document, Chunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'processing_status', 'page_count', 'chunk_count', 'upload_timestamp']
    list_filter = ['processing_status', 'upload_timestamp']
    search_fields = ['original_filename', 'filename']
    readonly_fields = ['id', 'upload_timestamp', 'file_size', 'page_count', 'chunk_count']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('id', 'original_filename', 'filename', 'file_path', 'mime_type')
        }),
        ('Processing', {
            'fields': ('processing_status', 'processing_error', 'page_count', 'chunk_count')
        }),
        ('Metadata', {
            'fields': ('file_size', 'upload_timestamp', 'metadata'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ['document', 'chunk_index', 'page_number', 'chunk_token_count', 'created_at']
    list_filter = ['document', 'page_number', 'created_at']
    search_fields = ['chunk_text', 'document__original_filename']
    readonly_fields = ['id', 'created_at', 'embedding_vector_id']
    
    fieldsets = (
        ('Chunk Information', {
            'fields': ('id', 'document', 'chunk_index', 'page_number')
        }),
        ('Content', {
            'fields': ('chunk_text', 'chunk_token_count', 'start_char_index', 'end_char_index')
        }),
        ('Embedding', {
            'fields': ('embedding_vector_id', 'created_at')
        }),
    )
