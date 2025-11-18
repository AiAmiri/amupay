from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
import re
import secrets
import string
from utils.otp_utils import generate_otp_code_6_digits, calculate_otp_expiry


class NormalUser(models.Model):
    """Normal user account for customers"""
    
    user_id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=128)
    
    # Both email AND WhatsApp number are now required
    # email is used for OTP verification, email_or_whatsapp is for WhatsApp only (field name kept for compatibility)
    email = models.EmailField(max_length=128, unique=True)  # Required for OTP
    email_or_whatsapp = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid WhatsApp number')],
        help_text="WhatsApp number only (field name kept for API compatibility)"
    )  # WhatsApp number field
    
    password_hash = models.CharField(max_length=255, editable=False)
    
    # Verification status
    is_email_verified = models.BooleanField(default=False)
    is_whatsapp_verified = models.BooleanField(default=False)  # Not used anymore (no WhatsApp OTP)
    is_active = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Normal User'
        verbose_name_plural = 'Normal Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['email_or_whatsapp']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def clean(self):
        """Validate that both email and WhatsApp number are provided"""
        if not self.email:
            raise ValidationError("Email is required")
        
        # Validate WhatsApp number if provided
        if self.email_or_whatsapp:
            # Validate that email_or_whatsapp is NOT an email (should be WhatsApp only)
            if '@' in self.email_or_whatsapp:
                raise ValidationError("email_or_whatsapp field should contain a WhatsApp number only. Use the 'email' field for email addresses.")
        
        super().clean()
    
    def set_password(self, raw_password):
        """Securely hash and store the password"""
        if not self._validate_password(raw_password):
            raise ValidationError("Password does not meet security requirements")
        self.password_hash = make_password(raw_password)
        if self.pk:
            self.save(update_fields=['password_hash'])
    
    def check_password(self, raw_password):
        """Verify if the provided password matches the stored hash"""
        return check_password(raw_password, self.password_hash)
    
    def _validate_password(self, password):
        """Validate password strength"""
        if len(password) < 6:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True
    
    def get_password_requirements(self):
        """Return password requirements for user guidance"""
        return {
            'min_length': 6,
            'requires_uppercase': True,
            'requires_lowercase': True,
            'requires_digit': True,
            'requires_special': True,
            'requirements': [
                'At least 6 characters long',
                'At least one uppercase letter (A-Z)',
                'At least one lowercase letter (a-z)',
                'At least one digit (0-9)',
                'At least one special character (!@#$%^&*(),.?":{}|<>)'
            ]
        }
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])
    
    def is_verified(self):
        """Check if user has verified their email (email_or_whatsapp/WhatsApp doesn't require verification)"""
        return self.is_email_verified
    
    def get_primary_contact(self):
        """Get the primary contact method (email or WhatsApp)"""
        return self.email if self.email else self.email_or_whatsapp
    
    def save(self, *args, **kwargs):
        """Ensure password is never stored in plain text and validate contact info"""
        if hasattr(self, 'password'):
            delattr(self, 'password')
        self.full_clean()
        super().save(*args, **kwargs)


class NormalUserOTP(models.Model):
    """OTP verification codes for normal users"""
    
    OTP_TYPES = [
        ('email', 'Email OTP'),
        ('whatsapp', 'WhatsApp OTP'),
        ('password_reset', 'Password Reset OTP'),
    ]
    
    otp_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(NormalUser, on_delete=models.CASCADE, related_name='otps')
    otp_type = models.CharField(max_length=20, choices=OTP_TYPES)
    contact_info = models.CharField(max_length=128, help_text="Email or WhatsApp number")
    otp_code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Normal User OTP'
        verbose_name_plural = 'Normal User OTPs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'otp_type']),
            models.Index(fields=['contact_info']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.otp_type} - {self.otp_code}"
    
    @classmethod
    def generate_otp(cls):
        """Generate a 6-digit OTP code"""
        return generate_otp_code_6_digits()
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self):
        """Mark OTP as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
