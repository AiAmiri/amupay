from rest_framework import serializers
from .models import PhoneOTP
import re
from utils.phone_validation import validate_and_format_phone_number

class GeneratePhoneOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    
    def validate_phone_number(self, value):
        """Validate phone number format - accepts both local Afghan format and E.164"""
        return validate_and_format_phone_number(value)

class VerifyPhoneOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_phone_number(self, value):
        """Validate phone number format - accepts both local Afghan format and E.164"""
        return validate_and_format_phone_number(value)
    
    def validate_otp_code(self, value):
        """Validate OTP code is numeric and 6 digits"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must be numeric")
        if len(value) != 6:
            raise serializers.ValidationError("OTP code must be exactly 6 digits")
        return value

class PhoneOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneOTP
        fields = ['phone_number', 'is_active', 'created_at']
        read_only_fields = ['created_at']
