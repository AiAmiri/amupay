from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils import timezone
from datetime import timedelta
import re
from .models import NormalUser, NormalUserOTP
from utils.phone_validation import validate_and_format_phone_number


class NormalUserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for normal user registration - Both email and WhatsApp required"""
    
    password = serializers.CharField(write_only=True, min_length=6)
    repeat_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True, help_text="Email address for OTP verification")
    email_or_whatsapp = serializers.CharField(required=True, write_only=True, help_text="Afghan WhatsApp number (e.g., 0790976268 or +93790976268)")
    
    class Meta:
        model = NormalUser
        fields = ['full_name', 'email', 'email_or_whatsapp', 'password', 'repeat_password']
        # Note: email_or_whatsapp in API maps to email_or_whatsapp in model (WhatsApp only)
    
    def validate_email_or_whatsapp(self, value):
        """Validate that the input is a valid Afghan WhatsApp number (ONLY phone numbers, no emails)"""
        value = value.strip()
        
        # Should NOT be an email
        if '@' in value:
            raise serializers.ValidationError("This field should contain a WhatsApp number only. Please use the 'email' field for your email address.")
        
        # It's a phone number - use shared validation utility
        return validate_and_format_phone_number(value)
    
    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character")
        
        return value
    
    def validate(self, attrs):
        """Validate that passwords match and email/WhatsApp don't already exist (or delete unverified accounts)"""
        if attrs['password'] != attrs['repeat_password']:
            raise serializers.ValidationError("Passwords do not match")
        
        email = attrs['email']
        whatsapp_number = attrs['email_or_whatsapp']
        
        # Check if email already exists - allow re-registration if not verified
        existing_user_email = NormalUser.objects.filter(email=email).first()
        if existing_user_email:
            if not existing_user_email.is_email_verified:
                # Delete unverified account to allow re-registration
                existing_user_email.delete()
            else:
                raise serializers.ValidationError({"email": "An account with this email already exists and is verified"})
        
        # Check if WhatsApp number already exists - allow re-registration if not verified
        existing_user_whatsapp = NormalUser.objects.filter(email_or_whatsapp=whatsapp_number).first()
        if existing_user_whatsapp:
            if not existing_user_whatsapp.is_email_verified:
                # Delete unverified account to allow re-registration
                existing_user_whatsapp.delete()
            else:
                raise serializers.ValidationError({"email_or_whatsapp": "An account with this WhatsApp number already exists and is verified"})
        
        return attrs
    
    def create(self, validated_data):
        """Create a new normal user with both email and WhatsApp - set as inactive until OTP verification"""
        password = validated_data.pop('password')
        validated_data.pop('repeat_password')  # Remove repeat_password
        
        # email and email_or_whatsapp are already in validated_data with correct field names
        
        # Create user as inactive and unverified - will be activated after OTP verification
        user = NormalUser.objects.create(
            **validated_data,
            is_active=False,  # Will be activated after OTP verification
            is_email_verified=False  # Will be set to True after OTP verification
        )
        user.set_password(password)
        
        return user


