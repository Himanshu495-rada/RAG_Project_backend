"""
Views for chat and RAG queries
"""
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
import uuid

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer,
    ChatQuerySerializer,
    ChatResponseSerializer
)
from .services import chat_service
import logging

logger = logging.getLogger(__name__)


class ChatQueryView(APIView):
    """Process RAG query"""
    
    def post(self, request, *args, **kwargs):
        """Handle RAG query request"""
        serializer = ChatQuerySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        question = serializer.validated_data['question']
        conversation_id = serializer.validated_data.get('conversation_id')
        document_filter = serializer.validated_data.get('document_filter', [])
        top_k = serializer.validated_data.get('top_k', 5)
        
        # Get or create conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response(
                    {'error': 'Conversation not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Create new conversation
            conversation = Conversation.objects.create(
                session_id=str(uuid.uuid4())
            )
            conversation_id = str(conversation.id)
        
        try:
            # Save user message
            chat_service.save_message(
                conversation_id=conversation_id,
                role='user',
                content=question
            )
            
            # Process RAG query
            logger.info(f"Processing RAG query: {question[:50]}...")
            result = chat_service.process_query(
                question=question,
                conversation_id=conversation_id,
                document_ids=document_filter if document_filter else None,
                top_k=top_k
            )
            
            # Save assistant response
            source_chunk_ids = [src['chunk_id'] for src in result['sources']]
            chat_service.save_message(
                conversation_id=conversation_id,
                role='assistant',
                content=result['answer'],
                source_chunks=source_chunk_ids
            )
            
            response_data = {
                'answer': result['answer'],
                'conversation_id': conversation_id,
                'sources': result['sources'],
                'metadata': {
                    'chunks_retrieved': result.get('chunks_retrieved', 0),
                    'question': question
                }
            }
            
            response_serializer = ChatResponseSerializer(data=response_data)
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                logger.error(f"Response serializer errors: {response_serializer.errors}")
                return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error processing RAG query: {str(e)}")
            return Response(
                {
                    'error': 'Failed to process query',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationCreateView(generics.CreateAPIView):
    """Create new conversation"""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    
    def perform_create(self, serializer):
        """Auto-generate session_id if not provided"""
        if not serializer.validated_data.get('session_id'):
            serializer.save(session_id=str(uuid.uuid4()))
        else:
            serializer.save()


class ConversationMessagesView(generics.ListAPIView):
    """Get all messages for a specific conversation"""
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        """Get messages for the specified conversation"""
        conversation_id = self.kwargs.get('pk')
        return Message.objects.filter(conversation_id=conversation_id)


class ConversationDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete conversation details"""
    queryset = Conversation.objects.all()
    serializer_class = ConversationDetailSerializer
