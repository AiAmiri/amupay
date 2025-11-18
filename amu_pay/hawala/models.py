from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class HawalaTransaction(models.Model):
    """
    Model for Hawala (Money Transfer) transactions
    Supports both modes: internal (both sarafs use app) and external (one saraf uses app)
    """
    
    # Transaction Status Choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('completed', 'Completed'),
    ]
    
    # Transaction Mode Choices
    MODE_CHOICES = [
        ('internal', 'Internal (Both sarafs use app)'),
        ('external_sender', 'External (Only sender uses app)'),
        ('external_receiver', 'External (Only receiver uses app)'),
    ]
    
    # Primary transaction identifier (manually entered by saraf)
    hawala_number = models.CharField(
        max_length=20,
        primary_key=True,
        help_text="Hawala number manually entered by saraf (used as primary key)"
    )
    
    # Sender Information
    sender_name = models.CharField(
        max_length=128,
        help_text="Name of the person sending money"
    )
    sender_phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')],
        help_text="Sender's phone number"
    )
    
    # Receiver Information
    receiver_name = models.CharField(
        max_length=128,
        help_text="Name of the person receiving money"
    )
    receiver_phone = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')],
        help_text="Receiver's phone number (filled by receiving saraf)"
    )
    receiver_photo = models.ImageField(
        upload_to='hawala_receiver_photos/',
        null=True,
        blank=True,
        help_text="Photo of receiver (taken by receiving saraf)"
    )
    
    # Transaction Details
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Transfer amount"
    )
    currency = models.ForeignKey(
        'currency.Currency',
        on_delete=models.PROTECT,
        help_text="Currency type"
    )
    transfer_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Transfer fee charged"
    )
    
    # Exchange Information
    sender_exchange = models.ForeignKey(
        'saraf_account.SarafAccount',
        on_delete=models.PROTECT,
        related_name='sent_hawalas',
        help_text="Sending exchange"
    )
    sender_exchange_name = models.CharField(
        max_length=128,
        help_text="Name of sending exchange"
    )
    
    # Destination Exchange Information
    destination_exchange_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="ID of destination exchange (if using app)"
    )
    destination_exchange_name = models.CharField(
        max_length=128,
        help_text="Name of destination exchange"
    )
    destination_exchange_address = models.TextField(
        help_text="Address of destination exchange"
    )
    
    # Transaction Status and Mode
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current transaction status"
    )
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        help_text="Transaction mode (internal/external)"
    )
    destination_saraf_uses_app = models.BooleanField(
        default=True,
        help_text="Does the destination saraf also use the app?"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional Information
    notes = models.TextField(
        blank=True,
        help_text="Additional notes or comments"
    )
    
    # Tracking fields
    created_by_employee = models.ForeignKey(
        'saraf_account.SarafEmployee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_hawalas',
        help_text="Employee who created this transaction"
    )
    received_by_employee = models.ForeignKey(
        'saraf_account.SarafEmployee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_hawalas',
        help_text="Employee who received this transaction"
    )

    class Meta:
        verbose_name = 'Hawala Transaction'
        verbose_name_plural = 'Hawala Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['hawala_number']),
            models.Index(fields=['sender_exchange', 'status']),
            models.Index(fields=['destination_exchange_id', 'status']),
            models.Index(fields=['status', 'mode']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Hawala #{self.hawala_number} - {self.sender_name} to {self.receiver_name}"

    def save(self, *args, **kwargs):
        """Validate hawala number is provided and unique"""
        if not self.hawala_number:
            raise ValidationError("Hawala number is required and must be manually entered.")
        
        # Check uniqueness if this is a new instance or hawala_number changed
        if not self.pk:
            # New instance - check if hawala_number already exists
            if HawalaTransaction.objects.filter(hawala_number=self.hawala_number).exists():
                raise ValidationError("Hawala number already exists. Please use a different number.")
        else:
            # Existing instance - check if hawala_number changed and if new value exists
            try:
                original = HawalaTransaction.objects.get(pk=self.pk)
                if original.hawala_number != self.hawala_number:
                    if HawalaTransaction.objects.filter(hawala_number=self.hawala_number).exists():
                        raise ValidationError("Hawala number already exists. Please use a different number.")
            except HawalaTransaction.DoesNotExist:
                pass  # If original doesn't exist, it's likely a new instance
        
        super().save(*args, **kwargs)

    def mark_as_sent(self):
        """Mark transaction as sent"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])

    def mark_as_received(self, receiver_phone=None, receiver_photo=None, employee=None):
        """Mark transaction as received with receiver details"""
        self.status = 'received'
        self.received_at = timezone.now()
        
        if receiver_phone:
            self.receiver_phone = receiver_phone
        if receiver_photo:
            self.receiver_photo = receiver_photo
        if employee:
            self.received_by_employee = employee
            
        self.save(update_fields=['status', 'received_at', 'receiver_phone', 'receiver_photo', 'received_by_employee'])

    def mark_as_completed(self, employee=None):
        """Mark transaction as completed and generate receipt"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
        
        # Generate receipt automatically
        self.generate_receipt(employee)

    def cancel_transaction(self):
        """Cancel the transaction"""
        self.status = 'cancelled'
        self.save(update_fields=['status'])

    def get_total_amount(self):
        """Get total amount including transfer fee"""
        return self.amount + self.transfer_fee

    def is_internal_transaction(self):
        """Check if this is an internal transaction (both sarafs use app)"""
        return self.mode == 'internal'

    def is_external_transaction(self):
        """Check if this is an external transaction"""
        return self.mode in ['external_sender', 'external_receiver']

    def can_be_received(self):
        """Check if transaction can be received"""
        return self.status in ['pending', 'sent']

    def can_be_completed(self):
        """Check if transaction can be completed"""
        return self.status in ['pending', 'sent']

    def generate_receipt(self, employee=None):
        """Generate receipt for completed transaction"""
        # Check if receipt already exists
        if hasattr(self, 'receipt') and self.receipt:
            return self.receipt
        
        # Create new receipt
        receipt = HawalaReceipt.objects.create(
            hawala_transaction=self,
            generated_by_employee=employee
        )
        return receipt


class HawalaReceipt(models.Model):
    """
    Model for Hawala transaction receipts
    Generated automatically when a transaction is completed
    """
    
    receipt_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique receipt ID"
    )
    
    hawala_transaction = models.OneToOneField(
        HawalaTransaction,
        on_delete=models.CASCADE,
        related_name='receipt',
        help_text="Associated hawala transaction"
    )
    
    # Receipt generation info
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by_employee = models.ForeignKey(
        'saraf_account.SarafEmployee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_receipts',
        help_text="Employee who generated the receipt"
    )
    
    # Receipt content (stored as JSON for flexibility)
    receipt_data = models.JSONField(
        help_text="Receipt data in structured format"
    )
    
    # Receipt status
    is_active = models.BooleanField(
        default=True,
        help_text="Is this receipt active and valid?"
    )
    
    class Meta:
        verbose_name = 'Hawala Receipt'
        verbose_name_plural = 'Hawala Receipts'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['hawala_transaction']),
            models.Index(fields=['generated_at']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"Receipt for Hawala #{self.hawala_transaction.hawala_number}"

    def generate_receipt_data(self):
        """Generate receipt data from hawala transaction"""
        hawala = self.hawala_transaction
        
        # Sender Saraf Information
        sender_saraf_info = {
            'saraf_name': hawala.sender_exchange.full_name,
            'exchange_name': hawala.sender_exchange.exchange_name,
            'saraf_id': hawala.sender_exchange.saraf_id,
            'phone': hawala.sender_exchange.email_or_whatsapp_number,
            'email': hawala.sender_exchange.email_or_whatsapp_number,
            'amu_pay_code': hawala.sender_exchange.amu_pay_code,
            'address': hawala.sender_exchange.saraf_address,
            'province': hawala.sender_exchange.province
        }
        
        # Hawala Information
        hawala_info = {
            'hawala_number': hawala.hawala_number,
            'amount': float(hawala.amount),
            'currency': {
                'code': hawala.currency.currency_code,
                'name': hawala.currency.currency_name,
                'symbol': hawala.currency.symbol
            },
            'transfer_fee': float(hawala.transfer_fee),
            'total_amount': float(hawala.get_total_amount()),
            'created_at': hawala.created_at.isoformat(),
            'completed_at': hawala.completed_at.isoformat() if hawala.completed_at else None,
            'status': hawala.status,
            'mode': hawala.mode,
            'notes': hawala.notes
        }
        
        # Employee Information
        employee_info = {
            'created_by': {
                'name': hawala.created_by_employee.full_name if hawala.created_by_employee else None,
                'username': hawala.created_by_employee.username if hawala.created_by_employee else None
            },
            'received_by': {
                'name': hawala.received_by_employee.full_name if hawala.received_by_employee else None,
                'username': hawala.received_by_employee.username if hawala.received_by_employee else None
            },
            'generated_by': {
                'name': self.generated_by_employee.full_name if self.generated_by_employee else None,
                'username': self.generated_by_employee.username if self.generated_by_employee else None
            }
        }
        
        # Receiver Information
        receiver_info = {
            'receiver_name': hawala.receiver_name,
            'receiver_phone': hawala.receiver_phone,
            'sender_name': hawala.sender_name,
            'sender_phone': hawala.sender_phone
        }
        
        # Destination Exchange Information
        destination_info = {
            'exchange_name': hawala.destination_exchange_name,
            'exchange_address': hawala.destination_exchange_address,
            'exchange_id': hawala.destination_exchange_id
        }
        
        # Combine all receipt data
        receipt_data = {
            'receipt_id': str(self.receipt_id),
            'generated_at': self.generated_at.isoformat(),
            'sender_saraf': sender_saraf_info,
            'hawala_details': hawala_info,
            'receiver_info': receiver_info,
            'destination_exchange': destination_info,
            'employee_info': employee_info,
            'receipt_type': 'hawala_completion_receipt',
            'version': '1.0'
        }
        
        return receipt_data

    def save(self, *args, **kwargs):
        """Auto-generate receipt data on save"""
        if not self.receipt_data:
            self.receipt_data = self.generate_receipt_data()
        super().save(*args, **kwargs)
