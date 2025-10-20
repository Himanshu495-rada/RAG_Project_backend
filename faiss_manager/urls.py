from django.urls import path
from . import views

urlpatterns = [
    path('status/', views.FAISSStatusView.as_view(), name='faiss-status'),
    path('rebuild/', views.FAISSRebuildView.as_view(), name='faiss-rebuild'),
]
