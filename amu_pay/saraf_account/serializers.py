from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import SarafAccount, SarafOTP, AmuPayCode


class SarafListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Saraf accounts with basic information
    """
    saraf_logo = serializers.SerializerMethodField()
    
    class Meta:
        model = SarafAccount
        fields = ['saraf_id', 'exchange_name', 'province', 'saraf_logo', 'email_or_whatsapp_number', 'saraf_location_google_map']
    
    def get_saraf_logo(self, obj):
        """
        Return full URL for saraf_logo if it exists
        """
        if obj.saraf_logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.saraf_logo.url)
            return obj.saraf_logo.url
        return None


class SarafDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Saraf account information
    """
    class Meta:
        model = SarafAccount
        fields = [
            'saraf_id', 'full_name', 'exchange_name', 'email_or_whatsapp_number',
            'license_no', 'saraf_address', 'saraf_location_google_map', 'province', 'saraf_logo',
            'is_email_verified', 'is_whatsapp_verified', 'is_active', 'created_at'
        ]
        read_only_fields = ['saraf_id', 'created_at', 'is_email_verified', 'is_whatsapp_verified']


class SarafRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for Saraf account registration - Both email and WhatsApp required"""
    password = serializers.CharField(write_only=True, min_length=6)
    repeat_password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True, help_text="Email address for OTP verification")
    email_or_whatsapp_number = serializers.CharField(required=True, help_text="WhatsApp number (e.g., 0790976268 or +93790976268)")
    
    class Meta:
        model = SarafAccount
        fields = [
            'full_name', 'exchange_name', 'email', 'email_or_whatsapp_number',
            'license_no', 'amu_pay_code', 'saraf_address', 'saraf_location_google_map', 'province',
            'password', 'repeat_password'
        ]
    
    def validate_email_or_whatsapp_number(self, value):
        """Validate WhatsApp number format ONLY (no emails allowed)"""
        if not value:
            raise serializers.ValidationError("WhatsApp number is required")
        
        # Should NOT be an email
        if '@' in value:
            raise serializers.ValidationError("This field should contain a WhatsApp number only. Please use the 'email' field for your email address.")
        
        # It's a phone number - validate Afghanistan format
        import re
        # Remove any spaces, dashes, parentheses, or other formatting
        cleaned_number = re.sub(r'[\s\-\(\)]', '', value)
        
        # Check if it's Afghan local format (starts with 0 and 10 digits total)
        if re.match(r'^0[7][0-9]{8}$', cleaned_number):
            # Valid Afghanistan local format
            pass
        elif re.match(r'^\+93[7][0-9]{8}$', cleaned_number):
            # Valid Afghanistan international format
            pass
        elif re.match(r'^\+[1-9]\d{6,14}$', cleaned_number):
            # Valid international format
            pass
        elif re.match(r'^[1-9]\d{6,14}$', cleaned_number):
            # Valid number without + prefix
            pass
        else:
            raise serializers.ValidationError(
                "Phone number must be in valid format. Afghanistan: 0701234567 or +93701234567. International: +1234567890"
            )
        
        return value
    
    def validate_amu_pay_code(self, value):
        """Validate AmuPay code exists and is unused"""
        if not value:
            raise serializers.ValidationError("AmuPay code is required")
        
        # Check if code exists and is unused
        try:
            amu_pay_code = AmuPayCode.objects.get(code=value.upper(), is_used=False)
            return value.upper()  # Return uppercase version
        except AmuPayCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used AmuPay code")
    
    def validate(self, data):
        """Validate password match and check duplicates"""
        if data['password'] != data['repeat_password']:
            raise serializers.ValidationError("Passwords do not match")
        
        # Check if email already exists
        if SarafAccount.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "A Saraf account with this email already exists"})
        
        # Check if WhatsApp number already exists
        if SarafAccount.objects.filter(email_or_whatsapp_number=data['email_or_whatsapp_number']).exists():
            raise serializers.ValidationError({"email_or_whatsapp_number": "A Saraf account with this WhatsApp number already exists"})
        
        return data
    
    def create(self, validated_data):
        """Create Saraf account with hashed password"""
        # Remove fields not needed for model creation
        password = validated_data.pop('password')
        repeat_password = validated_data.pop('repeat_password')
        
        # Get the AmuPay code before creating the account
        amu_pay_code_value = validated_data.get('amu_pay_code')
        
        # Create account
        saraf_account = SarafAccount.objects.create(**validated_data)
        
        # Set password
        saraf_account.set_password(password)
        
        # Mark AmuPay code as used
        if amu_pay_code_value:
            try:
                amu_pay_code = AmuPayCode.objects.get(code=amu_pay_code_value, is_used=False)
                amu_pay_code.mark_as_used(saraf_account)
            except AmuPayCode.DoesNotExist:
                # This shouldn't happen due to validation, but handle gracefully
                pass
        
        return saraf_account


class SarafLoginSerializer(serializers.Serializer):
    """Serializer for Saraf account login"""
    email_or_whatsapp_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate_email_or_whatsapp_number(self, value):
        """Validate email or WhatsApp number exists - check both email and email_or_whatsapp_number fields (like normal user login)"""
        try:
            if '@' in value:
                # If it's an email, check the email field
                saraf_account = SarafAccount.objects.get(email=value.lower())
            else:
                # If it's a WhatsApp number, check the email_or_whatsapp_number field
                saraf_account = SarafAccount.objects.get(email_or_whatsapp_number=value)
            
            if not saraf_account.is_active:
                raise serializers.ValidationError("Account is not active")
            return value
        except SarafAccount.DoesNotExist:
            raise serializers.ValidationError("Account not found")


class SarafOTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification - Email only"""
    email = serializers.EmailField(required=True, help_text="Email address that received the OTP")
    otp_code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_email(self, value):
        """Validate email exists"""
        try:
            SarafAccount.objects.get(email=value)
            return value.lower()
        except SarafAccount.DoesNotExist:
            raise serializers.ValidationError("Saraf account not found with this email")


class SarafForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password request - Email only"""
    email = serializers.EmailField(required=True, help_text="Email address for password reset")
    
    def validate_email(self, value):
        """Validate email exists"""
        try:
            SarafAccount.objects.get(email=value.lower())
            return value.lower()
        except SarafAccount.DoesNotExist:
            raise serializers.ValidationError("Saraf account not found with this email")


class SarafResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset - Email only (Legacy - Token-based reset is now preferred)"""
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(min_length=6)
    repeat_password = serializers.CharField(min_length=6)
    
    def validate_email(self, value):
        """Validate email exists"""
        try:
            SarafAccount.objects.get(email=value.lower())
            return value.lower()
        except SarafAccount.DoesNotExist:
            raise serializers.ValidationError("Saraf account not found")
    
    def validate(self, data):
        """Validate password match"""
        if data['new_password'] != data['repeat_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data


class SarafResendOTPSerializer(serializers.Serializer):
    """Serializer for resending OTP - Email only"""
    email = serializers.EmailField(required=True, help_text="Email address to resend OTP to")
    
    def validate_email(self, value):
        """Validate email exists"""
        try:
            SarafAccount.objects.get(email=value.lower())
            return value.lower()
        except SarafAccount.DoesNotExist:
            raise serializers.ValidationError("Saraf account not found with this email")


class SarafProfileSerializer(serializers.ModelSerializer):
    """Serializer for Saraf account profile"""
    contact_type = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()
    
    class Meta:
        model = SarafAccount
        fields = [
            'saraf_id', 'full_name', 'exchange_name', 'email_or_whatsapp_number',
            'contact_type', 'license_no', 'amu_pay_code', 'saraf_address', 
            'province', 'is_email_verified', 'is_whatsapp_verified', 'is_verified',
            'is_active', 'created_at'
        ]
        read_only_fields = ['saraf_id', 'created_at', 'is_email_verified', 'is_whatsapp_verified']
    
    def get_contact_type(self, obj):
        """Get contact type (email or whatsapp)"""
        return 'email' if obj.is_email() else 'whatsapp'
    
    def get_is_verified(self, obj):
        """Get verification status"""
        return obj.is_verified()


class SarafPictureUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Saraf account picture fields
    """
    class Meta:
        model = SarafAccount
        fields = [
            'saraf_logo', 'saraf_logo_wallpeper', 
            'front_id_card', 'back_id_card'
        ]
        extra_kwargs = {
            'saraf_logo': {'required': False, 'allow_null': True},
            'saraf_logo_wallpeper': {'required': False, 'allow_null': True},
            'front_id_card': {'required': False, 'allow_null': True},
            'back_id_card': {'required': False, 'allow_null': True},
        }
    
    def validate_saraf_logo(self, value):
        """Validate logo image"""
        if value:
            return self._validate_image(value, "saraf_logo")
        return value
    
    def validate_saraf_logo_wallpeper(self, value):
        """Validate wallpaper image"""
        if value:
            return self._validate_image(value, "saraf_logo_wallpeper")
        return value
    
    def validate_front_id_card(self, value):
        """Validate front ID card image"""
        if value:
            return self._validate_image(value, "front_id_card")
        return value
    
    def validate_back_id_card(self, value):
        """Validate back ID card image"""
        if value:
            return self._validate_image(value, "back_id_card")
        return value
    
    def _validate_image(self, image, field_name):
        """Enhanced image validation with comprehensive checks"""
        import os
        from PIL import Image
        
        # Check file size (max 5MB)
        if image.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(f"{field_name} file size cannot exceed 5MB")
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        file_extension = os.path.splitext(image.name)[1].lower()
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(f"{field_name} must be in JPEG, PNG, or WEBP format")
        
        # Check image format and content
        try:
            # Reset file pointer to beginning
            image.seek(0)
            
            # Open image with PIL to validate content
            with Image.open(image) as img:
                # Check if it's a valid image format
                if img.format not in ['JPEG', 'PNG', 'WEBP']:
                    raise serializers.ValidationError(f"{field_name} must be in JPEG, PNG, or WEBP format")
                
                # Check image dimensions (prevent extremely large images)
                max_dimension = 4096  # Max width or height
                if img.width > max_dimension or img.height > max_dimension:
                    raise serializers.ValidationError(f"{field_name} dimensions cannot exceed {max_dimension}x{max_dimension} pixels")
                
                # Check if image is too small (prevent tiny images)
                min_dimension = 10
                if img.width < min_dimension or img.height < min_dimension:
                    raise serializers.ValidationError(f"{field_name} dimensions must be at least {min_dimension}x{min_dimension} pixels")
                
                # Verify image can be loaded properly
                img.verify()
            
            # Reset file pointer again after validation
            image.seek(0)
            
        except Exception as e:
            if isinstance(e, serializers.ValidationError):
                raise e
            raise serializers.ValidationError(f"{field_name} is not a valid image file: {str(e)}")
        
        return image


class SarafPictureDeleteSerializer(serializers.Serializer):
    """
    Serializer for deleting specific picture fields
    """
    PICTURE_FIELDS = [
        'saraf_logo', 'saraf_logo_wallpeper', 
        'front_id_card', 'back_id_card'
    ]
    
    fields_to_delete = serializers.ListField(
        child=serializers.ChoiceField(choices=PICTURE_FIELDS),
        min_length=1,
        max_length=4,
        help_text="List of picture fields to delete"
    )
    
    def validate_fields_to_delete(self, value):
        """Validate that fields exist and are unique"""
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate fields are not allowed")
        return value


class SarafPictureListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Saraf account pictures with full URLs
    """
    saraf_logo_url = serializers.SerializerMethodField()
    saraf_logo_wallpeper_url = serializers.SerializerMethodField()
    front_id_card_url = serializers.SerializerMethodField()
    back_id_card_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SarafAccount
        fields = [
            'saraf_id', 'full_name', 'exchange_name',
            'saraf_logo', 'saraf_logo_wallpeper', 
            'front_id_card', 'back_id_card',
            'saraf_logo_url', 'saraf_logo_wallpeper_url',
            'front_id_card_url', 'back_id_card_url'
        ]
        read_only_fields = ['saraf_id', 'full_name', 'exchange_name']
    
    def get_saraf_logo_url(self, obj):
        """Get full URL for saraf_logo"""
        if obj.saraf_logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.saraf_logo.url)
            return obj.saraf_logo.url
        return None
    
    def get_saraf_logo_wallpeper_url(self, obj):
        """Get full URL for saraf_logo_wallpeper"""
        if obj.saraf_logo_wallpeper:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.saraf_logo_wallpeper.url)
            return obj.saraf_logo_wallpeper.url
        return None
    
    def get_front_id_card_url(self, obj):
        """Get full URL for front_id_card"""
        if obj.front_id_card:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.front_id_card.url)
            return obj.front_id_card.url
        return None
    
    def get_back_id_card_url(self, obj):
        """Get full URL for back_id_card"""
        if obj.back_id_card:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.back_id_card.url)
            return obj.back_id_card.url
        return None