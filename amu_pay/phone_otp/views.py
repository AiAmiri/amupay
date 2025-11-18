from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import PhoneOTP
from .serializers import GeneratePhoneOTPSerializer, VerifyPhoneOTPSerializer, PhoneOTPSerializer
from .utils import send_sms_otp
import logging

logger = logging.getLogger(__name__)

class GeneratePhoneOTPView(APIView):
    permission_classes = [AllowAny]
    """
    API endpoint to generate and send OTP to phone number via SMS
    """
    def post(self, request):
        serializer = GeneratePhoneOTPSerializer(data=request.data)
        
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            
            try:
                # Check if OTP already exists for this phone number
                try:
                    phone_otp = PhoneOTP.objects.get(phone_number=phone_number)
                    # Delete existing OTP to create a new one
                    phone_otp.delete()
                except PhoneOTP.DoesNotExist:
                    pass
                
                # Create new OTP
                phone_otp = PhoneOTP.objects.create(phone_number=phone_number)
                
                # Send OTP via SMS
                if send_sms_otp(phone_number, phone_otp.otp_code):
                    return Response({
                        'message': 'OTP sent successfully to your phone',
                        'phone_number': phone_number
                    }, status=status.HTTP_200_OK)
                else:
                    # Delete the OTP if SMS sending failed
                    phone_otp.delete()
                    return Response({
                        'error': 'Failed to send OTP SMS. Please try again.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
            except Exception as e:
                logger.error(f"Error generating OTP for {phone_number}: {str(e)}")
                return Response({
                    'error': 'An error occurred while generating OTP'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyPhoneOTPView(APIView):
    permission_classes = [AllowAny]
    """
    API endpoint to verify OTP and activate phone number
    """
    def post(self, request):
        serializer = VerifyPhoneOTPSerializer(data=request.data)
        
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp_code = serializer.validated_data['otp_code']
            
            try:
                # Find the OTP record
                phone_otp = PhoneOTP.objects.get(phone_number=phone_number, otp_code=otp_code)
                
                # Check if OTP has expired
                if phone_otp.is_expired():
                    phone_otp.delete()  # Clean up expired OTP
                    return Response({
                        'error': 'OTP has expired. Please request a new one.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if phone number is already active
                if phone_otp.is_active:
                    return Response({
                        'message': 'Phone number is already verified',
                        'phone_number': phone_number,
                        'is_active': True
                    }, status=status.HTTP_200_OK)
                
                # Activate the phone number
                phone_otp.is_active = True
                phone_otp.save()
                
                return Response({
                    'message': 'Phone number verified successfully',
                    'phone_number': phone_number,
                    'is_active': True
                }, status=status.HTTP_200_OK)
                
            except PhoneOTP.DoesNotExist:
                return Response({
                    'error': 'Invalid OTP code or phone number'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error verifying OTP for {phone_number}: {str(e)}")
                return Response({
                    'error': 'An error occurred while verifying OTP'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PhoneStatusView(APIView):
    permission_classes = [AllowAny]
    """
    API endpoint to check phone number verification status
    """
    def get(self, request):
        phone_number = request.query_params.get('phone_number')
        
        if not phone_number:
            return Response({
                'error': 'Phone number parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            phone_otp = PhoneOTP.objects.get(phone_number=phone_number)
            serializer = PhoneOTPSerializer(phone_otp)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PhoneOTP.DoesNotExist:
            return Response({
                'phone_number': phone_number,
                'is_active': False,
                'message': 'Phone number not found in system'
            }, status=status.HTTP_404_NOT_FOUND)
