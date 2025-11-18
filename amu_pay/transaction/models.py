from django.db import models
from decimal import Decimal
from django.utils import timezone


class Transaction(models.Model):
    """Model for deposit and withdrawal transactions"""
    
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]
    
    transaction_id = models.BigAutoField(primary_key=True)
    saraf_account = models.ForeignKey(
        'saraf_account.SarafAccount',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    currency = models.ForeignKey(
        'currency.Currency',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Transaction amount"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Transaction description"
    )
    
    # Performer information (extracted from JWT)
    performer_user_id = models.BigIntegerField(help_text="Performer user ID")
    performer_user_type = models.CharField(max_length=20, help_text="User type (saraf/employee)")
    performer_full_name = models.CharField(max_length=255, help_text="Performer full name")
    performer_employee_id = models.BigIntegerField(
        blank=True,
        null=True,
        help_text="Employee ID (if performed by employee)"
    )
    performer_employee_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Employee name (if performed by employee)"
    )
    
    # Date and time
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Balance before and after transaction
    balance_before = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Balance before transaction"
    )
    balance_after = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Balance after transaction"
    )
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['saraf_account', 'currency']),
            models.Index(fields=['saraf_account', 'transaction_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['performer_user_id']),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.amount} {self.currency.currency_code} - {self.saraf_account.full_name}"

    def save(self, *args, **kwargs):
        """Save transaction and update balance"""
        from saraf_balance.models import SarafBalance
        
        # Get or create balance
        balance, created = SarafBalance.get_or_create_balance(
            self.saraf_account, 
            self.currency
        )
        
        # Record balance before transaction
        self.balance_before = balance.balance
        
        # Update balance
        balance.update_balance(self.amount, self.transaction_type)
        
        # Record balance after transaction
        self.balance_after = balance.balance
        
        super().save(*args, **kwargs)

    @classmethod
    def create_transaction(cls, saraf_account, currency, transaction_type, amount, description, user_info):
        """Create new transaction with user information"""
        transaction = cls(
            saraf_account=saraf_account,
            currency=currency,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            performer_user_id=user_info.get('user_id'),
            performer_user_type=user_info.get('user_type'),
            performer_full_name=user_info.get('full_name'),
            performer_employee_id=user_info.get('employee_id'),
            performer_employee_name=user_info.get('employee_name')
        )
        transaction.save()
        return transaction