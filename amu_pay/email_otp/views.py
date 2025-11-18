from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import EmailOTP
from .serializers import GenerateOTPSerializer, VerifyOTPSerializer, EmailOTPSerializer
from .utils import send_otp_email
import logging

logger = logging.getLogger(__name__)

class GenerateOTPView(APIView):
    permission_classes = [AllowAny]
    """
    API endpoint to generate and send OTP to email
    """
    def post(self, request):
        serializer = GenerateOTPSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                # Check if OTP already exists for this email
                try:
                    email_otp = EmailOTP.objects.get(email=email)
                    # Delete existing OTP to create a new one
                    email_otp.delete()
                except EmailOTP.DoesNotExist:
                    pass
                
                # Create new OTP
                email_otp = EmailOTP.objects.create(email=email)
                
                # Send OTP via email
                if send_otp_email(email, email_otp.otp_code):
                    return Response({
                        'message': 'OTP sent successfully to your email',
                        'email': email
                    }, status=status.HTTP_200_OK)
                else:
                    # Delete the OTP if email sending failed
                    email_otp.delete()
                    return Response({
                        'error': 'Failed to send OTP email. Please try again.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
            except Exception as e:
                logger.error(f"Error generating OTP for {email}: {str(e)}")
                return Response({
                    'error': 'An error occurred while generating OTP'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    """
    API endpoint to verify OTP and activate email
    """
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            
            try:
                # Find the OTP record
                email_otp = EmailOTP.objects.get(email=email, otp_code=otp_code)
                
                # Check if OTP has expired
                if email_otp.is_expired():
                    email_otp.delete()  # Clean up expired OTP
                    return Response({
                        'error': 'OTP has expired. Please request a new one.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if email is already active
                if email_otp.is_active:
                    return Response({
                        'message': 'Email is already verified',
                        'email': email,
                        'is_active': True
                    }, status=status.HTTP_200_OK)
                
                # Activate the email
                email_otp.is_active = True
                email_otp.save()
                
                return Response({
                    'message': 'Email verified successfully',
                    'email': email,
                    'is_active': True
                }, status=status.HTTP_200_OK)
                
            except EmailOTP.DoesNotExist:
                return Response({
                    'error': 'Invalid OTP code or email'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error verifying OTP for {email}: {str(e)}")
                return Response({
                    'error': 'An error occurred while verifying OTP'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailStatusView(APIView):
    permission_classes = [AllowAny]
    """
    API endpoint to check email verification status
    """
    def get(self, request):
        email = request.query_params.get('email')
        
        if not email:
            return Response({
                'error': 'Email parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            email_otp = EmailOTP.objects.get(email=email.lower())
            serializer = EmailOTPSerializer(email_otp)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except EmailOTP.DoesNotExist:
            return Response({
                'email': email.lower(),
                'is_active': False,
                'message': 'Email not found in system'
            }, status=status.HTTP_404_NOT_FOUND)
