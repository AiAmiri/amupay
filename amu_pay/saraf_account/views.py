
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import json
import base64

from email_otp.models import EmailOTP
from email_otp.utils import send_otp_email
from .models import SarafAccount, SarafEmployee, SarafOTP, DEFAULT_EMPLOYEE_PERMISSIONS, PERMISSION_DESCRIPTIONS
from .serializers import (
    SarafRegistrationSerializer, SarafLoginSerializer, SarafOTPVerificationSerializer,
    SarafForgotPasswordSerializer, SarafResetPasswordSerializer, SarafResendOTPSerializer,
    SarafProfileSerializer, SarafPictureUpdateSerializer, SarafPictureDeleteSerializer,
    SarafPictureListSerializer
)
import logging

logger = logging.getLogger(__name__)

def send_otp_email_saraf(email, otp_code):
    """Send OTP email for Saraf account"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = 'Saraf Account Verification Code'
        message = f'''
        Your verification code for Saraf account is: {otp_code}
        
        This code will expire in 10 minutes.
        
        If you did not request this code, please ignore this email.
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error sending email OTP: {str(e)}")
        return False

def send_otp_whatsapp_saraf(phone_number, otp_code):
    """Send OTP via WhatsApp for Saraf account"""
    try:
        from twilio.rest import Client
        from django.conf import settings
        import re
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Clean and validate phone number format - Afghanistan focused
        cleaned_number = re.sub(r'[\s\-\(\)]', '', phone_number)
        
        # Check if it's Afghan local format (starts with 0 and 10 digits total)
        if re.match(r'^0[7][0-9]{8}$', cleaned_number):
            # Convert to E.164 format for Afghanistan (+93)
            formatted_phone = '+93' + cleaned_number[1:]
        elif re.match(r'^\+93[7][0-9]{8}$', cleaned_number):
            # Already in Afghan international format
            formatted_phone = cleaned_number
        elif re.match(r'^\+[1-9]\d{6,14}$', cleaned_number):
            # Valid international format
            formatted_phone = cleaned_number
        elif re.match(r'^[1-9]\d{6,14}$', cleaned_number):
            # Add + if missing
            formatted_phone = '+' + cleaned_number
        else:
            logger.error(f"Invalid phone number format: {phone_number}")
            return False
        
        # Use WhatsApp template with content_sid and content_variables (like wa_otp app)
        client.messages.create(
            content_sid=settings.TWILIO_WHATSAPP_CONTENT_SID,
            from_='whatsapp:' + settings.TWILIO_WHATSAPP_FROM_NUMBER,
            content_variables='{"1": "' + otp_code + '"}',
            to='whatsapp:' + formatted_phone
        )
        return True
    except Exception as e:
        logger.error(f"Error sending WhatsApp OTP: {str(e)}")
        return False

def get_user_info_from_token(request):
    """Helper function to extract user info from JWT token"""
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        
        # Get the raw token string
        token_string = str(request.auth)
        
        # Create AccessToken object
        token = AccessToken(token_string)
        
        user_info = {
            'saraf_id': token.get('saraf_id'),
            'employee_id': token.get('employee_id'),
            'user_type': token.get('user_type'),
            'user_id': token.get('user_id')
        }
        
        return user_info
    except Exception as e:
        logger.error(f"Error extracting user info from token: {str(e)}")
        return None


def build_absolute_uri(request, file_field):
    """Helper function to build absolute URI for file fields"""
    if file_field:
        return request.build_absolute_uri(file_field.url)
    return None

# Create your views here.


class PasswordTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, saraf, timestamp):
        """
        Hash the saraf's primary key and some saraf state that's sure to change
        after a password reset to produce a token that invalidated when it's used.
        """
        return str(saraf.saraf_id) + str(timestamp) + str(saraf.password_hash)


class SarafAccountRegisterView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        # Collect JSON or multipart form-data fields
        full_name = (request.data.get('full_name') or '').strip()
        exchange_name = (request.data.get('exchange_name') or '').strip() or None
        email = (request.data.get('email') or '').strip()
        email_or_whatsapp_number = (request.data.get('email_or_whatsapp_number') or '').strip()
        
        license_no = (request.data.get('license_no') or '').strip()
        amu_pay_code = (request.data.get('amu_pay_code') or '').strip()
        saraf_address = (request.data.get('saraf_address') or '').strip()
        saraf_location_google_map = (request.data.get('saraf_location_google_map') or '').strip()
        province = (request.data.get('province') or '').strip()
        password = request.data.get('password')
        # file inputs should be in request.FILES when multipart
        saraf_logo = request.FILES.get('saraf_logo')
        saraf_logo_wallpeper = request.FILES.get('saraf_logo_wallpeper')
        front_id_card = request.FILES.get('front_id_card')
        back_id_card = request.FILES.get('back_id_card')
        # optional
        is_active_raw = request.data.get('is_active')

        # Basic required fields validation - BOTH email AND email_or_whatsapp_number now required
        missing = []
        for key, val in {
            'full_name': full_name,
            'email': email,
            'email_or_whatsapp_number': email_or_whatsapp_number,
            'amu_pay_code': amu_pay_code,
            'province': province,
            'password': password,
        }.items():
            if not val:
                missing.append(key)
        if missing:
            return Response({'error': f"Missing required fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate email format
        from django.core.validators import validate_email
        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate email_or_whatsapp_number is NOT an email (should be WhatsApp only)
        if '@' in email_or_whatsapp_number:
            return Response({'error': 'email_or_whatsapp_number should contain a WhatsApp number only. Use the email field for email addresses.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate WhatsApp number format
        import re
        if not re.match(r'^0\d{9}$', email_or_whatsapp_number):
            return Response({'error': 'WhatsApp number must be 10 digits and start with 0'}, status=status.HTTP_400_BAD_REQUEST)

        # Enhanced uniqueness checks - ensure no duplicate accounts
        if SarafAccount.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if SarafAccount.objects.filter(email_or_whatsapp_number=email_or_whatsapp_number).exists():
            return Response({'error': 'WhatsApp number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # License number uniqueness check (only if provided)
        if license_no and SarafAccount.objects.filter(license_no=license_no).exists():
            return Response({'error': 'License number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate password strength before proceeding
        try:
            # Create a temporary SarafAccount object to validate password
            temp_saraf = SarafAccount(
                full_name=full_name,
                email=email,
                email_or_whatsapp_number=email_or_whatsapp_number,
                amu_pay_code=amu_pay_code,
                province=province,
            )
            temp_saraf.set_password(password)
        except ValidationError as ve:
            return Response({'error': 'Validation error', 'details': ve.message_dict if hasattr(ve, 'message_dict') else ve.messages}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP code
        import random
        otp_code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)
        
        # Store registration data in cache (NOT in database yet)
        # Cache key: saraf_registration_{email}
        registration_data = {
            'full_name': full_name,
            'exchange_name': exchange_name,
            'email': email,
            'email_or_whatsapp_number': email_or_whatsapp_number,
            'license_no': license_no,
            'amu_pay_code': amu_pay_code,
            'saraf_address': saraf_address,
            'saraf_location_google_map': saraf_location_google_map,
            'province': province,
            'password_hash': temp_saraf.password_hash,  # Store hashed password
            'is_active': str(is_active_raw).lower() in ['1', 'true', 'yes'] if is_active_raw is not None else False,
            'otp_code': otp_code,
            'otp_expires_at': expires_at.isoformat(),
            'created_at': timezone.now().isoformat(),
        }
        
        # Handle file uploads - store file paths temporarily
        # For files, we'll need to save them temporarily and move them after verification
        file_data = {}
        if saraf_logo:
            # Save file temporarily
            import os
            from django.core.files.storage import default_storage
            temp_path = f'temp_registrations/saraf_logo_{email}_{timezone.now().timestamp()}.{saraf_logo.name.split(".")[-1]}'
            file_data['saraf_logo'] = default_storage.save(temp_path, saraf_logo)
        if saraf_logo_wallpeper:
            temp_path = f'temp_registrations/saraf_logo_wallpeper_{email}_{timezone.now().timestamp()}.{saraf_logo_wallpeper.name.split(".")[-1]}'
            file_data['saraf_logo_wallpeper'] = default_storage.save(temp_path, saraf_logo_wallpeper)
        if front_id_card:
            temp_path = f'temp_registrations/front_id_card_{email}_{timezone.now().timestamp()}.{front_id_card.name.split(".")[-1]}'
            file_data['front_id_card'] = default_storage.save(temp_path, front_id_card)
        if back_id_card:
            temp_path = f'temp_registrations/back_id_card_{email}_{timezone.now().timestamp()}.{back_id_card.name.split(".")[-1]}'
            file_data['back_id_card'] = default_storage.save(temp_path, back_id_card)
        
        registration_data.update(file_data)
        
        # Store in cache for 15 minutes (longer than OTP expiration)
        cache_key = f'saraf_registration_{email.lower()}'
        cache.set(cache_key, registration_data, 15 * 60)  # 15 minutes
        
        # Send OTP to email
        try:
            send_otp_email_saraf(email, otp_code)
            otp_message = " Please check your email for OTP verification."
        except Exception as e:
            logger.error(f"Failed to send OTP email: {str(e)}")
            # Clean up cache if email sending fails
            cache.delete(cache_key)
            return Response({
                'error': 'Failed to send verification email. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': f'Registration data received.{otp_message}',
            'email': email,
            'otp_sent': True,
            'requires_verification': True,
            'message_note': 'Your account will be created after OTP verification.'
        }, status=status.HTTP_200_OK)


class SarafAccountProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_info = {
            'user_id': request.user.user_id,
            'user_type': request.user.user_type,
            'full_name': request.user.full_name,
            'email': request.user.email,
            'saraf_id': request.user.saraf_id,
        }
        if hasattr(request.user, 'employee_id') and request.user.employee_id:
            user_info['employee_id'] = request.user.employee_id
            
        return Response({
            'message': f'Hello, {request.user.full_name}! This is a protected view.',
            'user_info': user_info
        })


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'error': 'old_password and new_password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return Response({'error': 'Invalid user token'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            if user_info['user_type'] == 'saraf':
                # Change password for Saraf account
                saraf = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
                if not saraf.check_password(old_password):
                    return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
                
                if len(new_password) < 6:
                    return Response({'error': 'New password must be at least 6 characters.'}, status=status.HTTP_400_BAD_REQUEST)
                
                saraf.set_password(new_password)
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
                
            elif user_info['user_type'] == 'employee':
                # Change password for Employee account
                employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                if not employee.check_password(old_password):
                    return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
                
                if len(new_password) < 6:
                    return Response({'error': 'New password must be at least 6 characters.'}, status=status.HTTP_400_BAD_REQUEST)
                
                employee.set_password(new_password)
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
                
        except (SarafAccount.DoesNotExist, SarafEmployee.DoesNotExist):
            return Response({'error': 'User account not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return Response({'error': 'Failed to change password.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangeEmployeePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, employee_id):
        """Allow saraf to change employee password without requiring current password"""
        import re
        
        new_password = request.data.get('new_password')
        repeat_password = request.data.get('repeat_password')

        # Validate required fields
        if not new_password or not repeat_password:
            return Response({
                'error': 'new_password and repeat_password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate password match
        if new_password != repeat_password:
            return Response({
                'error': 'Passwords do not match.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return Response({'error': 'Invalid user token'}, status=status.HTTP_401_UNAUTHORIZED)

        # Only Saraf owners can change employee passwords
        if user_info['user_type'] != 'saraf':
            return Response({
                'error': 'Only Saraf owners can change employee passwords.'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            # Get the employee
            employee = SarafEmployee.objects.get(employee_id=employee_id)
            
            # Ensure the employee belongs to the authenticated Saraf
            if employee.saraf_account.saraf_id != user_info['saraf_id']:
                return Response({
                    'error': 'You can only change passwords for your own employees.'
                }, status=status.HTTP_403_FORBIDDEN)

            # Validate password strength
            if len(new_password) < 6:
                return Response({
                    'error': 'New password must be at least 6 characters.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Additional password strength validation (optional - based on your existing validation)
            if not re.search(r'[A-Z]', new_password):
                return Response({
                    'error': 'Password must contain at least one uppercase letter.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not re.search(r'[a-z]', new_password):
                return Response({
                    'error': 'Password must contain at least one lowercase letter.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not re.search(r'\d', new_password):
                return Response({
                    'error': 'Password must contain at least one digit.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                return Response({
                    'error': 'Password must contain at least one special character.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Set new password
            employee.set_password(new_password)
            employee.save()  # Save the employee after setting password
            
            return Response({
                'message': 'Employee password changed successfully.',
                'employee': {
                    'employee_id': employee.employee_id,
                    'username': employee.username,
                    'full_name': employee.full_name
                }
            }, status=status.HTTP_200_OK)

        except SarafEmployee.DoesNotExist:
            return Response({
                'error': 'Employee not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({
                'error': 'Password validation failed.',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error changing employee password: {str(e)}")
            return Response({
                'error': 'Failed to change employee password.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get('password')
        if not password:
            return Response({'error': 'Password is required to delete account.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info or not user_info.get('saraf_id'):
            return Response({'error': 'Invalid user token'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            saraf = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
            if not saraf.check_password(password):
                return Response({'error': 'Password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

            saraf_name = saraf.full_name
            saraf.delete()
            return Response({'message': f'Account {saraf_name} deleted successfully.'}, status=status.HTTP_200_OK)
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found.'}, status=status.HTTP_404_NOT_FOUND)


class ForgotPasswordRequestView(APIView):
    """Request password reset OTP - Email only"""
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        
        if not email:
            return Response({'error': 'email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the SarafAccount for this email
            saraf = SarafAccount.objects.get(email=email)
        except SarafAccount.DoesNotExist:
            # Do not reveal whether the account exists (security best practice)
            return Response({'message': 'If an account with that email exists, a reset OTP has been sent.'}, status=status.HTTP_200_OK)

        # Send OTP for password reset verification - ALWAYS to email
        contact_info = saraf.email
        otp_type = 'email'

        try:
            # Generate OTP using SarafOTP model
            otp = SarafOTP.generate_otp(saraf, 'password_reset', contact_info)

            # Send OTP to email
            otp_sent = send_otp_email_saraf(contact_info, otp.otp_code)
            if not otp_sent:
                return Response({'error': 'Failed to send OTP email. Try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Store the saraf ID and email in session for OTP verification
            request.session['reset_saraf_id'] = saraf.saraf_id
            request.session['reset_email'] = email
            request.session['reset_otp_type'] = 'email'

        except Exception as e:
            logger.error(f"Error in ForgotPasswordRequestView: {str(e)}")
            return Response({'error': 'Failed to send OTP. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'message': 'OTP sent to your email for password reset verification.',
            'email': email,
            'otp_type': 'email'
        }, status=status.HTTP_200_OK)


class ForgotPasswordOTPVerifyView(APIView):
    """Verify password reset OTP - Email only"""
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        otp_code = request.data.get('otp_code')

        if not email or not otp_code:
            return Response({'error': 'email and otp_code are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the SarafAccount for this email
            saraf = SarafAccount.objects.get(email=email)
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Invalid OTP or email address.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP using SarafOTP model
        try:
            otp = SarafOTP.verify_otp(saraf, 'password_reset', email, otp_code)
            
            if not otp:
                return Response({'error': 'Invalid OTP or email address.'}, status=status.HTTP_400_BAD_REQUEST)

            if otp.is_expired():
                otp.mark_as_used()
                return Response({'error': 'OTP expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

            # Mark OTP as used
            otp.mark_as_used()

            # Generate password reset token for SarafAccount
            token_generator = PasswordTokenGenerator()
            uidb64 = urlsafe_base64_encode(force_bytes(saraf.saraf_id))
            token = token_generator.make_token(saraf)

            # Store verification in session
            request.session['reset_otp_verified'] = True
            request.session['reset_saraf_id'] = saraf.saraf_id
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
            return Response({'error': 'Error verifying OTP. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({'error': 'new_password is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            saraf_id = force_str(urlsafe_base64_decode(uidb64))
            saraf = SarafAccount.objects.get(saraf_id=saraf_id)
        except Exception:
            return Response({'error': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordTokenGenerator()
        if not token_generator.check_token(saraf, token):
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            saraf.set_password(new_password)
            return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'error': 'Password validation failed', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SarafEmailOTPRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # Explicitly disable authentication for this endpoint

    def post(self, request):
        # Get email from request data
        email = request.data.get('email')

        if not email:
            return Response({'error': 'email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        email = email.lower()

        # Remove existing OTP for this email to avoid duplicates
        EmailOTP.objects.filter(email=email).delete()

        email_otp = EmailOTP.objects.create(email=email)
        sent = send_otp_email(email, email_otp.otp_code)
        if not sent:
            email_otp.delete()
            return Response({'error': 'Failed to send OTP email. Try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'OTP sent to email.', 'email': email}, status=status.HTTP_200_OK)


class SarafEmailOTPVerifyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # Explicitly disable authentication for this endpoint
    
    @transaction.atomic
    def post(self, request):
        email = (request.data.get('email') or '').lower()
        otp_code = request.data.get('otp_code')

        if not email or not otp_code:
            return Response({'error': 'email and otp_code are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            email_otp = EmailOTP.objects.get(email=email, otp_code=otp_code)
        except EmailOTP.DoesNotExist:
            return Response({'error': 'Invalid OTP or email.'}, status=status.HTTP_400_BAD_REQUEST)

        if email_otp.is_expired():
            email_otp.delete()
            return Response({'error': 'OTP expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

        # Mark OTP/email as active
        email_otp.is_active = True
        email_otp.save(update_fields=['is_active'])

        # Generate password reset token for SarafAccount
        try:
            saraf = SarafAccount.objects.get(email=email)
            
            token_generator = PasswordTokenGenerator()
            uidb64 = urlsafe_base64_encode(force_bytes(saraf.saraf_id))
            token = token_generator.make_token(saraf)

            # Store verification in session
            request.session['reset_otp_verified'] = True
            request.session['reset_saraf_id'] = saraf.saraf_id
            request.session['reset_email'] = email

            # Activate the SarafAccount if needed
            if not saraf.is_active:
                saraf.is_active = True
                saraf.save(update_fields=['is_active'])

            return Response({
                'message': 'OTP verified successfully. You can now reset your password.',
                'uidb64': uidb64,
                'token': token,
                'reset_path': f"reset-password-confirm/{uidb64}/{token}/"
            }, status=status.HTTP_200_OK)

        except SarafAccount.DoesNotExist:
            return Response({'error': 'No saraf account found for this email.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error generating reset token.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SarafLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Simple logout - just verify user is authenticated and return success
        # JWT tokens are stateless and will expire naturally based on their expiry time
        user = request.user

        if not user or not user.is_authenticated:
            return Response({'error': 'User not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Optional: Clear any session data if using sessions
        if hasattr(request, 'session'):
            request.session.flush()

        return Response({
            'message': 'Successfully logged out.',
            'user': user.username
        }, status=status.HTTP_200_OK)


class SarafLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Unified login for both saraf owners and employees
        email_or_whatsapp_number = (request.data.get('email_or_whatsapp_number') or '').strip()
        username = (request.data.get('username') or '').strip()  # For employee login
        password = request.data.get('password')

        if not email_or_whatsapp_number or not password:
            return Response({'error': 'email_or_whatsapp_number and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Find the saraf account first - check both email and email_or_whatsapp_number fields (like normal user login)
        try:
            if '@' in email_or_whatsapp_number:
                # If it's an email, check the email field
                saraf = SarafAccount.objects.get(email=email_or_whatsapp_number.lower())
            else:
                # If it's a WhatsApp number, check the email_or_whatsapp_number field
                saraf = SarafAccount.objects.get(email_or_whatsapp_number=email_or_whatsapp_number)
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if this is employee login (username provided) or saraf owner login
        if username:
            # Employee login: email_or_whatsapp_number + username + password
            try:
                employee = SarafEmployee.objects.get(
                    saraf_account=saraf,
                    username=username,
                    is_active=True
                )
                
                # Check employee password
                if not employee.check_password(password):
                    return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

                # Update last login
                from django.utils import timezone
                employee.last_login = timezone.now()
                employee.save(update_fields=['last_login'])

                # Create custom JWT token with employee claims
                refresh = RefreshToken()
                refresh['user_type'] = 'employee'
                refresh['user_id'] = employee.employee_id
                refresh['saraf_id'] = saraf.saraf_id
                refresh['employee_id'] = employee.employee_id
                refresh['full_name'] = employee.full_name
                refresh['email_or_whatsapp_number'] = saraf.email_or_whatsapp_number
                
                # Also set claims on the access token
                access_token = refresh.access_token
                access_token['user_type'] = 'employee'
                access_token['user_id'] = employee.employee_id
                access_token['saraf_id'] = saraf.saraf_id
                access_token['employee_id'] = employee.employee_id
                access_token['full_name'] = employee.full_name
                access_token['email_or_whatsapp_number'] = saraf.email_or_whatsapp_number
                
                return Response({
                    'message': 'Login successful (Employee)',
                    'user_type': 'employee',
                    'user_id': employee.employee_id,
                    'username': employee.username,
                    'full_name': employee.full_name,
                    'saraf_id': saraf.saraf_id,
                    'saraf_name': saraf.full_name,
                    'employee_id': employee.employee_id,
                    'employee_name': employee.full_name,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }, status=status.HTTP_200_OK)

            except SarafEmployee.DoesNotExist:
                return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            # Saraf owner login: email_or_whatsapp_number + password
            # Check saraf password
            if not saraf.check_password(password):
                return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

            # Check if saraf account is active
            if not saraf.is_active:
                return Response({'error': 'Account is not active. Please verify your contact information first.'}, status=status.HTTP_403_FORBIDDEN)

            # Create custom JWT token with saraf claims
            refresh = RefreshToken()
            refresh['user_type'] = 'saraf'
            refresh['user_id'] = saraf.saraf_id
            refresh['saraf_id'] = saraf.saraf_id
            refresh['full_name'] = saraf.full_name
            refresh['exchange_name'] = saraf.exchange_name
            refresh['email_or_whatsapp_number'] = saraf.email_or_whatsapp_number
            
            # Also set claims on the access token
            access_token = refresh.access_token
            access_token['user_type'] = 'saraf'
            access_token['user_id'] = saraf.saraf_id
            access_token['saraf_id'] = saraf.saraf_id
            access_token['full_name'] = saraf.full_name
            access_token['exchange_name'] = saraf.exchange_name
            access_token['email_or_whatsapp_number'] = saraf.email_or_whatsapp_number

            return Response({
                'message': 'Login successful',
                'user_type': 'saraf',
                'user_id': saraf.saraf_id,
                'full_name': saraf.full_name,
                'exchange_name': saraf.exchange_name,
                'email_or_whatsapp_number': saraf.email_or_whatsapp_number,
                'is_verified': saraf.is_verified(),
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)


class SarafListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """List all registered Saraf accounts with basic information"""
        try:
            # Get all active Saraf accounts
            saraf_accounts = SarafAccount.objects.filter(is_active=True).order_by('exchange_name')
            
            # Use serializer for consistent data structure
            from .serializers import SarafListSerializer
            serializer = SarafListSerializer(saraf_accounts, many=True, context={'request': request})
            
            return Response({
                'message': 'List of registered Saraf accounts',
                'count': len(serializer.data),
                'saraf_accounts': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching Saraf list: {str(e)}")
            return Response({
                'error': 'Failed to fetch Saraf accounts',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetEmployeesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Get email or WhatsApp number from query parameter (public access)
        # Support both 'email' and 'whatsapp_number' parameters for compatibility
        email_or_whatsapp = request.query_params.get('email') or request.query_params.get('whatsapp_number')
        
        if not email_or_whatsapp:
            return Response({
                'error': 'email or whatsapp_number parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find saraf account by email or WhatsApp (like login)
        try:
            if '@' in email_or_whatsapp:
                # If it's an email, check the email field
                saraf = SarafAccount.objects.get(email=email_or_whatsapp.lower())
            else:
                # If it's a WhatsApp number, check the email_or_whatsapp_number field
                saraf = SarafAccount.objects.get(email_or_whatsapp_number=email_or_whatsapp)
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get active employees for this saraf account
        employees = SarafEmployee.objects.filter(
            saraf_account=saraf,
            is_active=True
        ).values('employee_id', 'username', 'full_name').order_by('full_name')

        return Response({
            'saraf_name': saraf.full_name,
            'saraf_id': saraf.saraf_id,
            'whatsapp_number': saraf.email_or_whatsapp_number,
            'exchange_name': saraf.exchange_name,
            'employees': list(employees)
        }, status=status.HTTP_200_OK)


class EmployeeManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List all employees for a saraf account"""
        # Get saraf account from authenticated user
        user_info = get_user_info_from_token(request)
        if not user_info or not user_info.get('saraf_id'):
            return Response({
                'error': 'Invalid user information'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = user_info['saraf_id']
        try:
            saraf = SarafAccount.objects.get(saraf_id=saraf_id)
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get all employees for this saraf account
        employees = SarafEmployee.objects.filter(saraf_account=saraf).order_by('full_name')
        
        employee_data = []
        for emp in employees:
            employee_data.append({
                'employee_id': emp.employee_id,
                'username': emp.username,
                'full_name': emp.full_name,
                'is_active': emp.is_active,
                'created_at': emp.created_at.isoformat(),
                'updated_at': emp.updated_at.isoformat(),
                'last_login': emp.last_login.isoformat() if emp.last_login else None
            })

        return Response({
            'saraf_name': saraf.full_name,
            'saraf_id': saraf.saraf_id,
            'employees': employee_data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new employee"""
        # Get saraf account from authenticated user
        user_info = get_user_info_from_token(request)
        if not user_info or not user_info.get('saraf_id'):
            return Response({
                'error': 'Invalid user information'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = user_info['saraf_id']
        try:
            saraf = SarafAccount.objects.get(saraf_id=saraf_id)
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get employee data from request
        full_name = request.data.get('full_name', '').strip()
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not all([full_name, password]):
            return Response({
                'error': 'full_name and password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use provided username or generate one from full_name
            if username:
                # Validate provided username
                if len(username) < 3:
                    return Response({
                        'error': 'Username must be at least 3 characters long.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if username already exists for this saraf
                if SarafEmployee.objects.filter(saraf_account=saraf, username=username).exists():
                    return Response({
                        'error': f'Username "{username}" already exists for this saraf account.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Generate unique username based on full_name if not provided
                base_username = full_name.lower().replace(' ', '_')
                username = base_username
                counter = 1
                
                # Ensure username is unique for this saraf
                while SarafEmployee.objects.filter(saraf_account=saraf, username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1

            # Create new employee
            employee = SarafEmployee(
                saraf_account=saraf,
                username=username,
                full_name=full_name
            )
            employee.set_password(password)
            employee.save()

            return Response({
                'message': 'Employee created successfully.',
                'employee': {
                    'employee_id': employee.employee_id,
                    'username': employee.username,
                    'full_name': employee.full_name,
                    'is_active': employee.is_active,
                    'created_at': employee.created_at.isoformat()
                }
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({
                'error': 'Validation error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Failed to create employee',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployeeMyPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get logged-in employee's own permissions"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return Response({'error': 'Invalid user token'}, status=status.HTTP_401_UNAUTHORIZED)

        # Only employees can access their own permissions
        if user_info['user_type'] != 'employee':
            return Response({'error': 'Only employees can access their own permissions.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            # Get the employee
            employee = SarafEmployee.objects.select_related('saraf_account').get(
                employee_id=user_info['employee_id']
            )
            
            # Ensure permissions are initialized (in case they're empty dict)
            if not employee.permissions or len(employee.permissions) == 0:
                employee.permissions = DEFAULT_EMPLOYEE_PERMISSIONS.copy()
                employee.save(update_fields=['permissions'])
            
            # Get all permissions with descriptions
            permissions = employee.get_all_permissions()
            
            return Response({
                'employee_id': employee.employee_id,
                'username': employee.username,
                'full_name': employee.full_name,
                'saraf_id': employee.saraf_account.saraf_id,
                'saraf_name': employee.saraf_account.full_name,
                'permissions': permissions,
                'total_permissions': len(permissions),
                'allowed_permissions': sum(1 for p in permissions.values() if p.get('allowed', False))
            }, status=status.HTTP_200_OK)
            
        except SarafEmployee.DoesNotExist:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)


class EmployeePermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, employee_id=None):
        """Get employee permissions"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return Response({'error': 'Invalid user token'}, status=status.HTTP_401_UNAUTHORIZED)

        # Only Saraf owners can view employee permissions
        if user_info['user_type'] != 'saraf':
            return Response({'error': 'Only Saraf owners can view employee permissions.'}, status=status.HTTP_403_FORBIDDEN)

        if employee_id:
            # Get specific employee permissions
            try:
                employee = SarafEmployee.objects.get(employee_id=employee_id)
                
                # Ensure the employee belongs to the authenticated Saraf
                if employee.saraf_account.saraf_id != user_info['saraf_id']:
                    return Response({'error': 'You can only view permissions for your own employees.'}, status=status.HTTP_403_FORBIDDEN)
                
                permissions = employee.get_all_permissions()
                
                return Response({
                    'employee_id': employee.employee_id,
                    'username': employee.username,
                    'full_name': employee.full_name,
                    'permissions': permissions
                }, status=status.HTTP_200_OK)
                
            except SarafEmployee.DoesNotExist:
                return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Get default permissions template
            return Response({
                'default_permissions': DEFAULT_EMPLOYEE_PERMISSIONS,
                'permission_descriptions': PERMISSION_DESCRIPTIONS,
                'total_permissions': len(PERMISSION_DESCRIPTIONS)
            }, status=status.HTTP_200_OK)

    def put(self, request, employee_id):
        """Update employee permissions"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return Response({'error': 'Invalid user token'}, status=status.HTTP_401_UNAUTHORIZED)

        # Only Saraf owners can update employee permissions
        if user_info['user_type'] != 'saraf':
            return Response({'error': 'Only Saraf owners can update employee permissions.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            employee = SarafEmployee.objects.get(employee_id=employee_id)
            
            # Ensure the employee belongs to the authenticated Saraf
            if employee.saraf_account.saraf_id != user_info['saraf_id']:
                return Response({'error': 'You can only update permissions for your own employees.'}, status=status.HTTP_403_FORBIDDEN)
                
        except SarafEmployee.DoesNotExist:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)

        permissions_data = request.data.get('permissions', {})
        
        if not permissions_data:
            return Response({'error': 'permissions data is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate permissions
            invalid_permissions = []
            for permission in permissions_data.keys():
                if permission not in PERMISSION_DESCRIPTIONS:
                    invalid_permissions.append(permission)
            
            if invalid_permissions:
                return Response({
                    'error': 'Invalid permissions',
                    'invalid_permissions': invalid_permissions,
                    'valid_permissions': list(PERMISSION_DESCRIPTIONS.keys())
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update permissions
            employee.update_permissions(permissions_data)
            
            return Response({
                'message': 'Employee permissions updated successfully.',
                'employee_id': employee.employee_id,
                'username': employee.username,
                'updated_permissions': employee.get_all_permissions()
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Failed to update permissions',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, employee_id):
        """Update specific permission for employee"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return Response({'error': 'Invalid user token'}, status=status.HTTP_401_UNAUTHORIZED)

        # Only Saraf owners can update employee permissions
        if user_info['user_type'] != 'saraf':
            return Response({'error': 'Only Saraf owners can update employee permissions.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            employee = SarafEmployee.objects.get(employee_id=employee_id)
            
            # Ensure the employee belongs to the authenticated Saraf
            if employee.saraf_account.saraf_id != user_info['saraf_id']:
                return Response({'error': 'You can only update permissions for your own employees.'}, status=status.HTTP_403_FORBIDDEN)
                
        except SarafEmployee.DoesNotExist:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)

        permission_name = request.data.get('permission_name')
        allowed = request.data.get('allowed')

        if permission_name is None or allowed is None:
            return Response({
                'error': 'permission_name and allowed are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee.set_permission(permission_name, allowed)
            
            return Response({
                'message': f'Permission {permission_name} updated successfully.',
                'employee_id': employee.employee_id,
                'permission_name': permission_name,
                'allowed': bool(allowed),
                'description': PERMISSION_DESCRIPTIONS.get(permission_name, permission_name)
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Failed to update permission',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, employee_id):
        """Reset employee permissions to default"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return Response({'error': 'Invalid user token'}, status=status.HTTP_401_UNAUTHORIZED)

        # Only Saraf owners can reset employee permissions
        if user_info['user_type'] != 'saraf':
            return Response({'error': 'Only Saraf owners can reset employee permissions.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            employee = SarafEmployee.objects.get(employee_id=employee_id)
            
            # Ensure the employee belongs to the authenticated Saraf
            if employee.saraf_account.saraf_id != user_info['saraf_id']:
                return Response({'error': 'You can only reset permissions for your own employees.'}, status=status.HTTP_403_FORBIDDEN)
                
        except SarafEmployee.DoesNotExist:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            employee.reset_permissions_to_default()
            
            return Response({
                'message': 'Employee permissions reset to default successfully.',
                'employee_id': employee.employee_id,
                'username': employee.username,
                'default_permissions': employee.get_all_permissions()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': 'Failed to reset permissions',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BulkEmployeePermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Update permissions for multiple employees at once"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return Response({'error': 'Invalid user token'}, status=status.HTTP_401_UNAUTHORIZED)

        # Only Saraf owners can bulk update employee permissions
        if user_info['user_type'] != 'saraf':
            return Response({'error': 'Only Saraf owners can update employee permissions.'}, status=status.HTTP_403_FORBIDDEN)

        employees_data = request.data.get('employees', [])
        
        if not employees_data:
            return Response({'error': 'employees data is required.'}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        errors = []

        for emp_data in employees_data:
            employee_id = emp_data.get('employee_id')
            permissions = emp_data.get('permissions', {})

            if not employee_id:
                errors.append({'error': 'employee_id is required for each employee'})
                continue

            try:
                employee = SarafEmployee.objects.get(employee_id=employee_id)
                
                # Ensure the employee belongs to the authenticated Saraf
                if employee.saraf_account.saraf_id != user_info['saraf_id']:
                    errors.append({
                        'employee_id': employee_id,
                        'error': 'You can only update permissions for your own employees'
                    })
                    continue
                
                employee.update_permissions(permissions)
                
                results.append({
                    'employee_id': employee.employee_id,
                    'username': employee.username,
                    'status': 'updated',
                    'permissions_count': len([p for p in employee.permissions.values() if p])
                })

            except SarafEmployee.DoesNotExist:
                errors.append({
                    'employee_id': employee_id,
                    'error': 'Employee not found'
                })
            except Exception as e:
                errors.append({
                    'employee_id': employee_id,
                    'error': str(e)
                })

        return Response({
            'message': f'Bulk update completed. {len(results)} successful, {len(errors)} failed.',
            'successful_updates': results,
            'errors': errors
        }, status=status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS)


class PermissionTemplatesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Get permission templates and statistics"""
        # Calculate permission statistics
        total_permissions = len(PERMISSION_DESCRIPTIONS)
        default_allowed = sum(1 for allowed in DEFAULT_EMPLOYEE_PERMISSIONS.values() if allowed)
        
        # Create permission categories for better organization
        permission_categories = {
            'basic_operations': ['chat', 'send_transfer', 'receive_transfer', 'see_how_did_works', 'view_history'],
            'financial_operations': ['take_money', 'give_money', 'loans', 'deliver_amount', 'withdraw_to_customer', 'deposit_to_customer', 'withdraw_from_account', 'deposit_to_account'],
            'account_management': ['create_accounts', 'delete_accounts', 'edit_profile'],
            'administrative': ['add_employee', 'change_password', 'create_exchange', 'add_posts', 'add_currency']
        }

        categorized_permissions = {}
        for category, permissions in permission_categories.items():
            categorized_permissions[category] = {
                permission: {
                    'description': PERMISSION_DESCRIPTIONS.get(permission, permission.replace('_', ' ').title()),
                    'default_allowed': DEFAULT_EMPLOYEE_PERMISSIONS.get(permission, False)
                }
                for permission in permissions if permission in PERMISSION_DESCRIPTIONS
            }

        return Response({
            'default_template': DEFAULT_EMPLOYEE_PERMISSIONS,
            'permission_descriptions': PERMISSION_DESCRIPTIONS,
            'categorized_permissions': categorized_permissions,
            'statistics': {
                'total_permissions': total_permissions,
                'default_allowed': default_allowed,
                'default_denied': total_permissions - default_allowed,
                'default_percentage': round((default_allowed / total_permissions) * 100, 1)
            }
        }, status=status.HTTP_200_OK)

    def post(self, request):
        """Apply permission template to employee(s)"""
        employee_ids = request.data.get('employee_ids', [])
        template_permissions = request.data.get('template_permissions')
        
        if not employee_ids:
            return Response({'error': 'employee_ids are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if template_permissions is None:
            template_permissions = DEFAULT_EMPLOYEE_PERMISSIONS

        results = []
        errors = []

        for employee_id in employee_ids:
            try:
                employee = SarafEmployee.objects.get(employee_id=employee_id)
                employee.update_permissions(template_permissions)
                
                results.append({
                    'employee_id': employee.employee_id,
                    'username': employee.username,
                    'full_name': employee.full_name,
                    'status': 'template_applied'
                })

            except SarafEmployee.DoesNotExist:
                errors.append({
                    'employee_id': employee_id,
                    'error': 'Employee not found'
                })
            except Exception as e:
                errors.append({
                    'employee_id': employee_id,
                    'error': str(e)
                })

        return Response({
            'message': f'Template applied to {len(results)} employees. {len(errors)} failed.',
            'successful_applications': results,
            'errors': errors,
            'applied_template': template_permissions
        }, status=status.HTTP_200_OK if not errors else status.HTTP_207_MULTI_STATUS)


class SarafOTPVerificationView(APIView):
    """Verify OTP for Saraf account - Email only"""
    permission_classes = [AllowAny]
    
    @transaction.atomic
    def post(self, request):
        try:
            email = request.data.get('email', '').strip().lower()
            otp_code = request.data.get('otp_code', '').strip()
            
            if not email or not otp_code:
                return Response({'error': 'email and otp_code are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if account already exists (shouldn't happen, but check anyway)
            if SarafAccount.objects.filter(email=email).exists():
                saraf_account = SarafAccount.objects.get(email=email)
                # If account exists and is already verified, return success
                if saraf_account.is_email_verified:
                    return Response({
                        'message': 'Account already verified.',
                        'saraf_id': saraf_account.saraf_id,
                        'email': saraf_account.email,
                        'verified': True
                    })
                # If account exists but not verified, verify OTP from cache or existing OTP
                otp = SarafOTP.verify_otp(saraf_account, 'email', email, otp_code)
                if otp:
                    otp.mark_as_used()
                    saraf_account.update_verification_status(verified=True)
                    if not saraf_account.is_active:
                        saraf_account.is_active = True
                        saraf_account.save(update_fields=['is_active'])
                    return Response({
                        'message': 'Email OTP verified successfully. Your account is now active.',
                        'saraf_id': saraf_account.saraf_id,
                        'email': saraf_account.email,
                        'whatsapp_number': saraf_account.email_or_whatsapp_number,
                        'verified': True,
                        'is_active': saraf_account.is_active
                    })
            
            # Get registration data from cache
            cache_key = f'saraf_registration_{email}'
            registration_data = cache.get(cache_key)
            
            if not registration_data:
                return Response({
                    'error': 'Registration session expired or not found. Please register again.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify OTP code
            cached_otp = registration_data.get('otp_code')
            from datetime import datetime
            cached_expires_at = datetime.fromisoformat(registration_data.get('otp_expires_at'))
            
            if cached_otp != otp_code:
                return Response({
                    'error': 'Invalid OTP code'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if timezone.now() > cached_expires_at:
                # Clean up expired registration
                cache.delete(cache_key)
                return Response({
                    'error': 'OTP expired. Please register again.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # OTP is valid - create the account
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            
            saraf = SarafAccount(
                full_name=registration_data['full_name'],
                exchange_name=registration_data.get('exchange_name'),
                email=registration_data['email'],
                email_or_whatsapp_number=registration_data['email_or_whatsapp_number'],
                license_no=registration_data.get('license_no'),
                amu_pay_code=registration_data['amu_pay_code'],
                saraf_address=registration_data.get('saraf_address', ''),
                saraf_location_google_map=registration_data.get('saraf_location_google_map'),
                province=registration_data['province'],
                is_active=registration_data.get('is_active', False),
            )
            
            # Set password from stored hash
            saraf.password_hash = registration_data['password_hash']
            
            # Handle file uploads - move from temp to permanent location
            if registration_data.get('saraf_logo'):
                temp_file = default_storage.open(registration_data['saraf_logo'], 'rb')
                saraf.saraf_logo.save(
                    f'saraf_photos/saraf_logo_{email}_{timezone.now().timestamp()}.{registration_data["saraf_logo"].split(".")[-1]}',
                    temp_file,
                    save=False
                )
                temp_file.close()
                default_storage.delete(registration_data['saraf_logo'])
            
            if registration_data.get('saraf_logo_wallpeper'):
                temp_file = default_storage.open(registration_data['saraf_logo_wallpeper'], 'rb')
                saraf.saraf_logo_wallpeper.save(
                    f'saraf_photos/saraf_logo_wallpeper_{email}_{timezone.now().timestamp()}.{registration_data["saraf_logo_wallpeper"].split(".")[-1]}',
                    temp_file,
                    save=False
                )
                temp_file.close()
                default_storage.delete(registration_data['saraf_logo_wallpeper'])
            
            if registration_data.get('front_id_card'):
                temp_file = default_storage.open(registration_data['front_id_card'], 'rb')
                saraf.front_id_card.save(
                    f'saraf_photos/front_id_card_{email}_{timezone.now().timestamp()}.{registration_data["front_id_card"].split(".")[-1]}',
                    temp_file,
                    save=False
                )
                temp_file.close()
                default_storage.delete(registration_data['front_id_card'])
            
            if registration_data.get('back_id_card'):
                temp_file = default_storage.open(registration_data['back_id_card'], 'rb')
                saraf.back_id_card.save(
                    f'saraf_photos/back_id_card_{email}_{timezone.now().timestamp()}.{registration_data["back_id_card"].split(".")[-1]}',
                    temp_file,
                    save=False
                )
                temp_file.close()
                default_storage.delete(registration_data['back_id_card'])
            
            # Save the account
            saraf.save()
            
            # Mark as verified and active
            saraf.is_email_verified = True
            saraf.is_active = True
            saraf.save(update_fields=['is_email_verified', 'is_active'])
            
            # Clean up cache
            cache.delete(cache_key)
            
            # Create JWT token
            refresh = RefreshToken()
            refresh['saraf_id'] = saraf.saraf_id
            refresh['user_type'] = 'saraf'
            refresh['user_id'] = saraf.saraf_id
            refresh['full_name'] = saraf.full_name
            refresh['exchange_name'] = saraf.exchange_name
            refresh['email_or_whatsapp_number'] = saraf.email_or_whatsapp_number
            
            return Response({
                'message': 'Email OTP verified successfully. Your account is now active.',
                'saraf_id': saraf.saraf_id,
                'email': saraf.email,
                'whatsapp_number': saraf.email_or_whatsapp_number,
                'verified': True,
                'is_active': saraf.is_active,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error in SarafOTPVerificationView: {str(e)}", exc_info=True)
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SarafResendOTPView(APIView):
    """Resend OTP for Saraf account - Email only"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email', '').strip().lower()
            
            if not email:
                return Response({'error': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if registration data exists in cache (pending registration)
            cache_key = f'saraf_registration_{email}'
            registration_data = cache.get(cache_key)
            
            if registration_data:
                # Pending registration - regenerate OTP and update cache
                import random
                otp_code = str(random.randint(100000, 999999))
                expires_at = timezone.now() + timedelta(minutes=10)
                
                # Update registration data with new OTP
                registration_data['otp_code'] = otp_code
                registration_data['otp_expires_at'] = expires_at.isoformat()
                
                # Update cache
                cache.set(cache_key, registration_data, 15 * 60)
                
                # Send new OTP
                try:
                    send_otp_email_saraf(email, otp_code)
                    return Response({
                        'message': 'New OTP sent to your email. Please check your inbox.',
                        'email': email,
                        'otp_type': 'email'
                    })
                except Exception as e:
                    logger.error(f"Failed to send OTP email: {str(e)}")
                    return Response({
                        'error': 'Failed to send OTP email. Please try again.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Check if account already exists (old flow for existing accounts)
            try:
                saraf_account = SarafAccount.objects.get(email=email)
            except SarafAccount.DoesNotExist:
                return Response({
                    'error': 'No pending registration or account found with this email. Please register first.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Generate new OTP for existing account (always email)
            otp = SarafOTP.generate_otp(saraf_account, 'email', email)
            
            # Send OTP to email
            send_otp_email_saraf(email, otp.otp_code)
            
            return Response({
                'message': 'OTP resent successfully to your email',
                'email': email,
                'otp_type': 'email'
            })
            
        except Exception as e:
            logger.error(f"Error in SarafResendOTPView: {str(e)}", exc_info=True)
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomTokenRefreshView(APIView):
    """
    Custom token refresh view that works with SarafJWTAuthentication
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Refresh access token using refresh token
        """
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return Response({
                    'error': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate the refresh token
            from rest_framework_simplejwt.tokens import RefreshToken
            from rest_framework_simplejwt.exceptions import TokenError
            
            try:
                refresh = RefreshToken(refresh_token)
            except TokenError:
                return Response({
                    'error': 'Invalid refresh token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get user information from the refresh token
            user_type = refresh.get('user_type')
            user_id = refresh.get('user_id')
            saraf_id = refresh.get('saraf_id')
            
            if not user_type or not user_id:
                return Response({
                    'error': 'Invalid token format'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Verify user still exists and is active
            if user_type == 'saraf':
                try:
                    saraf = SarafAccount.objects.get(saraf_id=saraf_id, is_active=True)
                except SarafAccount.DoesNotExist:
                    return Response({
                        'error': 'Saraf account not found or inactive'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Create new access token with saraf data
                new_access_token = refresh.access_token
                new_access_token['user_type'] = 'saraf'
                new_access_token['user_id'] = saraf.saraf_id
                new_access_token['saraf_id'] = saraf.saraf_id
                new_access_token['full_name'] = saraf.full_name
                new_access_token['exchange_name'] = saraf.exchange_name
                new_access_token['email_or_whatsapp_number'] = saraf.email_or_whatsapp_number
                
            elif user_type == 'employee':
                try:
                    employee = SarafEmployee.objects.select_related('saraf_account').get(
                        employee_id=user_id,
                        is_active=True
                    )
                    saraf = employee.saraf_account
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found or inactive'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Create new access token with employee data
                new_access_token = refresh.access_token
                new_access_token['user_type'] = 'employee'
                new_access_token['user_id'] = employee.employee_id
                new_access_token['saraf_id'] = saraf.saraf_id
                new_access_token['employee_id'] = employee.employee_id
                new_access_token['full_name'] = employee.full_name
                new_access_token['email_or_whatsapp_number'] = saraf.email_or_whatsapp_number
                
            elif user_type == 'normal_user':
                try:
                    from normal_user_account.models import NormalUser
                    user = NormalUser.objects.get(user_id=user_id, is_active=True)
                except NormalUser.DoesNotExist:
                    return Response({
                        'error': 'User not found or inactive'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Create new access token with normal user data
                new_access_token = refresh.access_token
                new_access_token['user_type'] = 'normal_user'
                new_access_token['user_id'] = user.user_id
                new_access_token['full_name'] = user.full_name
                new_access_token['email'] = user.email
                new_access_token['whatsapp_number'] = user.whatsapp_number
                
            else:
                return Response({
                    'error': 'Invalid user type'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response({
                'access': str(new_access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in CustomTokenRefreshView: {str(e)}")
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SarafPictureManagementView(APIView):
    """
    View for managing Saraf account pictures
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request):
        """Get current pictures for the authenticated saraf account"""
        try:
            # Get user info from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get saraf account
            try:
                saraf = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
            except SarafAccount.DoesNotExist:
                return Response({
                    'error': 'Saraf account not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize pictures with full URLs
            serializer = SarafPictureListSerializer(saraf, context={'request': request})
            
            return Response({
                'message': 'Pictures retrieved successfully',
                'saraf_id': saraf.saraf_id,
                'saraf_name': saraf.full_name,
                'pictures': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving saraf pictures: {str(e)}")
            return Response({
                'error': 'Failed to retrieve pictures',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def put(self, request):
        """Update saraf account pictures"""
        try:
            # Get user info from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get saraf account
            try:
                saraf = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
            except SarafAccount.DoesNotExist:
                return Response({
                    'error': 'Saraf account not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validate and update pictures
            serializer = SarafPictureUpdateSerializer(saraf, data=request.data, partial=True)
            if serializer.is_valid():
                # Update only the provided fields
                updated_fields = []
                for field in ['saraf_logo', 'saraf_logo_wallpeper', 'front_id_card', 'back_id_card']:
                    if field in request.data:
                        updated_fields.append(field)
                
                serializer.save()
                
                # Log the action
                from .models import ActionLog
                ActionLog.objects.create(
                    saraf=saraf,
                    user_type='saraf',
                    user_id=saraf.saraf_id,
                    user_name=saraf.full_name,
                    action_type='update_pictures',
                    description=f'Updated pictures: {", ".join(updated_fields)}'
                )
                
                logger.info(f"Successfully updated pictures {updated_fields} for saraf {saraf.saraf_id}")
                
                # Return updated pictures with full URLs
                response_serializer = SarafPictureListSerializer(saraf, context={'request': request})
                
                return Response({
                    'message': 'Pictures updated successfully',
                    'updated_fields': updated_fields,
                    'saraf_id': saraf.saraf_id,
                    'pictures': response_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error updating saraf pictures: {str(e)}")
            return Response({
                'error': 'Failed to update pictures',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def delete(self, request):
        """Delete specific picture fields"""
        try:
            # Get user info from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get saraf account
            try:
                saraf = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
            except SarafAccount.DoesNotExist:
                return Response({
                    'error': 'Saraf account not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validate delete request
            serializer = SarafPictureDeleteSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            fields_to_delete = serializer.validated_data['fields_to_delete']
            
            # Delete the specified picture fields
            deleted_fields = []
            for field in fields_to_delete:
                if hasattr(saraf, field) and getattr(saraf, field):
                    # Delete the file from storage
                    old_file = getattr(saraf, field)
                    if old_file:
                        old_file.delete(save=False)
                    
                    # Clear the field
                    setattr(saraf, field, None)
                    deleted_fields.append(field)
            
            # Save the changes
            saraf.save(update_fields=fields_to_delete)
            
            # Log the action
            from .models import ActionLog
            ActionLog.objects.create(
                saraf=saraf,
                user_type='saraf',
                user_id=saraf.saraf_id,
                user_name=saraf.full_name,
                action_type='delete_pictures',
                description=f'Deleted pictures: {", ".join(deleted_fields)}'
            )
            
            logger.info(f"Successfully deleted pictures {deleted_fields} for saraf {saraf.saraf_id}")
            
            return Response({
                'message': 'Pictures deleted successfully',
                'deleted_fields': deleted_fields,
                'saraf_id': saraf.saraf_id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting saraf pictures: {str(e)}")
            return Response({
                'error': 'Failed to delete pictures',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SarafSinglePictureUpdateView(APIView):
    """
    View for updating a single picture field
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    @transaction.atomic
    def put(self, request, picture_field):
        """Update a single picture field"""
        try:
            # Validate picture field
            valid_fields = ['saraf_logo', 'saraf_logo_wallpeper', 'front_id_card', 'back_id_card']
            if picture_field not in valid_fields:
                return Response({
                    'error': 'Invalid picture field',
                    'valid_fields': valid_fields
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user info from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get saraf account
            try:
                saraf = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
            except SarafAccount.DoesNotExist:
                return Response({
                    'error': 'Saraf account not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get the new image file
            new_image = request.FILES.get(picture_field)
            if not new_image:
                return Response({
                    'error': f'{picture_field} file is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate image
            try:
                import os
                from PIL import Image
                
                # Check file size (max 5MB)
                if new_image.size > 5 * 1024 * 1024:
                    return Response({
                        'error': f'{picture_field} file size cannot exceed 5MB'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check file extension
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
                file_extension = os.path.splitext(new_image.name)[1].lower()
                if file_extension not in allowed_extensions:
                    return Response({
                        'error': f'{picture_field} must be in JPEG, PNG, or WEBP format'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check image format and content
                new_image.seek(0)
                with Image.open(new_image) as img:
                    # Check if it's a valid image format
                    if img.format not in ['JPEG', 'PNG', 'WEBP']:
                        return Response({
                            'error': f'{picture_field} must be in JPEG, PNG, or WEBP format'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Check image dimensions (prevent extremely large images)
                    max_dimension = 4096  # Max width or height
                    if img.width > max_dimension or img.height > max_dimension:
                        return Response({
                            'error': f'{picture_field} dimensions cannot exceed {max_dimension}x{max_dimension} pixels'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Check if image is too small (prevent tiny images)
                    min_dimension = 10
                    if img.width < min_dimension or img.height < min_dimension:
                        return Response({
                            'error': f'{picture_field} dimensions must be at least {min_dimension}x{min_dimension} pixels'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Verify image can be loaded properly
                    img.verify()
                
                # Reset file pointer after validation
                new_image.seek(0)
                
            except Exception as e:
                logger.error(f"Image validation error for {picture_field}: {str(e)}")
                return Response({
                    'error': f'Invalid image file: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Store reference to old file before updating
            old_file = getattr(saraf, picture_field)
            
            # Update the field and save first
            setattr(saraf, picture_field, new_image)
            saraf.save(update_fields=[picture_field])
            
            # Delete old file after successful save
            if old_file:
                try:
                    old_file.delete(save=False)
                    logger.info(f"Successfully deleted old {picture_field} file for saraf {saraf.saraf_id}")
                except Exception as e:
                    logger.warning(f"Failed to delete old {picture_field} file for saraf {saraf.saraf_id}: {str(e)}")
            
            # Log the action
            from .models import ActionLog
            ActionLog.objects.create(
                saraf=saraf,
                user_type='saraf',
                user_id=saraf.saraf_id,
                user_name=saraf.full_name,
                action_type='update_single_picture',
                description=f'Updated {picture_field}'
            )
            
            logger.info(f"Successfully updated {picture_field} for saraf {saraf.saraf_id}")
            
            # Return updated picture URL
            updated_file = getattr(saraf, picture_field)
            picture_url = build_absolute_uri(request, updated_file)
            
            return Response({
                'message': f'{picture_field} updated successfully',
                'picture_field': picture_field,
                'picture_url': picture_url,
                'saraf_id': saraf.saraf_id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating single picture {picture_field}: {str(e)}")
            return Response({
                'error': f'Failed to update {picture_field}',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def delete(self, request, picture_field):
        """Delete a single picture field"""
        try:
            # Validate picture field
            valid_fields = ['saraf_logo', 'saraf_logo_wallpeper', 'front_id_card', 'back_id_card']
            if picture_field not in valid_fields:
                return Response({
                    'error': 'Invalid picture field',
                    'valid_fields': valid_fields
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user info from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get saraf account
            try:
                saraf = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
            except SarafAccount.DoesNotExist:
                return Response({
                    'error': 'Saraf account not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if field has a value
            current_file = getattr(saraf, picture_field)
            if not current_file:
                return Response({
                    'error': f'{picture_field} is already empty'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Delete the file from storage
            current_file.delete(save=False)
            
            # Clear the field
            setattr(saraf, picture_field, None)
            saraf.save(update_fields=[picture_field])
            
            # Log the action
            from .models import ActionLog
            ActionLog.objects.create(
                saraf=saraf,
                user_type='saraf',
                user_id=saraf.saraf_id,
                user_name=saraf.full_name,
                action_type='delete_single_picture',
                description=f'Deleted {picture_field}'
            )
            
            logger.info(f"Successfully deleted {picture_field} for saraf {saraf.saraf_id}")
            
            return Response({
                'message': f'{picture_field} deleted successfully',
                'picture_field': picture_field,
                'saraf_id': saraf.saraf_id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting single picture {picture_field}: {str(e)}")
            return Response({
                'error': f'Failed to delete {picture_field}',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SarafDetailView(APIView):
    """Get detailed information about a specific Saraf account by ID"""
    permission_classes = [AllowAny]
    
    def get(self, request, saraf_id):
        """
        Get detailed Saraf profile by saraf_id
        """
        try:
            saraf = SarafAccount.objects.get(saraf_id=saraf_id)
            
            # Check if the account is active (optional - remove if you want to show inactive accounts too)
            if not saraf.is_active:
                return Response({
                    'error': 'Saraf account is not active'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Build full URLs for images
            data = {
                'saraf_id': saraf.saraf_id,
                'full_name': saraf.full_name,
                'exchange_name': saraf.exchange_name,
                'email_or_whatsapp_number': saraf.email_or_whatsapp_number,
                'license_no': saraf.license_no,
                'amu_pay_code': saraf.amu_pay_code,
                'saraf_address': saraf.saraf_address,
                'saraf_location_google_map': saraf.saraf_location_google_map,
                'province': saraf.province,
                'is_email_verified': saraf.is_email_verified,
                'is_whatsapp_verified': saraf.is_whatsapp_verified,
                'is_active': saraf.is_active,
                'created_at': saraf.created_at,
                'updated_at': saraf.updated_at,
                'saraf_logo': build_absolute_uri(request, saraf.saraf_logo),
                'saraf_logo_wallpeper': build_absolute_uri(request, saraf.saraf_logo_wallpeper),
                'front_id_card': build_absolute_uri(request, saraf.front_id_card),
                'back_id_card': build_absolute_uri(request, saraf.back_id_card),
            }
            
            # Get active employees count
            employee_count = SarafEmployee.objects.filter(
                saraf_account=saraf,
                is_active=True
            ).count()
            data['employee_count'] = employee_count
            
            return Response({
                'message': 'Saraf profile retrieved successfully',
                'saraf': data
            }, status=status.HTTP_200_OK)
            
        except SarafAccount.DoesNotExist:
            return Response({
                'error': 'Saraf account not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            logger.error(f"Error fetching Saraf profile {saraf_id}: {str(e)}")
            return Response({
                'error': 'Failed to fetch Saraf profile',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
