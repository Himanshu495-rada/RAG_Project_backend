"""
Views for document management
"""
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
import os
import uuid

from .models import Document, Chunk
from .serializers import (
    DocumentSerializer,
    DocumentDetailSerializer,
    DocumentUploadSerializer,
    ChunkSerializer
)
from .services import pdf_service
from faiss_manager.services import faiss_service
import logging

logger = logging.getLogger(__name__)


class DocumentUploadView(APIView):
    """Upload PDF document"""
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        """Handle PDF file upload"""
        serializer = DocumentUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = serializer.validated_data['file']
        
        # Generate unique filename
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.PDF_STORAGE_PATH, unique_filename)
        
        # Ensure directory exists
        os.makedirs(settings.PDF_STORAGE_PATH, exist_ok=True)
        
        # Save file to disk
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Create document record
        document = Document.objects.create(
            filename=unique_filename,
            original_filename=uploaded_file.name,
            file_path=file_path,
            file_size=uploaded_file.size,
            mime_type=uploaded_file.content_type or 'application/pdf',
            processing_status='pending'
        )
        
        try:
            # Process document immediately (in future, use Celery for async)
            logger.info(f"Processing document {document.id}...")
            success = pdf_service.process_document(document)
            
            if success:
                # Rebuild FAISS index with new document
                logger.info("Rebuilding FAISS index...")
                faiss_service.build_index()
                logger.info("FAISS index rebuilt successfully")
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            document.processing_status = 'failed'
            document.processing_error = str(e)
            document.save()
        
        # Refresh from database to get updated status
        document.refresh_from_db()
        
        return Response(
            {
                'message': 'Document uploaded successfully',
                'document': DocumentSerializer(document).data
            },
            status=status.HTTP_201_CREATED
        )


class DocumentListView(generics.ListAPIView):
    """List all documents with pagination"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    
    def get_queryset(self):
        """Filter documents by status if provided"""
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status', None)
        
        if status_filter:
            queryset = queryset.filter(processing_status=status_filter)
        
        return queryset


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete document details"""
    queryset = Document.objects.all()
    serializer_class = DocumentDetailSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Delete document and associated file"""
        instance = self.get_object()
        
        # Delete associated chunks from FAISS index
        # TODO: Implement FAISS cleanup
        
        # File will be deleted by signal handler
        self.perform_destroy(instance)
        
        return Response(
            {'message': 'Document deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


class DocumentChunksView(generics.ListAPIView):
    """Get all chunks for a specific document"""
    serializer_class = ChunkSerializer
    
    def get_queryset(self):
        """Get chunks for the specified document"""
        document_id = self.kwargs.get('pk')
        return Chunk.objects.filter(document_id=document_id)
