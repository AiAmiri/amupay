from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import re


class SarafCustomerAccount(models.Model):
    """Model for customer accounts created by Saraf"""
    
    ACCOUNT_TYPE_CHOICES = [
        ('exchanger', 'Exchanger'),
        ('customer', 'Customer'),
    ]
    
    account_id = models.BigAutoField(primary_key=True)
    saraf_account = models.ForeignKey(
        'saraf_account.SarafAccount',
        on_delete=models.CASCADE,
        related_name='created_customer_accounts'
    )
    account_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique account number for this saraf"
    )
    full_name = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Customer's full name"
    )
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        help_text="Type of account (exchanger or customer)"
    )
    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(
            regex=r'^0\d{9}$',
            message='Phone must be 10 digits and start with 0'
        )],
        help_text="10-digit phone number starting with 0"
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Customer's address"
    )
    job = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Customer's job/profession"
    )
    photo = models.ImageField(
        upload_to='customer_photos/',
        blank=True,
        null=True,
        help_text="Customer's photo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Customer Account'
        verbose_name_plural = 'Customer Accounts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['saraf_account', 'account_type']),
            models.Index(fields=['saraf_account', 'phone']),
            models.Index(fields=['account_number']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['saraf_account', 'phone'],
                name='unique_phone_per_saraf'
            )
        ]
    
    def __str__(self):
        return f"{self.account_number} - {self.full_name or 'No Name'} ({self.get_account_type_display()})"
    
    def clean(self):
        """Validate phone number format"""
        super().clean()
        if self.phone:
            if not re.match(r'^0\d{9}$', self.phone):
                raise ValidationError({
                    'phone': 'Phone must be 10 digits and start with 0'
                })
    
    def save(self, *args, **kwargs):
        """Generate account number if not provided"""
        if not self.account_number:
            self.account_number = self.generate_account_number()
        self.full_clean()
        super().save(*args, **kwargs)
    
    def generate_account_number(self):
        """Generate unique account number for this saraf"""
        import random
        import string
        
        # Get the saraf's ID for prefix
        saraf_prefix = str(self.saraf_account.saraf_id).zfill(3)
        
        # Generate random suffix
        while True:
            suffix = ''.join(random.choices(string.digits, k=7))
            account_number = f"{saraf_prefix}{suffix}"
            
            # Check if this account number already exists
            if not SarafCustomerAccount.objects.filter(account_number=account_number).exists():
                return account_number


