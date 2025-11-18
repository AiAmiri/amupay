from django.db import models
from decimal import Decimal


class SarafBalance(models.Model):
    """Balance for each exchange for each currency"""
    
    balance_id = models.BigAutoField(primary_key=True)
    saraf_account = models.ForeignKey(
        'saraf_account.SarafAccount',
        on_delete=models.CASCADE,
        related_name='balances'
    )
    currency = models.ForeignKey(
        'currency.Currency',
        on_delete=models.CASCADE,
        related_name='saraf_balances'
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_deposits = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_withdrawals = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    transaction_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Exchange Balance'
        verbose_name_plural = 'Exchange Balances'
        unique_together = [('saraf_account', 'currency')]

    def __str__(self):
        return f"{self.saraf_account.full_name} - {self.currency.currency_code}: {self.balance}"

    def update_balance(self, amount, transaction_type):
        """Update balance with validation to prevent negative balances"""
        if transaction_type == 'deposit':
            self.balance += amount
            self.total_deposits += amount
        elif transaction_type == 'withdrawal':
            # Check if withdrawal would result in negative balance
            if self.balance < amount:
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    f"Insufficient balance. Current balance: {self.balance} {self.currency.currency_code}, "
                    f"Requested withdrawal: {amount} {self.currency.currency_code}"
                )
            self.balance -= amount
            self.total_withdrawals += amount
        
        self.transaction_count += 1
        self.save()

    @classmethod
    def get_or_create_balance(cls, saraf_account, currency):
        """Get or create balance"""
        balance, created = cls.objects.get_or_create(
            saraf_account=saraf_account,
            currency=currency,
            defaults={
                'balance': Decimal('0.00'),
                'total_deposits': Decimal('0.00'),
                'total_withdrawals': Decimal('0.00'),
                'transaction_count': 0
            }
        )
        return balance, created