class NormalUserLoginSerializer(serializers.Serializer):
    """Serializer for normal user login"""
    
    email_or_whatsapp = serializers.CharField()
    password = serializers.CharField()
    
    def validate_email_or_whatsapp(self, value):
        """Validate login identifier - Afghanistan focused"""
        value = value.strip()
        
        # Check if it's an email
        email_validator = EmailValidator()
        try:
            email_validator(value)
            return value
        except ValidationError:
            pass
        
        # It's a phone number - validate Afghanistan format
        # Remove any spaces, dashes, parentheses, or other formatting
        cleaned_number = re.sub(r'[\s\-\(\)]', '', value)
        
        # Check if it's Afghan local format (starts with 0 and 10 digits total)
        if re.match(r'^0[7][0-9]{8}$', cleaned_number):
            # Convert to E.164 format for Afghanistan (+93)
            return '+93' + cleaned_number[1:]
        
        # Check if it's already in Afghan international format
        if re.match(r'^\+93[7][0-9]{8}$', cleaned_number):
            return cleaned_number
        
        # Check if it's a valid international number (E.164 format) - but not Afghan format
        if re.match(r'^\+[1-9]\d{6,14}$', cleaned_number) and not re.match(r'^\+93[7][0-9]{8}$', cleaned_number):
            return cleaned_number
            
        # Check if it's a valid number without + (add +) - but not Afghan format
        if re.match(r'^[1-9]\d{6,14}$', cleaned_number) and not re.match(r'^93[7][0-9]{8}$', cleaned_number):
            return '+' + cleaned_number
        
        raise serializers.ValidationError(
            "Please enter a valid email address or WhatsApp number. Afghanistan: 0701234567 or +93701234567. International: +1234567890"
        )
    
    def validate(self, attrs):
        """Validate login credentials"""
        email_or_whatsapp = attrs['email_or_whatsapp']
        password = attrs['password']
        
        # Find user by email or WhatsApp
        try:
            if '@' in email_or_whatsapp:
                user = NormalUser.objects.get(email=email_or_whatsapp)
            else:
                user = NormalUser.objects.get(email_or_whatsapp=email_or_whatsapp)
        except NormalUser.DoesNotExist:
            raise serializers.ValidationError("Invalid email/WhatsApp or password")
        
        # Check if user is active
        if not user.is_active:
            raise serializers.ValidationError("Account is deactivated")
        
        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email/WhatsApp or password")
        
        attrs['user'] = user
        return attrs


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification during registration - Email only"""
    
    email = serializers.EmailField(required=True, help_text="Email address that received the OTP")
    otp_code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_email(self, value):
        """Validate email format"""
        return value.strip().lower()
    
    def validate(self, attrs):
        """Validate OTP - Email only"""
        email = attrs['email']
        otp_code = attrs['otp_code']
        
        # Find user by email
        try:
            user = NormalUser.objects.get(email=email)
        except NormalUser.DoesNotExist:
            raise serializers.ValidationError("User not found with this email")
        
        # Find valid OTP - get the latest OTP first, then check if code matches
        try:
            otp = NormalUserOTP.objects.filter(
                user=user,
                otp_type='email',
                contact_info=email,
                is_used=False
            ).latest('created_at')
            
            # Check if the OTP code matches
            if otp.otp_code != otp_code:
                raise serializers.ValidationError("Invalid OTP code")
            
            # Check if OTP is expired
            if otp.is_expired():
                raise serializers.ValidationError("OTP has expired")
            
            attrs['user'] = user
            attrs['otp'] = otp
            attrs['otp_type'] = 'email'  # OTP type is always email for normal user registration
            
        except NormalUserOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP code")
        
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password request - Email only"""
    
    email = serializers.EmailField(required=True, help_text="Email address for password reset")
    
    def validate_email_or_whatsapp(self, value):
        """Validate contact info - Afghanistan focused"""
        value = value.strip()
        
        # Check if it's an email
        email_validator = EmailValidator()
        try:
            email_validator(value)
            return value
        except ValidationError:
            pass
        
        # It's a phone number - validate Afghanistan format
        # Remove any spaces, dashes, parentheses, or other formatting
        cleaned_number = re.sub(r'[\s\-\(\)]', '', value)
        
        # Check if it's Afghan local format (starts with 0 and 10 digits total)
        if re.match(r'^0[7][0-9]{8}$', cleaned_number):
            # Convert to E.164 format for Afghanistan (+93)
            return '+93' + cleaned_number[1:]
        
        # Check if it's already in Afghan international format
        if re.match(r'^\+93[7][0-9]{8}$', cleaned_number):
            return cleaned_number
        
        # Check if it's a valid international number (E.164 format) - but not Afghan format
        if re.match(r'^\+[1-9]\d{6,14}$', cleaned_number) and not re.match(r'^\+93[7][0-9]{8}$', cleaned_number):
            return cleaned_number
            
        # Check if it's a valid number without + (add +) - but not Afghan format
        if re.match(r'^[1-9]\d{6,14}$', cleaned_number) and not re.match(r'^93[7][0-9]{8}$', cleaned_number):
            return '+' + cleaned_number
        
        raise serializers.ValidationError(
            "Please enter a valid email address or WhatsApp number. Afghanistan: 0701234567 or +93701234567. International: +1234567890"
        )
    
    def validate(self, attrs):
        """Validate that user exists"""
        email_or_whatsapp = attrs['email_or_whatsapp']
        
        try:
            if '@' in email_or_whatsapp:
                user = NormalUser.objects.get(email=email_or_whatsapp)
            else:
                user = NormalUser.objects.get(email_or_whatsapp=email_or_whatsapp)
            
            if not user.is_active:
                raise serializers.ValidationError("Account is deactivated")
            
            attrs['user'] = user
            
        except NormalUser.DoesNotExist:
            raise serializers.ValidationError("No account found with this email/WhatsApp number")
        
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset"""
    
    email_or_whatsapp = serializers.CharField()
    otp_code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(min_length=6)
    repeat_password = serializers.CharField()
    
    def validate_new_password(self, value):
        """Validate password strength"""
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character")
        
        return value
    
    def validate(self, attrs):
        """Validate passwords match and OTP"""
        if attrs['new_password'] != attrs['repeat_password']:
            raise serializers.ValidationError("Passwords do not match")
        
        email_or_whatsapp = attrs['email_or_whatsapp']
        otp_code = attrs['otp_code']
        
        # Find user
        try:
            if '@' in email_or_whatsapp:
                user = NormalUser.objects.get(email=email_or_whatsapp)
            else:
                user = NormalUser.objects.get(email_or_whatsapp=email_or_whatsapp)
        except NormalUser.DoesNotExist:
            raise serializers.ValidationError("User not found")
        
        # Find valid OTP - get the latest OTP first, then check if code matches
        try:
            otp = NormalUserOTP.objects.filter(
                user=user,
                otp_type='password_reset',
                contact_info=email_or_whatsapp,
                is_used=False
            ).latest('created_at')
            
            # Check if the OTP code matches
            if otp.otp_code != otp_code:
                raise serializers.ValidationError("Invalid OTP code")
            
            # Check if OTP is expired
            if otp.is_expired():
                raise serializers.ValidationError("OTP has expired")
            
            attrs['user'] = user
            attrs['otp'] = otp
            
        except NormalUserOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP code")
        
        return attrs


class ResendOTPSerializer(serializers.Serializer):
    """Serializer for resending OTP - Email only"""
    
    email = serializers.EmailField(required=True, help_text="Email address to resend OTP to")
    otp_type = serializers.ChoiceField(choices=['email', 'password_reset'], required=True)
    
    def validate_email(self, value):
        """Validate email format"""
        return value.strip().lower()
    
    def validate(self, attrs):
        """Validate that user exists"""
        email = attrs['email']
        otp_type = attrs['otp_type']
        
        try:
            user = NormalUser.objects.get(email=email)
            
            # Don't check if deactivated - allow password reset for deactivated accounts
            # if not user.is_active:
            #     raise serializers.ValidationError("Account is deactivated")
            
            # For 'email' type, check if already verified (but allow password_reset even if verified)
            if otp_type == 'email' and user.is_email_verified:
                raise serializers.ValidationError("Email is already verified")
            
            attrs['user'] = user
            
        except NormalUser.DoesNotExist:
            raise serializers.ValidationError("No account found with this email address")
        
        return attrs


class NormalUserProfileSerializer(serializers.ModelSerializer):
    """Serializer for normal user profile"""
    
    class Meta:
        model = NormalUser
        fields = ['user_id', 'full_name', 'email', 'email_or_whatsapp', 
                 'is_email_verified', 'is_whatsapp_verified', 'is_active',
                 'created_at', 'last_login']
        read_only_fields = ['user_id', 'is_email_verified', 'is_whatsapp_verified', 
                           'created_at', 'last_login']
