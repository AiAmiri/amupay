from rest_framework import serializers
import re
from utils.phone_validation import validate_and_format_phone_number

class WhatsAppOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    
    def validate_phone_number(self, value):
        """Validate phone number format - Afghanistan focused for Twilio"""
        return validate_and_format_phone_number(value)

class VerifyWhatsAppOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=4)
    
    def validate_phone_number(self, value):
        """Validate phone number format - Afghanistan focused for Twilio"""
        return validate_and_format_phone_number(value)
    
    def validate_otp_code(self, value):
        """Validate OTP code is numeric and 4 digits"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must be numeric")
        if len(value) != 4:
            raise serializers.ValidationError("OTP code must be exactly 4 digits")
        return value
