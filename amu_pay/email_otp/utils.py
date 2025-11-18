from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

def send_otp_email(email, otp_code):
    """
    Send OTP code to the specified email address
    """
    try:
        subject = 'Your OTP Code'
        
        # Create HTML message
        html_message = f"""
        <html>
        <body>
            <h2>Your OTP Code</h2>
            <p>Your One-Time Password (OTP) code is:</p>
            <h1 style="color: #007bff; font-size: 32px; letter-spacing: 5px;">{otp_code}</h1>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this code, please ignore this email.</p>
        </body>
        </html>
        """
        
        # Create plain text version
        plain_message = f"""
        Your OTP Code
        
        Your One-Time Password (OTP) code is: {otp_code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this code, please ignore this email.
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"OTP email sent successfully to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        return False
