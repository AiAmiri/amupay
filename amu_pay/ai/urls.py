"""
URL patterns for AI Chat endpoint
Simple chat endpoint for frontend integration
"""

from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    # Main chat endpoint - for frontend
    path('chat/', views.AIChatView.as_view(), name='ai_chat'),
    
    # Clear conversation memory (optional)
    path('clear-memory/', views.ClearMemoryView.as_view(), name='clear_memory'),
]
