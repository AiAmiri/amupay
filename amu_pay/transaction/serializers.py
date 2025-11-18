from rest_framework import serializers
from .models import Transaction
from currency.serializers import CurrencySerializer
from decimal import Decimal


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for displaying transactions"""
    
    currency = CurrencySerializer(read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'transaction_id',
            'transaction_type',
            'transaction_type_display',
            'amount',
            'description',
            'currency',
            'performer_full_name',
            'performer_employee_name',
            'balance_before',
            'balance_after',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'transaction_id',
            'balance_before',
            'balance_after',
            'created_at',
            'updated_at'
        ]


class CreateTransactionSerializer(serializers.Serializer):
    """Serializer for creating new transactions"""
    
    currency_code = serializers.CharField(max_length=3)
    transaction_type = serializers.ChoiceField(choices=Transaction.TRANSACTION_TYPES)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'))
    description = serializers.CharField(required=False, allow_blank=True)
    
    def validate_amount(self, value):
        """Amount validation"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value
    
    def validate_currency_code(self, value):
        """Currency code validation"""
        from currency.models import Currency
        try:
            currency = Currency.objects.get(currency_code=value, is_active=True)
            return value
        except Currency.DoesNotExist:
            raise serializers.ValidationError("Selected currency is not valid")


class TransactionListSerializer(serializers.ModelSerializer):
    """Simple serializer for transaction list"""
    
    currency_code = serializers.CharField(source='currency.currency_code', read_only=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'transaction_id',
            'transaction_type',
            'transaction_type_display',
            'amount',
            'currency_code',
            'currency_symbol',
            'description',
            'performer_full_name',
            'balance_after',
            'created_at'
        ]
