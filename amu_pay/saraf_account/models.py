from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
import re
import secrets
import string


# Default Employee Permissions Dictionary - Each employee gets their own copy
# All permissions are set to True by default
DEFAULT_EMPLOYEE_PERMISSIONS = {
    'edit_profile': True,
    'chat': True,
    'send_transfer': True,
    'receive_transfer': True,
    'take_money': True,
    'give_money': True,
    'loans': True,
    'add_employee': True,
    'change_password': True,
    'see_how_did_works': True,
    'create_exchange': True,
    'view_history': True,
    'create_accounts': True,
    'delete_accounts': True,
    'add_posts': True,
    'deliver_amount': True,
    'withdraw_to_customer': True,
    'deposit_to_customer': True,
    'withdraw_from_account': True,
    'deposit_to_account': True,
    'add_currency': True,
}

# Permission descriptions for UI display
PERMISSION_DESCRIPTIONS = {
    'edit_profile': 'Edit Profile',
    'chat': 'Chat',
    'send_transfer': 'Send Transfer',
    'receive_transfer': 'Receive Transfer',
    'take_money': 'Take Money',
    'give_money': 'Give Money',
    'loans': 'Loans',
    'add_employee': 'Add Employee',
    'change_password': 'Change Password',
    'see_how_did_works': 'See How Did Works',
    'create_exchange': 'Create Exchange',
    'view_history': 'View History',
    'create_accounts': 'Create Accounts',
    'delete_accounts': 'Delete Accounts',
    'add_posts': 'Add Posts',
    'deliver_amount': 'Deliver Amount',
    'withdraw_to_customer': 'Withdraw to Customer',
    'deposit_to_customer': 'Deposit to Customer',
    'withdraw_from_account': 'Withdraw from Account',
    'deposit_to_account': 'Deposit to Account',
    'add_currency': 'Add Currency',
}


