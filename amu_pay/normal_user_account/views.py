from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from twilio.rest import Client
from django.utils import timezone
from datetime import timedelta
import logging

from .models import NormalUser, NormalUserOTP
from .serializers import (
    NormalUserRegistrationSerializer,
    NormalUserLoginSerializer,
    OTPVerificationSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ResendOTPSerializer,
    NormalUserProfileSerializer
)

logger = logging.getLogger(__name__)


def send_otp_email(email, otp_code):
    """Send OTP code to email"""
    try:
        subject = 'Your OTP Code - Amu Pay'
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h2 style="color: #333; text-align: center;">Your OTP Code</h2>
                <p style="color: #666; text-align: center;">Your One-Time Password (OTP) code is:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <h1 style="color: #007bff; font-size: 36px; letter-spacing: 8px; background-color: white; padding: 20px; border-radius: 8px; display: inline-block;">{otp_code}</h1>
                </div>
                <p style="color: #666; text-align: center;">This code will expire in 10 minutes.</p>
                <p style="color: #999; text-align: center; font-size: 14px;">If you didn't request this code, please ignore this email.</p>
            </div>
        </body>
        </html>
        """
        
        plain_message = f"""
        Your OTP Code - Amu Pay
        
        Your One-Time Password (OTP) code is: {otp_code}
        
        This code will expire in 10 minutes.
        
        If you didn't request this code, please ignore this email.
        """
        
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


def send_otp_whatsapp(phone_number, otp_code):
    """
    WhatsApp OTP sending is currently disabled (Twilio account deleted).
    
    NOTE: WhatsApp OTP functionality has been disconnected because the Twilio
    account was deleted. Users should register/verify using email instead.
    
    To re-enable WhatsApp OTP:
    1. Set up a new Twilio account
    2. Configure Twilio settings in .env file
    3. Uncomment the Twilio implementation code below
    """
    logger.warning(f"WhatsApp OTP requested for {phone_number} but Twilio is disabled")
    logger.info(f"OTP Code would have been: {otp_code} (for testing/manual verification)")
    
    # Return False to indicate WhatsApp OTP is not available
    return False
    
    # ORIGINAL TWILIO IMPLEMENTATION (DISABLED):
    # try:
    #     logger.info(f"Starting WhatsApp OTP send for: {phone_number}, OTP: {otp_code}")
    #     
    #     # Import validation function
    #     from utils.phone_validation import validate_and_format_phone_number
    #     
    #     # Ensure phone number is in E.164 format for Twilio
    #     # If already formatted, validate_and_format_phone_number will handle it
    #     try:
    #         formatted_phone = validate_and_format_phone_number(phone_number)
    #         logger.info(f"Phone number formatted: {phone_number} -> {formatted_phone}")
    #     except Exception as e:
    #         logger.error(f"Invalid phone number format: {phone_number} - {str(e)}")
    #         return False
    #     
    #     # Check if settings are configured
    #     if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
    #         logger.error("Twilio credentials not configured in settings")
    #         return False
    #     
    #     if not settings.TWILIO_WHATSAPP_CONTENT_SID or not settings.TWILIO_WHATSAPP_FROM_NUMBER:
    #         logger.error("Twilio WhatsApp settings not configured")
    #         return False
    #     
    #     # Initialize Twilio client
    #     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    #     logger.info(f"Twilio client initialized. From: whatsapp:{settings.TWILIO_WHATSAPP_FROM_NUMBER}")
    #     
    #     # Create WhatsApp message using Content API
    #     to_number = 'whatsapp:' + formatted_phone
    #     logger.info(f"Sending WhatsApp message to: {to_number}")
    #     
    #     message = client.messages.create(
    #         content_sid=settings.TWILIO_WHATSAPP_CONTENT_SID,
    #         from_='whatsapp:' + settings.TWILIO_WHATSAPP_FROM_NUMBER,
    #         content_variables='{"1": "' + otp_code + '"}',
    #         to=to_number
    #     )
    #     
    #     logger.info(f"WhatsApp OTP sent successfully to {formatted_phone}. Message SID: {message.sid}")
    #     return True
    # except Exception as e:
    #     logger.error(f"Failed to send WhatsApp OTP to {phone_number}: {str(e)}", exc_info=True)
    #     return False


class NormalUserRegistrationView(APIView):
    """Register a new normal user - Both email and WhatsApp required"""
    
    def post(self, request):
        serializer = NormalUserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # OTP is ALWAYS sent to email (WhatsApp is for profile only, no OTP)
            email = user.email
            otp_code = NormalUserOTP.generate_otp()
            expires_at = timezone.now() + timedelta(minutes=10)
            
            logger.info(f"Registration: Sending OTP to email: {email}, WhatsApp: {user.email_or_whatsapp}")
            
            # Send OTP to email
            if send_otp_email(email, otp_code):
                # Mark any previous unused OTPs as used
                NormalUserOTP.objects.filter(
                    user=user,
                    otp_type='email',
                    contact_info=email,
                    is_used=False
                ).update(is_used=True, used_at=timezone.now())
                
                NormalUserOTP.objects.create(
                    user=user,
                    otp_type='email',
                    contact_info=email,
                    otp_code=otp_code,
                    expires_at=expires_at
                )
                
                return Response({
                    'message': 'Registration successful. Please check your email for OTP verification.',
                    'user_id': user.user_id,
                    'email': user.email,
                    'email_or_whatsapp': user.email_or_whatsapp,
                    'requires_verification': True
                }, status=status.HTTP_201_CREATED)
            else:
                user.delete()  # Clean up if email sending fails
                return Response({
                    'error': 'Failed to send verification email. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """Verify OTP for normal user registration - Email only"""
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            otp = serializer.validated_data['otp']
            
            # Mark OTP as used
            otp.mark_as_used()
            
            # Update user verification status (Email only)
            user.is_email_verified = True
            
            # Activate the account after successful email verification
            if not user.is_active:
                user.is_active = True
            
            user.save()
            
            return Response({
                'message': 'Email verification successful! Your account is now active.',
                'user_id': user.user_id,
                'email': user.email,
                'email_or_whatsapp': user.email_or_whatsapp,
                'is_verified': user.is_verified(),
                'is_active': user.is_active
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NormalUserLoginView(APIView):
    """Login for normal users"""
    
    def post(self, request):
        serializer = NormalUserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Update last login
            user.update_last_login()
            
            # Generate JWT tokens manually
            from rest_framework_simplejwt.tokens import RefreshToken
            from django.contrib.auth.models import AnonymousUser
            
            # Create tokens manually with user data
            refresh = RefreshToken()
            access_token = refresh.access_token
            
            # Add user data to tokens
            refresh['user_id'] = user.user_id
            refresh['user_type'] = 'normal_user'
            refresh['full_name'] = user.full_name
            refresh['email'] = user.email
            refresh['email_or_whatsapp'] = user.email_or_whatsapp
            
            access_token['user_id'] = user.user_id
            access_token['user_type'] = 'normal_user'
            access_token['full_name'] = user.full_name
            access_token['email'] = user.email
            access_token['email_or_whatsapp'] = user.email_or_whatsapp
            
            return Response({
                'message': 'Login successful',
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'user': {
                    'user_id': user.user_id,
                    'full_name': user.full_name,
                    'email': user.email,
                    'email_or_whatsapp': user.email_or_whatsapp,
                    'is_email_verified': user.is_email_verified,
                    'is_whatsapp_verified': user.is_whatsapp_verified,
                    'is_verified': user.is_verified()
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordTokenGenerator(PasswordResetTokenGenerator):
    """Custom password reset token generator for NormalUser"""
    def _make_hash_value(self, user, timestamp):
        """
        Hash the user's primary key and some user state that's sure to change
        after a password reset to produce a token that's invalidated when it's used.
        """
        return str(user.user_id) + str(timestamp) + str(user.password_hash)


class ForgotPasswordView(APIView):
    """Request password reset OTP (Step 1) - Email only"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        
        if not email:
            return Response({
                'error': 'email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Find the NormalUser for this email
            user = NormalUser.objects.get(email=email)
        except NormalUser.DoesNotExist:
            # Do not reveal whether the account exists (security best practice)
            return Response({
                'message': 'If an account with that email exists, a reset OTP has been sent.'
            }, status=status.HTTP_200_OK)
        
        try:
            # Generate OTP
            otp_code = NormalUserOTP.generate_otp()
            expires_at = timezone.now() + timedelta(minutes=10)
            
            # Mark any previous unused password reset OTPs as used
            NormalUserOTP.objects.filter(
                user=user,
                otp_type='password_reset',
                contact_info=email,
                is_used=False
            ).update(is_used=True, used_at=timezone.now())
            
            # Create OTP record
            NormalUserOTP.objects.create(
                user=user,
                otp_type='password_reset',
                contact_info=email,
                otp_code=otp_code,
                expires_at=expires_at
            )
            
            # Send OTP via email
            otp_sent = send_otp_email(email, otp_code)
            if not otp_sent:
                return Response({
                    'error': 'Failed to send OTP email. Try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Store information in session for OTP verification
            request.session['reset_user_id'] = user.user_id
            request.session['reset_email'] = email
            request.session['reset_otp_type'] = 'email'
            
        except Exception as e:
            logger.error(f"Error in ForgotPasswordView: {str(e)}")
            return Response({
                'error': 'Failed to send OTP. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': 'OTP sent to your email for password reset verification.',
            'email': email,
            'otp_type': 'email'
        }, status=status.HTTP_200_OK)


class ForgotPasswordOTPVerifyView(APIView):
    """Verify password reset OTP and generate reset token (Step 2) - Email only"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        otp_code = request.data.get('otp_code', '').strip()
        
        if not email or not otp_code:
            return Response({
                'error': 'email and otp_code are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Find the NormalUser for this email
            user = NormalUser.objects.get(email=email)
        except NormalUser.DoesNotExist:
            return Response({
                'error': 'Invalid email address.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify OTP
            otp = NormalUserOTP.objects.filter(
                user=user,
                otp_type='password_reset',
                contact_info=email,
                otp_code=otp_code,
                is_used=False
            ).first()
            
            if not otp:
                return Response({
                    'error': 'Invalid OTP or email address.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if otp.is_expired():
                otp.mark_as_used()
                return Response({
                    'error': 'OTP expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as used
            otp.mark_as_used()
            
            # Generate password reset token for NormalUser
            token_generator = PasswordTokenGenerator()
            uidb64 = urlsafe_base64_encode(force_bytes(user.user_id))
            token = token_generator.make_token(user)
            
            # Store verification in session
            request.session['reset_otp_verified'] = True
            request.session['reset_user_id'] = user.user_id
            request.session['reset_email'] = email
            request.session['reset_otp_type'] = 'email'
            
            return Response({
                'message': 'OTP verified successfully. You can now reset your password.',
                'uidb64': uidb64,
                'token': token,
                'reset_path': f"reset-password-confirm/{uidb64}/{token}/"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in ForgotPasswordOTPVerifyView: {str(e)}")
            return Response({
                'error': 'Error verifying OTP. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordView(APIView):
    """Reset password using reset token (Step 3)"""
    permission_classes = [AllowAny]
    
    def post(self, request, uidb64, token):
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response({
                'error': 'new_password is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Decode user ID from uidb64
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = NormalUser.objects.get(user_id=user_id)
        except Exception:
            return Response({
                'error': 'Invalid reset link.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify token
        token_generator = PasswordTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response({
                'error': 'Invalid or expired token.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Update password
            user.set_password(new_password)
            
            return Response({
                'message': 'Password has been reset successfully. You can now login with your new password.'
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response({
                'error': 'Password validation failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(APIView):
    """Resend OTP for verification - Email only"""
    
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            otp_type = serializer.validated_data['otp_type']
            email = user.email
            
            # Generate new OTP
            otp_code = NormalUserOTP.generate_otp()
            expires_at = timezone.now() + timedelta(minutes=10)
            
            # Mark all previous unused OTPs as used to prevent confusion
            NormalUserOTP.objects.filter(
                user=user,
                otp_type=otp_type,
                contact_info=email,
                is_used=False
            ).update(is_used=True, used_at=timezone.now())
            
            # Create new OTP record
            NormalUserOTP.objects.create(
                user=user,
                otp_type=otp_type,
                contact_info=email,
                otp_code=otp_code,
                expires_at=expires_at
            )
            
            # Send OTP to email
            if send_otp_email(email, otp_code):
                return Response({
                    'message': 'New OTP sent to your email. Please check your inbox.',
                    'email': email
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Failed to send OTP email. Please try again.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NormalUserLogoutView(APIView):
    """Logout for normal users with JWT token handling"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Logout normal user and handle JWT token"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Get the authenticated user
            user = request.user
            
            # Check if user is authenticated (works with CustomUser from JWT auth)
            if not user or not hasattr(user, 'is_authenticated') or not user.is_authenticated:
                return Response({'error': 'User not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)

            # For JWT-based authentication, we can't invalidate the token on the server side
            # without implementing a token blacklist. Instead, we:
            # 1. Return a success response indicating logout
            # 2. The client should discard the token
            # 3. Optionally, we can log the logout event
            
            # Log the logout event (optional)
            logger.info(f"Normal user logout: {getattr(user, 'user_id', 'unknown')} - {getattr(user, 'full_name', 'unknown')}")

            return Response({
                'message': 'Successfully logged out. Please discard your token on the client side.',
                'user_id': getattr(user, 'user_id', None),
                'logout_timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'error': 'Logout failed',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NormalUserProfileView(APIView):
    """Get normal user profile"""
    
    def get(self, request):
        # This would need authentication middleware to get user from JWT
        # For now, we'll assume user is passed in request
        user_id = request.data.get('user_id')
        
        try:
            user = NormalUser.objects.get(user_id=user_id)
            serializer = NormalUserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NormalUser.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
