"""
Django views for AI Chat with Agent architecture
Uses LangGraph Agent with dual tools:
- SuperTool: Business data queries
- DocumentationTool: App usage queries
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
import json
import logging

# Load settings first to ensure environment variables are set
from amu_pay import settings

# Now import AI components that require environment variables
from ai.rag_helper import get_documentation_context
from ai.agent import get_agent
from saraf_account.authentication import SarafJWTAuthentication

logger = logging.getLogger(__name__)


class AIChatView(APIView):
    """
    Simple chat endpoint with 10 message memory.
    No data collection - just conversation with LLM.
    """
    authentication_classes = [SarafJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def _get_memory_key(self, saraf_id):
        """Generate cache key for conversation memory"""
        return f"ai_memory_{saraf_id}"
    
    def _get_conversation_history(self, saraf_id):
        """Get last 10 messages from memory buffer"""
        memory_key = self._get_memory_key(saraf_id)
        history = cache.get(memory_key, [])
        return history[-10:] if history else []
    
    def _save_to_memory(self, saraf_id, user_msg, ai_msg):
        """Save conversation to memory buffer"""
        memory_key = self._get_memory_key(saraf_id)
        history = cache.get(memory_key, [])
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": ai_msg})
        # Keep last 20 messages (10 exchanges)
        if len(history) > 20:
            history = history[-20:]
        cache.set(memory_key, history, timeout=3600)  # 1 hour memory
    
    def post(self, request):
        """
        Process user query using Agent with dual tools.
        Agent automatically chooses between:
        - SuperTool (business data)
        - DocumentationTool (app usage)
        """
        try:
            authenticated_user = request.user
            query = request.data.get('query', '').strip()
            
            if not query:
                return Response({'error': 'Query is required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Get saraf_id from token
            saraf_id = authenticated_user.saraf_id
            if not saraf_id:
                return Response({'error': 'Saraf ID not found in token'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Get conversation history
            history = self._get_conversation_history(saraf_id)
            
            # Build context with history
            messages = []
            
            # Add conversation history
            for msg in history[-4:]:  # Last 4 messages (2 exchanges)
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current query
            messages.append({
                "role": "user",
                "content": query
            })
            
            logger.info(f"🤖 Processing query for saraf_id {saraf_id}: {query[:50]}...")
            
            # Validate saraf_id is an integer
            if not isinstance(saraf_id, int):
                logger.error(f"Invalid saraf_id type in AIChatView: {type(saraf_id)} = {saraf_id}")
                return Response({'error': f'Invalid saraf_id type: {type(saraf_id)}'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Create agent with dual tools
            try:
                agent = get_agent(authenticated_user)
            except Exception as e:
                logger.error(f"Error creating agent: {str(e)}", exc_info=True)
                return Response({'error': f'Agent creation failed: {str(e)}'}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Invoke agent
            try:
                result = agent.invoke({
                    "messages": messages
                })
            except AttributeError as e:
                error_msg = str(e)
                # Handle known LangChain Google GenAI bug where finish_reason is int instead of enum
                if "'int' object has no attribute 'name'" in error_msg or "finish_reason" in error_msg.lower():
                    logger.warning(f"LangChain Google GenAI finish_reason bug detected: {error_msg}")
                    logger.warning("This is a known issue with langchain-google-genai. Trying workaround...")
                    # Try to get a response anyway by catching the error in the tool
                    # The error happens after the model generates a response, so we might still have useful data
                    return Response({
                        'error': 'AI model response processing error. This is a known issue with the Google GenAI library. Please try again or contact support.',
                        'technical_details': 'finish_reason enum conversion error in langchain-google-genai'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    logger.error(f"AttributeError in agent.invoke: {error_msg}", exc_info=True)
                    return Response({'error': f'Agent invocation error: {error_msg}'}, 
                                  status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Extract final response
            if isinstance(result, dict) and 'messages' in result:
                # Get last message from agent
                last_message = result['messages'][-1]
                ai_response = last_message.content if hasattr(last_message, 'content') else str(last_message)
                logger.info(f"Extracted response from messages, length: {len(str(ai_response))} chars")
            else:
                ai_response = str(result)
                logger.info(f"Response is not dict with messages, converted to string, length: {len(ai_response)} chars")
            
            # Log response preview
            response_preview = str(ai_response)[:100] if ai_response else "Empty"
            logger.info(f"Response preview: {response_preview}...")
            
            # Save to memory buffer
            self._save_to_memory(saraf_id, query, ai_response)
            
            logger.info(f"✅ Query processed successfully for saraf_id {saraf_id}")
            
            return Response({'response': ai_response})
            
        except Exception as e:
            logger.error(f"❌ Error in AIChatView: {str(e)}")
            return Response({'error': str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClearMemoryView(APIView):
    """
    Clear conversation memory buffer for authenticated user.
    """
    authentication_classes = [SarafJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Clear memory buffer for current saraf"""
        try:
            saraf_id = request.user.saraf_id
            if not saraf_id:
                return Response({'error': 'Saraf ID not found'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            memory_key = f"ai_memory_{saraf_id}"
            cache.delete(memory_key)
            logger.info(f"Memory cleared for saraf_id {saraf_id}")
            
            return Response({'message': 'Memory cleared successfully'})
            
        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}")
            return Response({'error': str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)