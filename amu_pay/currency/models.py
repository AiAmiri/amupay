from django.db import models
from django.core.exceptions import ValidationError


class Currency(models.Model):
    """
    Model for currencies supported in the system
    """
    currency_code = models.CharField(
        max_length=3, 
        primary_key=True,
        help_text="Currency code (e.g. USD, AFN, EUR)"
    )
    currency_name = models.CharField(
        max_length=50,
        help_text="Currency name (e.g. US Dollar, Afghan Afghani)"
    )
    currency_name_local = models.CharField(
        max_length=50,
        help_text="Local currency name (e.g. Dollar, Afghani)"
    )
    symbol = models.CharField(
        max_length=5,
        help_text="Currency symbol (e.g. $, ؋, €)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this currency active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'
        ordering = ['currency_code']

    def __str__(self):
        return f"{self.currency_code} - {self.currency_name_local}"

    def clean(self):
        """Model validation"""
        if self.currency_code:
            self.currency_code = self.currency_code.upper()
        
        if len(self.currency_code) != 3:
            raise ValidationError("Currency code must be exactly 3 characters")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class SarafSupportedCurrency(models.Model):
    """
    Currencies supported by each exchange
    """
    saraf_account = models.ForeignKey(
        'saraf_account.SarafAccount',
        on_delete=models.CASCADE,
        related_name='supported_currencies'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='supporting_sarafs'
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this currency active for this exchange?"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    added_by_saraf = models.ForeignKey(
        'saraf_account.SarafAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_currencies'
    )
    added_by_employee = models.ForeignKey(
        'saraf_account.SarafEmployee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_currencies'
    )

    class Meta:
        verbose_name = 'Exchange Supported Currency'
        verbose_name_plural = 'Exchange Supported Currencies'
        unique_together = [('saraf_account', 'currency')]
        indexes = [
            models.Index(fields=['saraf_account', 'is_active']),
            models.Index(fields=['currency', 'is_active']),
        ]

    def __str__(self):
        return f"{self.saraf_account.full_name} - {self.currency.currency_code}"