"""
Placeholder consumers for WebSocket chat.
Will be implemented in the next step.
"""
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        pass
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        pass
