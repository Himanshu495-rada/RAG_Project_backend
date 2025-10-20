"""
Admin interface for chat models
"""
from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'message_count', 'created_at', 'last_updated']
    list_filter = ['created_at', 'last_updated']
    search_fields = ['session_id']
    readonly_fields = ['id', 'created_at', 'last_updated', 'message_count']
    
    fieldsets = (
        ('Conversation Information', {
            'fields': ('id', 'session_id', 'message_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'timestamp', 'content_preview']
    list_filter = ['role', 'timestamp']
    search_fields = ['content', 'conversation__session_id']
    readonly_fields = ['id', 'timestamp']
    
    fieldsets = (
        ('Message Information', {
            'fields': ('id', 'conversation', 'role', 'timestamp')
        }),
        ('Content', {
            'fields': ('content', 'audio_file_path')
        }),
        ('RAG Context', {
            'fields': ('source_chunks', 'metadata'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        """Show first 50 characters of content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
