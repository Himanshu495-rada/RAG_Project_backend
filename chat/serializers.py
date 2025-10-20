"""
Serializers for chat models
"""
from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'role', 'content', 'timestamp',
            'source_chunks', 'audio_file_path', 'metadata'
        ]
        read_only_fields = ['id', 'timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model"""
    message_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'session_id', 'created_at', 'last_updated',
            'metadata', 'message_count'
        ]
        read_only_fields = ['id', 'created_at', 'last_updated', 'message_count']


class ConversationDetailSerializer(ConversationSerializer):
    """Detailed serializer for Conversation with messages"""
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages']


class ChatQuerySerializer(serializers.Serializer):
    """Serializer for RAG query requests"""
    question = serializers.CharField(
        required=True,
        help_text="User's question to ask the RAG system"
    )
    conversation_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="Optional conversation ID to continue existing conversation"
    )
    document_filter = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        allow_empty=True,
        help_text="Optional list of document IDs to search within"
    )
    top_k = serializers.IntegerField(
        default=5,
        min_value=1,
        max_value=20,
        help_text="Number of chunks to retrieve (1-20)"
    )


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for RAG query responses"""
    answer = serializers.CharField()
    conversation_id = serializers.UUIDField()
    sources = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of source chunks used for the answer"
    )
    metadata = serializers.DictField(required=False)