class CustomerTransaction(models.Model):
    """Model for customer account transactions"""
    
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('take_money', 'Take Money'),  # For exchangers
        ('give_money', 'Give Money'),  # For exchangers
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('exchange', 'Exchange'),
    ]
    
    transaction_id = models.BigAutoField(primary_key=True)
    customer_account = models.ForeignKey(
        SarafCustomerAccount,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    currency = models.ForeignKey(
        'currency.Currency',
        on_delete=models.CASCADE,
        related_name='customer_transactions'
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
        verbose_name = 'Customer Transaction'
        verbose_name_plural = 'Customer Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_account', 'currency']),
            models.Index(fields=['customer_account', 'transaction_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['performer_user_id']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.amount} {self.currency.currency_code} - {self.customer_account.account_number}"
    
    def save(self, *args, **kwargs):
        """Save transaction and update both customer balance and saraf balance"""
        # Get or create customer balance
        customer_balance, created = CustomerBalance.get_or_create_balance(
            self.customer_account, 
            self.currency
        )
        
        # Record customer balance before transaction
        self.balance_before = customer_balance.balance
        
        # Update customer balance based on transaction type
        if self.transaction_type in ['deposit', 'give_money']:
            customer_balance.balance += self.amount
            customer_balance.total_deposits += self.amount
        elif self.transaction_type in ['withdrawal', 'take_money']:
            # Removed the negative balance check as per user request
            customer_balance.balance -= self.amount
            customer_balance.total_withdrawals += self.amount
        
        customer_balance.transaction_count += 1
        customer_balance.save()
        
        # Record customer balance after transaction
        self.balance_after = customer_balance.balance
        
        # Update saraf balance based on transaction type
        # Deposit and Take Money increase saraf balance
        # Withdraw and Give Money decrease saraf balance
        from saraf_balance.models import SarafBalance
        
        saraf_balance, created = SarafBalance.get_or_create_balance(
            self.customer_account.saraf_account,
            self.currency
        )
        
        if self.transaction_type in ['deposit', 'take_money']:
            # These operations increase saraf balance
            saraf_balance.balance += self.amount
            saraf_balance.total_deposits += self.amount
        elif self.transaction_type in ['withdrawal', 'give_money']:
            # These operations decrease saraf balance
            saraf_balance.balance -= self.amount
            saraf_balance.total_withdrawals += self.amount
        
        saraf_balance.transaction_count += 1
        saraf_balance.save()
        
        super().save(*args, **kwargs)
    
    @classmethod
    def create_transaction(cls, customer_account, currency, transaction_type, amount, description, user_info):
        """Create new customer transaction with user information"""
        # Get performer full name from saraf account or employee
        performer_full_name = user_info.get('full_name')
        performer_employee_name = user_info.get('employee_name')
        
        # If full_name is not provided, get it from the database
        if not performer_full_name:
            if user_info.get('user_type') == 'employee':
                # Get employee name from database
                from saraf_account.models import SarafEmployee
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info.get('employee_id'))
                    performer_full_name = employee.full_name
                    performer_employee_name = employee.full_name
                except SarafEmployee.DoesNotExist:
                    performer_full_name = "Unknown Employee"
            else:
                # Get saraf name from database
                from saraf_account.models import SarafAccount
                try:
                    saraf = SarafAccount.objects.get(saraf_id=user_info.get('saraf_id'))
                    performer_full_name = saraf.full_name
                except SarafAccount.DoesNotExist:
                    performer_full_name = "Unknown Saraf"
        
        transaction = cls(
            customer_account=customer_account,
            currency=currency,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            performer_user_id=user_info.get('user_id'),
            performer_user_type=user_info.get('user_type'),
            performer_full_name=performer_full_name,
            performer_employee_id=user_info.get('employee_id'),
            performer_employee_name=performer_employee_name
        )
        transaction.save()
        return transaction


class CustomerBalance(models.Model):
    """Model for customer account balances"""
    
    balance_id = models.BigAutoField(primary_key=True)
    customer_account = models.ForeignKey(
        SarafCustomerAccount,
        on_delete=models.CASCADE,
        related_name='balances'
    )
    currency = models.ForeignKey(
        'currency.Currency',
        on_delete=models.CASCADE,
        related_name='customer_balances'
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Current balance"
    )
    total_deposits = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total deposits (deposit + give_money)"
    )
    total_withdrawals = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total withdrawals (withdrawal + take_money)"
    )
    transaction_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Customer Balance'
        verbose_name_plural = 'Customer Balances'
        unique_together = [('customer_account', 'currency')]
        indexes = [
            models.Index(fields=['customer_account', 'currency']),
        ]
    
    def __str__(self):
        return f"{self.customer_account.account_number} - {self.balance} {self.currency.currency_code}"
    
    @classmethod
    def get_or_create_balance(cls, customer_account, currency):
        """Get or create balance for customer account and currency"""
        balance, created = cls.objects.get_or_create(
            customer_account=customer_account,
            currency=currency,
            defaults={
                'balance': Decimal('0.00'),
                'total_deposits': Decimal('0.00'),
                'total_withdrawals': Decimal('0.00'),
                'transaction_count': 0
            }
        )
        return balance, created
    
    def update_balance(self, amount, transaction_type):
        """Update balance based on transaction type and also update saraf balance"""
        if transaction_type in ['deposit', 'give_money']:
            self.balance += amount
            self.total_deposits += amount
        elif transaction_type in ['withdrawal', 'take_money']:
            # Removed the negative balance check as per user request
            self.balance -= amount
            self.total_withdrawals += amount
        
        self.transaction_count += 1
        self.save(update_fields=['balance', 'total_deposits', 'total_withdrawals', 'transaction_count', 'updated_at'])
        
        # Also update saraf balance
        from saraf_balance.models import SarafBalance
        
        saraf_balance, created = SarafBalance.get_or_create_balance(
            self.customer_account.saraf_account,
            self.currency
        )
        
        if transaction_type in ['deposit', 'take_money']:
            # These operations increase saraf balance
            saraf_balance.balance += amount
            saraf_balance.total_deposits += amount
        elif transaction_type in ['withdrawal', 'give_money']:
            # These operations decrease saraf balance
            saraf_balance.balance -= amount
            saraf_balance.total_withdrawals += amount
        
        saraf_balance.transaction_count += 1
        saraf_balance.save()