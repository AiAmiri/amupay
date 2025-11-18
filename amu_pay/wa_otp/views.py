from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import logging

from .models import WhatsAppOTP
from .serializers import WhatsAppOTPSerializer, VerifyWhatsAppOTPSerializer
from .utils import send_whatsapp_otp

logger = logging.getLogger(__name__)

class WhatsAppOTPView(APIView):
    def post(self, request):
        serializer = WhatsAppOTPSerializer(data=request.data)
        if serializer.is_valid():
            # Get the formatted phone number (E.164 format: +93XXXXXXXXX)
            phone_number = serializer.validated_data['phone_number']
            
            try:
                otp_instance = WhatsAppOTP.objects.get(phone_number=phone_number)
                otp_instance.otp_code = '' # Reset OTP to trigger generation
                otp_instance.expires_at = None # Reset expiry to trigger generation
                otp_instance.save()
            except WhatsAppOTP.DoesNotExist:
                otp_instance = WhatsAppOTP.objects.create(phone_number=phone_number)

            # Send WhatsApp OTP using utility function
            success, result = send_whatsapp_otp(phone_number, otp_instance.otp_code)
            
            if success:
                return Response({
                    'message': 'WhatsApp OTP sent successfully',
                    'phone_number': phone_number
                }, status=status.HTTP_200_OK)
            else:
                logger.error(f"Failed to send WhatsApp OTP to {phone_number}: {result}")
                return Response({
                    'error': 'Failed to send WhatsApp OTP',
                    'details': result
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyWhatsAppOTPView(APIView):
    def post(self, request):
        serializer = VerifyWhatsAppOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp_code = serializer.validated_data['otp_code']

            try:
                otp_instance = WhatsAppOTP.objects.get(phone_number=phone_number, otp_code=otp_code)

                if otp_instance.is_expired():
                    return Response({'error': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

                otp_instance.is_active = True
                otp_instance.save()
                return Response({'message': 'Phone number verified successfully'}, status=status.HTTP_200_OK)

            except WhatsAppOTP.DoesNotExist:
                return Response({'error': 'Invalid OTP or phone number'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
