"""
Placeholder views for FAISS manager app.
Will be implemented in the next step.
"""
from rest_framework.views import APIView
from rest_framework.response import Response


class FAISSStatusView(APIView):
    """Get FAISS index status"""
    pass


class FAISSRebuildView(APIView):
    """Rebuild FAISS index"""
    pass
