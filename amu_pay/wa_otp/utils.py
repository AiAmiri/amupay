"""
Utility functions for WhatsApp OTP handling
Specifically optimized for Afghanistan phone numbers via Twilio
"""

from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_whatsapp_otp(phone_number, otp_code):
    """
    Send OTP via WhatsApp using Twilio Content API
    
    This function handles Afghanistan phone numbers specifically:
    - Accepts: 0790976268 (10 digits starting with 07)
    - Converts to: +93790976268 (E.164 format without leading zero)
    - Sends via: whatsapp:+93790976268
    
    Args:
        phone_number (str): Phone number in E.164 format (+93XXXXXXXXX)
        otp_code (str): 4-digit OTP code
    
    Returns:
        tuple: (success: bool, message: str or error: str)
    """
    try:
        # Validate input
        if not phone_number:
            return False, "Phone number is required"
        
        if not otp_code:
            return False, "OTP code is required"
        
        # Ensure phone number is in correct format for Twilio
        # Should already be in E.164 format (+93XXXXXXXXX) from serializer
        if not phone_number.startswith('+93'):
            return False, f"Invalid Afghanistan phone format. Expected +93XXXXXXXXX, got: {phone_number}"
        
        # Initialize Twilio client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Create WhatsApp message using Content API
        message = client.messages.create(
            content_sid=settings.TWILIO_WHATSAPP_CONTENT_SID,
            from_='whatsapp:' + settings.TWILIO_WHATSAPP_FROM_NUMBER,
            content_variables='{"1": "' + otp_code + '"}',  # OTP code in template variable
            to='whatsapp:' + phone_number  # E.164 format: +93XXXXXXXXX
        )
        
        logger.info(f"WhatsApp OTP sent successfully to {phone_number}. Message SID: {message.sid}")
        return True, f"OTP sent successfully. SID: {message.sid}"
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send WhatsApp OTP to {phone_number}: {error_msg}")
        return False, f"Failed to send WhatsApp OTP: {error_msg}"


def validate_afghan_whatsapp_number(phone_number):
    """
    Validate if phone number is a valid Afghanistan WhatsApp number
    
    Args:
        phone_number (str): Phone number to validate
        
    Returns:
        tuple: (is_valid: bool, formatted_number: str or error: str)
    """
    import re
    
    # Remove spaces and formatting
    cleaned = re.sub(r'[\s\-\(\)]', '', str(phone_number).strip())
    
    # Check if already in E.164 format (+93XXXXXXXXX)
    if re.match(r'^\+93[7][0-9]{8}$', cleaned):
        return True, cleaned
    
    # Check if in local Afghan format (0790976268)
    if re.match(r'^0[7][0-9]{8}$', cleaned):
        # Convert to E.164 format
        formatted = '+93' + cleaned[1:]  # Remove 0 and add +93
        return True, formatted
    
    return False, "Invalid Afghanistan phone number format. Expected: 0790976268 or +93790976268"

