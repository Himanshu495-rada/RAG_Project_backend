from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.DocumentUploadView.as_view(), name='document-upload'),
    path('', views.DocumentListView.as_view(), name='document-list'),
    path('<uuid:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    path('<uuid:pk>/chunks/', views.DocumentChunksView.as_view(), name='document-chunks'),
]
