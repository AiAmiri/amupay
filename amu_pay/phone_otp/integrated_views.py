from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import PhoneOTP
from email_otp.models import EmailOTP
from .serializers import GeneratePhoneOTPSerializer, VerifyPhoneOTPSerializer
from email_otp.serializers import GenerateOTPSerializer, VerifyOTPSerializer
from .utils import send_sms_otp
from email_otp.utils import send_otp_email
import logging

logger = logging.getLogger(__name__)

class CombinedOTPGenerateView(APIView):
    permission_classes = [AllowAny]
    """
    API endpoint to generate OTP for both email and phone (if both are provided)
    or individual email/phone verification
    """
    def post(self, request):
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        
        if not email and not phone_number:
            return Response({
                'error': 'Either email or phone_number (or both) must be provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        results = {}
        errors = {}
        
        # Handle email OTP generation
        if email:
            email_serializer = GenerateOTPSerializer(data={'email': email})
            if email_serializer.is_valid():
                try:
                    # Check if email OTP already exists
                    try:
                        email_otp = EmailOTP.objects.get(email=email)
                        email_otp.delete()
                    except EmailOTP.DoesNotExist:
                        pass
                    
                    # Create new email OTP
                    email_otp = EmailOTP.objects.create(email=email)
                    
                    # Send OTP via email
                    if send_otp_email(email, email_otp.otp_code):
                        results['email'] = {
                            'message': 'OTP sent successfully to your email',
                            'email': email
                        }
                    else:
                        email_otp.delete()
                        errors['email'] = 'Failed to send OTP email'
                        
                except Exception as e:
                    logger.error(f"Error generating email OTP for {email}: {str(e)}")
                    errors['email'] = 'An error occurred while generating email OTP'
            else:
                errors['email'] = email_serializer.errors
        
        # Handle phone OTP generation
        if phone_number:
            phone_serializer = GeneratePhoneOTPSerializer(data={'phone_number': phone_number})
            if phone_serializer.is_valid():
                try:
                    # Check if phone OTP already exists
                    try:
                        phone_otp = PhoneOTP.objects.get(phone_number=phone_number)
                        phone_otp.delete()
                    except PhoneOTP.DoesNotExist:
                        pass
                    
                    # Create new phone OTP
                    phone_otp = PhoneOTP.objects.create(phone_number=phone_number)
                    
                    # Send OTP via SMS
                    if send_sms_otp(phone_number, phone_otp.otp_code):
                        results['phone'] = {
                            'message': 'OTP sent successfully to your phone',
                            'phone_number': phone_number
                        }
                    else:
                        phone_otp.delete()
                        errors['phone'] = 'Failed to send OTP SMS'
                        
                except Exception as e:
                    logger.error(f"Error generating phone OTP for {phone_number}: {str(e)}")
                    errors['phone'] = 'An error occurred while generating phone OTP'
            else:
                errors['phone'] = phone_serializer.errors
        
        # Prepare response
        if results and not errors:
            return Response({
                'message': 'OTP(s) sent successfully',
                'results': results
            }, status=status.HTTP_200_OK)
        elif results and errors:
            return Response({
                'message': 'Partial success',
                'results': results,
                'errors': errors
            }, status=status.HTTP_207_MULTI_STATUS)
        else:
            return Response({
                'error': 'Failed to send OTP(s)',
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)

class CombinedOTPVerifyView(APIView):
    permission_classes = [AllowAny]
    """
    API endpoint to verify OTP for both email and phone
    Both must be verified for successful authentication
    """
    def post(self, request):
        email = request.data.get('email')
        email_otp_code = request.data.get('email_otp_code')
        phone_number = request.data.get('phone_number')
        phone_otp_code = request.data.get('phone_otp_code')
        
        if not ((email and email_otp_code) or (phone_number and phone_otp_code)):
            return Response({
                'error': 'Either (email and email_otp_code) or (phone_number and phone_otp_code) must be provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        results = {}
        errors = {}
        
        # Verify email OTP
        if email and email_otp_code:
            email_serializer = VerifyOTPSerializer(data={'email': email, 'otp_code': email_otp_code})
            if email_serializer.is_valid():
                try:
                    email_otp = EmailOTP.objects.get(email=email, otp_code=email_otp_code)
                    
                    if email_otp.is_expired():
                        email_otp.delete()
                        errors['email'] = 'Email OTP has expired'
                    elif email_otp.is_active:
                        results['email'] = {
                            'message': 'Email is already verified',
                            'email': email,
                            'is_active': True
                        }
                    else:
                        email_otp.is_active = True
                        email_otp.save()
                        results['email'] = {
                            'message': 'Email verified successfully',
                            'email': email,
                            'is_active': True
                        }
                        
                except EmailOTP.DoesNotExist:
                    errors['email'] = 'Invalid email OTP code'
                except Exception as e:
                    logger.error(f"Error verifying email OTP for {email}: {str(e)}")
                    errors['email'] = 'An error occurred while verifying email OTP'
            else:
                errors['email'] = email_serializer.errors
        
        # Verify phone OTP
        if phone_number and phone_otp_code:
            phone_serializer = VerifyPhoneOTPSerializer(data={'phone_number': phone_number, 'otp_code': phone_otp_code})
            if phone_serializer.is_valid():
                # Use the validated phone number (converted to E.164 format)
                validated_phone = phone_serializer.validated_data['phone_number']
                try:
                    phone_otp = PhoneOTP.objects.get(phone_number=validated_phone, otp_code=phone_otp_code)
                    
                    if phone_otp.is_expired():
                        phone_otp.delete()
                        errors['phone'] = 'Phone OTP has expired'
                    elif phone_otp.is_active:
                        results['phone'] = {
                            'message': 'Phone number is already verified',
                            'phone_number': validated_phone,
                            'is_active': True
                        }
                    else:
                        phone_otp.is_active = True
                        phone_otp.save()
                        results['phone'] = {
                            'message': 'Phone number verified successfully',
                            'phone_number': validated_phone,
                            'is_active': True
                        }
                        
                except PhoneOTP.DoesNotExist:
                    errors['phone'] = 'Invalid phone OTP code'
                except Exception as e:
                    logger.error(f"Error verifying phone OTP for {phone_number}: {str(e)}")
                    errors['phone'] = 'An error occurred while verifying phone OTP'
            else:
                errors['phone'] = phone_serializer.errors
        
        # Prepare response
        if results and not errors:
            return Response({
                'message': 'OTP(s) verified successfully',
                'results': results
            }, status=status.HTTP_200_OK)
        elif results and errors:
            return Response({
                'message': 'Partial verification',
                'results': results,
                'errors': errors
            }, status=status.HTTP_207_MULTI_STATUS)
        else:
            return Response({
                'error': 'Failed to verify OTP(s)',
                'errors': errors
            }, status=status.HTTP_400_BAD_REQUEST)

class CombinedStatusView(APIView):
    permission_classes = [AllowAny]
    """
    API endpoint to check verification status for both email and phone
    """
    def get(self, request):
        email = request.query_params.get('email')
        phone_number = request.query_params.get('phone_number')
        
        if not email and not phone_number:
            return Response({
                'error': 'Either email or phone_number parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        results = {}
        
        # Check email status
        if email:
            try:
                email_otp = EmailOTP.objects.get(email=email)
                results['email'] = {
                    'email': email,
                    'is_active': email_otp.is_active,
                    'created_at': email_otp.created_at
                }
            except EmailOTP.DoesNotExist:
                results['email'] = {
                    'email': email,
                    'is_active': False,
                    'message': 'Email not found in system'
                }
        
        # Check phone status
        if phone_number:
            try:
                phone_otp = PhoneOTP.objects.get(phone_number=phone_number)
                results['phone'] = {
                    'phone_number': phone_number,
                    'is_active': phone_otp.is_active,
                    'created_at': phone_otp.created_at
                }
            except PhoneOTP.DoesNotExist:
                results['phone'] = {
                    'phone_number': phone_number,
                    'is_active': False,
                    'message': 'Phone number not found in system'
                }
        
        return Response(results, status=status.HTTP_200_OK)
