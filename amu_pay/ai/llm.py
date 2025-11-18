"""
LLM module for Google Generative AI integration
Includes workaround for known finish_reason enum bug
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Apply the workaround immediately when module is imported
# This ensures the patch is active before any model is created
_PATCH_APPLIED = False

# Workaround for langchain-google-genai finish_reason bug
# Patch the _response_to_result function to handle integer finish_reason
def _patch_finish_reason_bug():
    """
    Monkey-patch langchain_google_genai to handle finish_reason as integer.
    This fixes the bug where finish_reason is 10 (int) instead of enum.
    """
    try:
        import langchain_google_genai.chat_models as chat_models_module
        import functools
        
        # Get the original function
        if not hasattr(chat_models_module, '_response_to_result'):
            logger.warning("_response_to_result not found in langchain_google_genai.chat_models")
            return
        
        original_response_to_result = chat_models_module._response_to_result
        
        @functools.wraps(original_response_to_result)
        def patched_response_to_result(response, *args, **kwargs):
            try:
                return original_response_to_result(response, *args, **kwargs)
            except AttributeError as e:
                error_str = str(e)
                if "'int' object has no attribute 'name'" in error_str or "finish_reason" in error_str.lower():
                    # This is the bug - finish_reason is an int, not an enum
                    logger.warning("Detected finish_reason enum bug, applying workaround")
                    
                    # Manually construct the result
                    from langchain_core.outputs import ChatGeneration, ChatResult
                    from langchain_core.messages import AIMessage
                    
                    # Extract the response content
                    if hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        content = ""
                        
                        # Try multiple ways to extract content
                        if hasattr(candidate, 'content'):
                            if hasattr(candidate.content, 'parts'):
                                # Extract text from all parts
                                parts_text = []
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        parts_text.append(part.text)
                                    elif hasattr(part, 'text'):
                                        parts_text.append(str(part.text))
                                content = "".join(parts_text)
                            elif hasattr(candidate.content, 'text'):
                                content = candidate.content.text
                        
                        # Fallback: try to get text directly from candidate
                        if not content and hasattr(candidate, 'text'):
                            content = candidate.text
                        
                        # Log if content is empty
                        if not content:
                            logger.warning(f"Could not extract content from response. Candidate attributes: {dir(candidate)}")
                        else:
                            logger.info(f"Extracted content length: {len(content)} characters")
                        
                        # Create message and generation
                        message = AIMessage(content=content)
                        generation = ChatGeneration(message=message)
                        
                        # Handle finish_reason - convert int to string if needed
                        finish_reason_str = "STOP"
                        if hasattr(candidate, 'finish_reason'):
                            fr = candidate.finish_reason
                            if isinstance(fr, int):
                                # Map common finish reason integers to strings
                                finish_reason_map = {
                                    1: "STOP",
                                    2: "MAX_TOKENS", 
                                    3: "SAFETY",
                                    4: "RECITATION",
                                    10: "OTHER"  # Unknown reason (the bug case)
                                }
                                finish_reason_str = finish_reason_map.get(fr, "OTHER")
                                logger.info(f"Mapped finish_reason integer {fr} to {finish_reason_str}")
                            elif hasattr(fr, 'name'):
                                finish_reason_str = fr.name
                            else:
                                finish_reason_str = str(fr)
                        
                        generation.generation_info = {"finish_reason": finish_reason_str}
                        return ChatResult(generations=[generation])
                    
                    # If we can't extract content, re-raise the original error
                    raise
                # Not our bug, re-raise
                raise
        
        # Apply the patch
        chat_models_module._response_to_result = patched_response_to_result
        global _PATCH_APPLIED
        _PATCH_APPLIED = True
        logger.info("✅ Applied workaround for langchain-google-genai finish_reason bug")
        return True
        
    except ImportError as e:
        logger.warning(f"Could not import langchain_google_genai.chat_models: {str(e)}")
        return False
    except Exception as e:
        logger.warning(f"Could not apply finish_reason bug workaround: {str(e)}")
        return False

# Apply patch immediately on module import
_patch_finish_reason_bug()


def get_google_model(model="gemini-2.5-flash"):
    """
    Get Google Generative AI model instance.
    
    Note: There's a known bug in langchain-google-genai where finish_reason
    can be an integer (10) instead of an enum, causing AttributeError.
    This is handled with a monkey-patch workaround applied at module import.
    
    Args:
        model: Model name to use
        
    Returns:
        ChatGoogleGenerativeAI instance
    """
    # Patch is already applied at module import time
    if not _PATCH_APPLIED:
        logger.warning("Finish reason bug patch was not applied, attempting to apply now...")
        _patch_finish_reason_bug()
    
    api_key_from_settings = settings.GEMINI_API_KEY 
    if not api_key_from_settings:
        logger.error("GEMINI_API_KEY not found in Django settings!")
        raise ValueError("GEMINI_API_KEY is required")
    
    if api_key_from_settings == 'your_gemini_api_key_here':
        logger.error("GEMINI_API_KEY is set to placeholder value!")
        raise ValueError("Please set a valid GEMINI_API_KEY in your .env file")
    
    try:
        model_instance = ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=api_key_from_settings 
        )
        logger.info(f"Google GenAI model initialized: {model}")
        return model_instance
    except Exception as e:
        logger.error(f"Error initializing Google GenAI model: {str(e)}")
        raise