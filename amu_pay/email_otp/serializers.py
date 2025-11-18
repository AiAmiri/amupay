from rest_framework import serializers
from .models import EmailOTP

class GenerateOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate email format"""
        return value.lower()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_email(self, value):
        """Validate email format"""
        return value.lower()
    
    def validate_otp_code(self, value):
        """Validate OTP code is numeric and 6 digits"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP code must be numeric")
        if len(value) != 6:
            raise serializers.ValidationError("OTP code must be exactly 6 digits")
        return value

class EmailOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailOTP
        fields = ['email', 'is_active', 'created_at']
        read_only_fields = ['created_at']