from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string
from utils.otp_utils import generate_otp_code_6_digits, calculate_otp_expiry

class PhoneOTP(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)  # E.164 format
    otp_code = models.CharField(max_length=6)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = self.generate_otp()
        if not self.expires_at:
            self.expires_at = calculate_otp_expiry(10)  # OTP expires in 10 minutes
        super().save(*args, **kwargs)
    
    def generate_otp(self):
        """Generate a 6-digit numeric OTP"""
        return generate_otp_code_6_digits()
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.phone_number} - {self.otp_code}"
    
    class Meta:
        verbose_name = "Phone OTP"
        verbose_name_plural = "Phone OTPs"