# Create your models here.
class SarafAccount(models.Model):
    saraf_id = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=128)
    exchange_name = models.CharField(max_length=128, null=True, help_text="Registered exchange business name")
    
    # Both email AND WhatsApp are now required
    # email is used for OTP verification, email_or_whatsapp_number is for WhatsApp only (no OTP)
    email = models.EmailField(max_length=128, unique=True, null=True, blank=True)  # Required for OTP
    email_or_whatsapp_number = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text="WhatsApp number only (field name kept for API compatibility)"
    )  # WhatsApp number field
    
    license_no = models.CharField(max_length=64, unique=True, null=True, blank=True)
    amu_pay_code = models.CharField(max_length=32)
    saraf_address = models.CharField(max_length=255, blank=True)
    saraf_location_google_map = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Google Maps location link for the saraf"
    )
    province = models.CharField('Province', max_length=64)
    password_hash = models.CharField(max_length=255, editable=False)
    is_email_verified = models.BooleanField(default=False)
    is_whatsapp_verified = models.BooleanField(default=False)  # Not used anymore (no WhatsApp OTP)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    saraf_logo = models.ImageField(upload_to='saraf_photos/', null=True, blank=True)
    saraf_logo_wallpeper = models.ImageField(upload_to='saraf_photos/', null=True, blank=True)
    front_id_card = models.ImageField(upload_to='saraf_photos/', null=True, blank=True)
    back_id_card = models.ImageField(upload_to='saraf_photos/', null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Saraf Profile'
        verbose_name_plural = 'Saraf Profiles'

    def __str__(self):
        return f"{self.full_name} ({self.exchange_name or '-'})"

    def clean(self):
        """Validate that both email and WhatsApp are provided"""
        super().clean()
        if not self.email:
            raise ValidationError("Email is required")
        if not self.email_or_whatsapp_number:
            raise ValidationError("WhatsApp number is required")
        
        # Validate that email_or_whatsapp_number is NOT an email (should be WhatsApp only)
        if '@' in self.email_or_whatsapp_number:
            raise ValidationError("email_or_whatsapp_number field should contain a WhatsApp number only. Use the 'email' field for email addresses.")
        
        # Validate phone number format
        phone_validator = RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid WhatsApp number')
        phone_validator(self.email_or_whatsapp_number)

    def is_email(self):
        """Deprecated - email is now in separate field. Always returns True."""
        return True

    def is_whatsapp(self):
        """Deprecated - WhatsApp is now in email_or_whatsapp_number field"""
        return bool(self.email_or_whatsapp_number)

    def is_verified(self):
        """Check if email is verified (WhatsApp doesn't require verification)"""
        return self.is_email_verified

    def update_verification_status(self, verified=True):
        """Update email verification status (WhatsApp doesn't require verification)"""
        self.is_email_verified = verified
        self.save(update_fields=['is_email_verified'])

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

    def save(self, *args, **kwargs):
        """Ensure password is never stored in plain text and validate AmuPay code"""
        from django.db import transaction
        
        if hasattr(self, 'password'):
            delattr(self, 'password')
        
        # Validate and mark AmuPay code as used for NEW accounts only
        is_new = self.pk is None
        if is_new and self.amu_pay_code:
            # Use transaction to ensure atomicity
            with transaction.atomic():
                # Lock the code row to prevent concurrent usage
                try:
                    amu_pay_code_obj = AmuPayCode.objects.select_for_update().get(
                        code=self.amu_pay_code.upper(),
                        is_used=False
                    )
                except AmuPayCode.DoesNotExist:
                    raise ValidationError(
                        f"AmuPay code '{self.amu_pay_code}' is invalid or already used. "
                        "Please use a valid, unused AmuPay code."
                    )
                
                # Save the account first
                self.full_clean()
                super().save(*args, **kwargs)
                
                # Then mark code as used (atomic operation)
                amu_pay_code_obj.mark_as_used(self)
        else:
            # Existing account or no code - just save normally
            self.full_clean()
            super().save(*args, **kwargs)


class SarafEmployee(models.Model):
    employee_id = models.BigAutoField(primary_key=True)
    saraf_account = models.ForeignKey(SarafAccount, on_delete=models.CASCADE, related_name='employees')
    username = models.CharField(max_length=64, help_text="Employee username for login")
    full_name = models.CharField(max_length=128, help_text="Employee's full name")
    password_hash = models.CharField(max_length=255, editable=False)
    permissions = models.JSONField(
        default=dict,
        help_text="Individual permissions dictionary for this employee"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        unique_together = [('saraf_account', 'username')]
        indexes = [
            models.Index(fields=['saraf_account', 'username']),
            models.Index(fields=['saraf_account', 'is_active']),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.username}) - {self.saraf_account.full_name}"

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

    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

    def initialize_permissions(self):
        """Initialize employee with default permissions"""
        if not self.permissions:
            self.permissions = DEFAULT_EMPLOYEE_PERMISSIONS.copy()
            if self.pk:
                self.save(update_fields=['permissions'])

    def has_permission(self, permission_name):
        """Check if employee has a specific permission"""
        if not self.permissions:
            self.initialize_permissions()
        return self.permissions.get(permission_name, False)

    def set_permission(self, permission_name, allowed):
        """Set a specific permission for this employee"""
        if not self.permissions:
            self.initialize_permissions()
        if permission_name in PERMISSION_DESCRIPTIONS:
            self.permissions[permission_name] = bool(allowed)
            if self.pk:
                self.save(update_fields=['permissions'])
        else:
            raise ValueError(f"Invalid permission: {permission_name}")

    def get_all_permissions(self):
        """Get all permissions with descriptions for this employee"""
        if not self.permissions:
            self.initialize_permissions()
        
        return {
            permission: {
                'allowed': self.permissions.get(permission, False),
                'description': PERMISSION_DESCRIPTIONS.get(permission, permission.replace('_', ' ').title())
            }
            for permission in PERMISSION_DESCRIPTIONS.keys()
        }

    def update_permissions(self, permissions_dict):
        """Update multiple permissions at once"""
        if not self.permissions:
            self.initialize_permissions()
        
        for permission, allowed in permissions_dict.items():
            if permission in PERMISSION_DESCRIPTIONS:
                self.permissions[permission] = bool(allowed)
            else:
                raise ValueError(f"Invalid permission: {permission}")
        
        if self.pk:
            self.save(update_fields=['permissions'])

    def reset_permissions_to_default(self):
        """Reset employee permissions to default values"""
        self.permissions = DEFAULT_EMPLOYEE_PERMISSIONS.copy()
        if self.pk:
            self.save(update_fields=['permissions'])

    def save(self, *args, **kwargs):
        """Ensure permissions are initialized on save"""
        if not self.permissions:
            self.permissions = DEFAULT_EMPLOYEE_PERMISSIONS.copy()
        super().save(*args, **kwargs)


class ActionLog(models.Model):
    USER_TYPE_CHOICES = [
        ('saraf', 'Saraf'),
        ('employee', 'Employee'),
    ]

    saraf = models.ForeignKey(SarafAccount, on_delete=models.CASCADE, related_name='action_logs')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    user_id = models.BigIntegerField()
    user_name = models.CharField(max_length=128)
    action_type = models.CharField(max_length=50)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Action Log'
        verbose_name_plural = 'Action Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['saraf', 'timestamp']),
            models.Index(fields=['saraf', 'user_type']),
            models.Index(fields=['saraf', 'action_type']),
        ]

    def __str__(self):
        return f"{self.user_name} ({self.user_type}) - {self.action_type} at {self.timestamp}"


