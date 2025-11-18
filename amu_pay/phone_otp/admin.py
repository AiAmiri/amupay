from django.contrib import admin
from .models import PhoneOTP

@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'otp_code', 'is_active', 'created_at', 'expires_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['phone_number']
    readonly_fields = ['created_at', 'expires_at']
    ordering = ['-created_at']
