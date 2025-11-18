from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_sms_otp(phone_number, otp_code):
    """
    Send OTP via SMS using Twilio
    
    Args:
        phone_number (str): Phone number in E.164 format
        otp_code (str): 6-digit OTP code
    
    Returns:
        bool: True if SMS sent successfully, False otherwise
    """
    try:
        # Initialize Twilio client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Create SMS message
        message_body = f"Your OTP code is: {otp_code}. This code will expire in 10 minutes. Do not share this code with anyone."
        
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        logger.info(f"SMS sent successfully to {phone_number}. Message SID: {message.sid}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
        return False
