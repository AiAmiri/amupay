from rest_framework import serializers
from .models import SarafBalance


class SarafBalanceSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying Saraf balance
    """
    currency_code = serializers.CharField(source='currency.currency_code', read_only=True)
    currency_name = serializers.CharField(source='currency.currency_name_local', read_only=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True)
    saraf_name = serializers.CharField(source='saraf_account.full_name', read_only=True)
    
    class Meta:
        model = SarafBalance
        fields = [
            'balance_id',
            'saraf_name',
            'currency_code',
            'currency_name',
            'currency_symbol',
            'balance',
            'total_deposits',
            'total_withdrawals',
            'transaction_count',
            'last_updated',
            'created_at'
        ]
        read_only_fields = [
            'balance_id',
            'saraf_name',
            'currency_code',
            'currency_name',
            'currency_symbol',
            'balance',
            'total_deposits',
            'total_withdrawals',
            'transaction_count',
            'last_updated',
            'created_at'
        ]


class SarafBalanceSummarySerializer(serializers.ModelSerializer):
    """
    Summary serializer for balance display
    """
    currency_code = serializers.CharField(source='currency.currency_code', read_only=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True)
    
    class Meta:
        model = SarafBalance
        fields = [
            'currency_code',
            'currency_symbol',
            'balance',
            'last_updated'
        ]
