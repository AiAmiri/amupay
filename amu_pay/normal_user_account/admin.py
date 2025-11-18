from django.contrib import admin
from .models import NormalUser, NormalUserOTP


@admin.register(NormalUser)
class NormalUserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'full_name', 'email', 'email_or_whatsapp', 
                   'is_email_verified', 'is_whatsapp_verified', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_email_verified', 'is_whatsapp_verified', 'created_at']
    search_fields = ['full_name', 'email', 'email_or_whatsapp']
    readonly_fields = ['user_id', 'created_at', 'updated_at', 'last_login']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user_id', 'full_name', 'email', 'email_or_whatsapp')
        }),
        ('Verification Status', {
            'fields': ('is_email_verified', 'is_whatsapp_verified', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['password_hash']
        return self.readonly_fields


@admin.register(NormalUserOTP)
class NormalUserOTPAdmin(admin.ModelAdmin):
    list_display = ['otp_id', 'user', 'otp_type', 'contact_info', 'otp_code', 
                   'is_used', 'expires_at', 'created_at']
    list_filter = ['otp_type', 'is_used', 'created_at', 'expires_at']
    search_fields = ['user__full_name', 'contact_info', 'otp_code']
    readonly_fields = ['otp_id', 'created_at', 'used_at']
    fieldsets = (
        ('OTP Information', {
            'fields': ('otp_id', 'user', 'otp_type', 'contact_info', 'otp_code')
        }),
        ('Status', {
            'fields': ('is_used', 'expires_at', 'used_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
