from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class ExchangeTransaction(models.Model):
    """
    Model for currency exchange transactions
    """
    TRANSACTION_TYPE_CHOICES = [
        ('person', 'Person'),
        ('exchanger', 'Exchanger'),
        ('customer', 'Customer'),
    ]
    
    # Basic transaction information
    name = models.CharField(
        max_length=100,
        help_text="Name of the exchange partner or customer"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        default='customer',
        help_text="Type of exchange transaction"
    )
    
    # Currency information
    sell_currency = models.CharField(
        max_length=3,
        help_text="Currency code being sold (e.g. USD, AFN)"
    )
    sell_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Amount of currency being sold"
    )
    buy_currency = models.CharField(
        max_length=3,
        help_text="Currency code being bought (e.g. USD, AFN)"
    )
    buy_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Amount of currency being bought"
    )
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Exchange rate (buy_amount per 1 sell_amount)"
    )
    
    # Additional information
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the transaction"
    )
    transaction_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time of the transaction"
    )
    
    # Saraf information
    saraf_account = models.ForeignKey(
        'saraf_account.SarafAccount',
        on_delete=models.CASCADE,
        related_name='exchange_transactions',
        help_text="Saraf account performing the exchange"
    )
    
    # Customer account information (optional)
    customer_account = models.ForeignKey(
        'saraf_create_accounts.SarafCustomerAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exchange_transactions',
        help_text="Customer account if transaction is with a registered customer"
    )
    
    # User information (who performed the transaction)
    performed_by_saraf = models.ForeignKey(
        'saraf_account.SarafAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_exchanges',
        help_text="Saraf who performed the transaction"
    )
    performed_by_employee = models.ForeignKey(
        'saraf_account.SarafEmployee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_exchanges',
        help_text="Employee who performed the transaction"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Exchange Transaction'
        verbose_name_plural = 'Exchange Transactions'
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['saraf_account', 'transaction_date']),
            models.Index(fields=['sell_currency', 'buy_currency']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['transaction_date']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.sell_amount} {self.sell_currency} → {self.buy_amount} {self.buy_currency}"
    
    def clean(self):
        """Model validation"""
        # Validate currency codes
        if self.sell_currency:
            self.sell_currency = self.sell_currency.upper()
        if self.buy_currency:
            self.buy_currency = self.buy_currency.upper()
        
        # Check currency code length
        if len(self.sell_currency) != 3:
            raise ValidationError("Sell currency code must be exactly 3 characters")
        if len(self.buy_currency) != 3:
            raise ValidationError("Buy currency code must be exactly 3 characters")
        
        # Check if currencies are different
        if self.sell_currency == self.buy_currency:
            raise ValidationError("Sell and buy currencies must be different")
        
        # Validate amounts
        if self.sell_amount <= 0:
            raise ValidationError("Sell amount must be greater than 0")
        if self.buy_amount <= 0:
            raise ValidationError("Buy amount must be greater than 0")
        
        # Validate rate
        if self.rate <= 0:
            raise ValidationError("Exchange rate must be greater than 0")
        
        # Validate transaction type
        if self.transaction_type not in [choice[0] for choice in self.TRANSACTION_TYPE_CHOICES]:
            raise ValidationError("Invalid transaction type")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_performed_by_info(self):
        """Get information about who performed the transaction"""
        if self.performed_by_employee:
            return {
                'type': 'employee',
                'id': self.performed_by_employee.employee_id,
                'name': self.performed_by_employee.full_name
            }
        elif self.performed_by_saraf:
            return {
                'type': 'saraf',
                'id': self.performed_by_saraf.saraf_id,
                'name': self.performed_by_saraf.full_name
            }
        return None
    
    def calculate_rate(self):
        """Calculate exchange rate from amounts"""
        if self.sell_amount and self.buy_amount:
            return self.buy_amount / self.sell_amount
        return None
