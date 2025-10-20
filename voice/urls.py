from django.urls import path
from . import views

urlpatterns = [
    path('text-to-speech/', views.TextToSpeechView.as_view(), name='text-to-speech'),
    path('speech-to-text/', views.SpeechToTextView.as_view(), name='speech-to-text'),
    path('chat/', views.VoiceChatView.as_view(), name='voice-chat'),
]
