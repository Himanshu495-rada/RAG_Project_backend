from django.urls import path
from . import views

urlpatterns = [
    path('query/', views.ChatQueryView.as_view(), name='chat-query'),
    path('conversations/', views.ConversationCreateView.as_view(), name='conversation-create'),
    path('conversations/<uuid:pk>/messages/', views.ConversationMessagesView.as_view(), name='conversation-messages'),
    path('conversations/<uuid:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
]
