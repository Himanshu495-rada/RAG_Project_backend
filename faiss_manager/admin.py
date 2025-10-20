"""
Admin interface for FAISS index models
"""
from django.contrib import admin
from .models import FAISSIndex


@admin.register(FAISSIndex)
class FAISSIndexAdmin(admin.ModelAdmin):
    list_display = ['index_name', 'total_vectors', 'dimension', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['index_name']
    readonly_fields = ['id', 'last_updated', 'total_vectors']
    
    fieldsets = (
        ('Index Information', {
            'fields': ('id', 'index_name', 'dimension', 'total_vectors')
        }),
        ('Files', {
            'fields': ('index_file_path', 'metadata_file_path')
        }),
        ('Metadata', {
            'fields': ('last_updated', 'documents_included'),
            'classes': ('collapse',)
        }),
    )
