from django.contrib import admin
from .models import SarafAccount, SarafEmployee, ActionLog, AmuPayCode, SarafOTP

@admin.register(SarafAccount)
class SarafAccountAdmin(admin.ModelAdmin):
    list_display = (
        'saraf_id', 'full_name', 'exchange_name', 'email_or_whatsapp_number', 
        'contact_type', 'is_email_verified', 'is_whatsapp_verified', 'license_no', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'is_email_verified', 'is_whatsapp_verified', 'created_at', 'updated_at')
    search_fields = ('full_name', 'exchange_name', 'email', 'email_or_whatsapp_number', 'license_no', 'amu_pay_code')
    ordering = ('-created_at',)
    readonly_fields = ('saraf_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('saraf_id', 'full_name', 'exchange_name', 'email', 'email_or_whatsapp_number', 'license_no', 'amu_pay_code')
        }),
        ('Address Information', {
            'fields': ('saraf_address', 'province'),
            'classes': ('collapse',)
        }),
        ('Verification Status', {
            'fields': ('is_email_verified', 'is_whatsapp_verified', 'is_active'),
        }),
        ('Documents', {
            'fields': ('saraf_logo', 'saraf_logo_wallpeper', 'front_id_card', 'back_id_card'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def contact_type(self, obj):
        """Display contact type (email or whatsapp)"""
        if not obj.email_or_whatsapp_number:
            return 'Not Set'
        return 'Email' if obj.is_email() else 'WhatsApp'
    contact_type.short_description = 'Contact Type'
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion of Saraf accounts"""
        return True
    
    def delete_model(self, request, obj):
        """Custom delete method to handle related records"""
        try:
            # Delete related records first
            SarafEmployee.objects.filter(saraf_account=obj).delete()
            ActionLog.objects.filter(saraf=obj).delete()
            SarafOTP.objects.filter(saraf_account=obj).delete()
            
            # Delete the main object
            super().delete_model(request, obj)
            
            # Log the deletion
            ActionLog.objects.create(
                saraf=None,  # No saraf since it's deleted
                user_type='admin',
                user_id=request.user.id,
                user_name=request.user.username,
                action_type='delete_saraf_account',
                description=f'Deleted Saraf account: {obj.full_name} (ID: {obj.saraf_id})'
            )
        except Exception as e:
            # If there's an error, log it but don't fail
            print(f"Error during deletion: {str(e)}")
            super().delete_model(request, obj)

@admin.register(SarafEmployee)
class SarafEmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_id', 'username', 'full_name', 'saraf_account', 'is_active', 'created_at', 'last_login'
    )
    list_filter = ('is_active', 'created_at', 'last_login', 'saraf_account')
    search_fields = ('username', 'full_name', 'saraf_account__full_name', 'saraf_account__exchange_name')
    ordering = ('-created_at',)
    readonly_fields = ('employee_id', 'created_at', 'updated_at', 'last_login')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('saraf_account')

    def saraf_account(self, obj):
        return f"{obj.saraf_account.full_name} ({obj.saraf_account.exchange_name})"
    saraf_account.short_description = 'Saraf Account'

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 'saraf', 'user_type', 'user_name', 'action_type', 'ip_address'
    )
    list_filter = ('user_type', 'action_type', 'timestamp', 'saraf')
    search_fields = ('user_name', 'action_type', 'description', 'saraf__full_name')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'saraf', 'user_type', 'user_id', 'user_name', 'action_type', 'description', 'ip_address', 'user_agent', 'metadata')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('saraf')

    def saraf(self, obj):
        return f"{obj.saraf.full_name} ({obj.saraf.exchange_name})"
    saraf.short_description = 'Saraf Account'

    def has_add_permission(self, request):
        return False  # Prevent manual creation of action logs


@admin.register(AmuPayCode)
class AmuPayCodeAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'description', 'is_used', 'used_by', 'created_at', 'used_at', 'created_by'
    )
    list_filter = ('is_used', 'created_at', 'used_at')
    search_fields = ('code', 'description', 'used_by__full_name', 'created_by')
    ordering = ('-created_at',)
    readonly_fields = ('code', 'used_by', 'used_at')
    
    fieldsets = (
        ('Code Information', {
            'fields': ('code', 'description', 'created_by')
        }),
        ('Usage Status', {
            'fields': ('is_used', 'used_by', 'used_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Save model - AmuPay code validation is handled in model's save() method"""
        # Model's save() method will handle AmuPay code validation and marking
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        """Only allow deletion of unused codes"""
        if obj and obj.is_used:
            return False
        return super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        """Optimize queries with select_related"""
        return super().get_queryset(request).select_related('used_by')

    actions = ['generate_bulk_codes']

    def generate_bulk_codes(self, request, queryset):
        """Admin action to generate multiple codes at once"""
        count = 0
        for i in range(10):  # Generate 10 codes
            AmuPayCode.objects.create(
                description=f"Bulk generated code {i+1}",
                created_by=request.user.username
            )
            count += 1
        
        self.message_user(request, f"Successfully generated {count} AmuPay codes.")
    
    generate_bulk_codes.short_description = "Generate 10 new AmuPay codes"


@admin.register(SarafOTP)
class SarafOTPAdmin(admin.ModelAdmin):
    list_display = (
        'otp_id', 'saraf_account', 'otp_type', 'contact_info', 'is_used', 'expires_at', 'created_at'
    )
    list_filter = ('otp_type', 'is_used', 'created_at', 'expires_at')
    search_fields = ('saraf_account__full_name', 'saraf_account__exchange_name', 'contact_info', 'otp_code')
    ordering = ('-created_at',)
    readonly_fields = ('otp_id', 'otp_code', 'created_at', 'used_at')
    
    fieldsets = (
        ('OTP Information', {
            'fields': ('saraf_account', 'otp_type', 'contact_info', 'otp_code')
        }),
        ('Status', {
            'fields': ('is_used', 'expires_at', 'used_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queries with select_related"""
        return super().get_queryset(request).select_related('saraf_account')
    
    def saraf_account(self, obj):
        """Display Saraf account name"""
        return f"{obj.saraf_account.full_name} ({obj.saraf_account.exchange_name})"
    saraf_account.short_description = 'Saraf Account'
    
    def has_add_permission(self, request):
        """Prevent manual creation of OTPs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of OTPs"""
        return False
