"""
Placeholder views for voice app.
Will be implemented in the next step.
"""
from rest_framework.views import APIView
from rest_framework.response import Response


class TextToSpeechView(APIView):
    """Convert text to speech"""
    pass


class SpeechToTextView(APIView):
    """Convert speech to text"""
    pass


class VoiceChatView(APIView):
    """Combined voice chat (STT + RAG + TTS)"""
    pass
