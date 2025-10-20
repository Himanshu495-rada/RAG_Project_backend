"""
Serializers for document models
"""
from rest_framework import serializers
from .models import Document, Chunk


class ChunkSerializer(serializers.ModelSerializer):
    """Serializer for Chunk model"""
    
    class Meta:
        model = Chunk
        fields = [
            'id', 'document', 'chunk_index', 'page_number',
            'chunk_text', 'chunk_token_count', 'start_char_index',
            'end_char_index', 'embedding_vector_id', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'embedding_vector_id']


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""
    chunk_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'filename', 'original_filename', 'file_path',
            'file_size', 'mime_type', 'page_count', 'upload_timestamp',
            'processing_status', 'processing_error', 'metadata', 'chunk_count'
        ]
        read_only_fields = [
            'id', 'filename', 'file_path', 'file_size', 'mime_type',
            'page_count', 'upload_timestamp', 'processing_status',
            'processing_error', 'chunk_count'
        ]


class DocumentDetailSerializer(DocumentSerializer):
    """Detailed serializer for Document with chunks"""
    chunks = ChunkSerializer(many=True, read_only=True)
    
    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ['chunks']


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload"""
    file = serializers.FileField(
        help_text="PDF file to upload",
        required=True
    )
    
    def validate_file(self, value):
        """Validate that the uploaded file is a PDF"""
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed")
        
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size must not exceed 50MB. Current size: {value.size / (1024*1024):.2f}MB"
            )
        
        return value