class AmuPayCode(models.Model):
    """One-time use codes for Saraf accounts"""
    
    code = models.CharField(
        max_length=12, 
        unique=True, 
        help_text="Unique AmuPay code"
    )
    description = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Optional description for this code"
    )
    is_used = models.BooleanField(
        default=False, 
        help_text="Whether this code has been used"
    )
    used_by = models.ForeignKey(
        SarafAccount, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Which Saraf account used this code"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(
        max_length=128, 
        default='Admin',
        help_text="Who created this code"
    )

    class Meta:
        verbose_name = 'AmuPay Code'
        verbose_name_plural = 'AmuPay Codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_used']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        status = "Used" if self.is_used else "Available"
        return f"{self.code} - {status}"

    @classmethod
    def generate_code(cls):
        """Generate a unique 12-character code (4 letters + 4 numbers + 4 letters)"""
        while True:
            # Generate code: ABCD1234EFGH format
            letters1 = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(4))
            numbers = ''.join(secrets.choice(string.digits) for _ in range(4))
            letters2 = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(4))
            code = f"{letters1}{numbers}{letters2}"
            
            # Check if code already exists
            if not cls.objects.filter(code=code).exists():
                return code

    def mark_as_used(self, saraf_account):
        """Mark this code as used by a specific Saraf account - atomic operation"""
        # Use update() to atomically set is_used and prevent race conditions
        # This ensures only one request can successfully mark the code as used
        updated = self.__class__.objects.filter(
            pk=self.pk,
            is_used=False  # Only update if still unused
        ).update(
            is_used=True,
            used_by=saraf_account,
            used_at=timezone.now()
        )
        
        if updated == 0:
            # Code was already used by another request (race condition detected)
            # Refresh to get the actual used_by information
            self.refresh_from_db()
            raise ValidationError(
                f"AmuPay code {self.code} was already used by {self.used_by.full_name if self.used_by else 'another registration'}"
            )
        
        # Refresh to get updated values
        self.refresh_from_db()

    @classmethod
    def validate_and_use_code(cls, code):
        """Validate a code and return it if valid and unused"""
        try:
            reg_code = cls.objects.get(code=code.upper(), is_used=False)
            return reg_code
        except cls.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        """Auto-generate code if not provided and ensure uppercase"""
        if not self.code:
            self.code = self.generate_code()
        self.code = self.code.upper()  # Always store in uppercase
        super().save(*args, **kwargs)


class SarafOTP(models.Model):
    """OTP verification for Saraf accounts"""
    
    OTP_TYPE_CHOICES = [
        ('email', 'Email OTP'),
        ('whatsapp', 'WhatsApp OTP'),
        ('password_reset', 'Password Reset OTP'),
    ]
    
    otp_id = models.BigAutoField(primary_key=True)
    saraf_account = models.ForeignKey(
        SarafAccount, 
        on_delete=models.CASCADE, 
        related_name='otps'
    )
    otp_type = models.CharField(
        max_length=20, 
        choices=OTP_TYPE_CHOICES,
        help_text="Type of OTP (email, whatsapp, password_reset)"
    )
    contact_info = models.CharField(
        max_length=128,
        help_text="Email address or WhatsApp number where OTP was sent"
    )
    otp_code = models.CharField(
        max_length=6,
        help_text="6-digit OTP code"
    )
    is_used = models.BooleanField(
        default=False,
        help_text="Whether this OTP has been used"
    )
    expires_at = models.DateTimeField(
        help_text="When this OTP expires"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Saraf OTP'
        verbose_name_plural = 'Saraf OTPs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['saraf_account', 'otp_type', 'is_used']),
            models.Index(fields=['contact_info', 'otp_type', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"OTP for {self.saraf_account.full_name} ({self.otp_type})"
    
    @classmethod
    def generate_otp(cls, saraf_account, otp_type, contact_info):
        """Generate a new OTP for Saraf account"""
        import random
        from django.utils import timezone
        from datetime import timedelta
        
        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Set expiration time (10 minutes from now)
        expires_at = timezone.now() + timedelta(minutes=10)
        
        # Mark all previous unused OTPs for this account/type/contact as used
        cls.objects.filter(
            saraf_account=saraf_account,
            otp_type=otp_type,
            contact_info=contact_info,
            is_used=False
        ).update(is_used=True)
        
        # Create new OTP
        otp = cls.objects.create(
            saraf_account=saraf_account,
            otp_type=otp_type,
            contact_info=contact_info,
            otp_code=otp_code,
            expires_at=expires_at
        )
        
        return otp
    
    def is_expired(self):
        """Check if OTP has expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if OTP is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self):
        """Mark OTP as used"""
        from django.utils import timezone
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])
    
    @classmethod
    def verify_otp(cls, saraf_account, otp_type, contact_info, otp_code):
        """Verify OTP and return the OTP object if valid"""
        try:
            # Get the latest unused OTP for this account/type/contact
            otp = cls.objects.filter(
                saraf_account=saraf_account,
                otp_type=otp_type,
                contact_info=contact_info,
                is_used=False
            ).order_by('-created_at').first()
            
            if otp and otp.otp_code == otp_code and otp.is_valid():
                return otp
            return None
        except cls.DoesNotExist:
            return None