from django.contrib import admin
from .models import EmailOTP

# Register your models here.


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("email", "otp_code", "is_active", "created_at", "expires_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("email",)
    readonly_fields = ("otp_code", "created_at", "expires_at")