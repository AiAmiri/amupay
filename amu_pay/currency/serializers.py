from rest_framework import serializers
from .models import Currency, SarafSupportedCurrency


class CurrencySerializer(serializers.ModelSerializer):
    """
    Serializer for Currency model
    """
    class Meta:
        model = Currency
        fields = [
            'currency_code',
            'currency_name', 
            'currency_name_local',
            'symbol',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['created_at']


class SarafSupportedCurrencySerializer(serializers.ModelSerializer):
    """
    Serializer for Saraf supported currencies
    """
    currency_details = CurrencySerializer(source='currency', read_only=True)
    currency_code = serializers.CharField(write_only=True)
    
    class Meta:
        model = SarafSupportedCurrency
        fields = [
            'currency_code',
            'currency_details',
            'is_active',
            'added_at'
        ]
        read_only_fields = ['added_at']

    def validate_currency_code(self, value):
        """Currency code validation"""
        try:
            currency = Currency.objects.get(currency_code=value.upper(), is_active=True)
            return currency
        except Currency.DoesNotExist:
            raise serializers.ValidationError(f"Currency with code {value} not found or inactive")

    def create(self, validated_data):
        """Create new supported currency"""
        currency = validated_data.pop('currency_code')
        validated_data['currency'] = currency
        return super().create(validated_data)


class SarafSupportedCurrencyListSerializer(serializers.ModelSerializer):
    """
    Simple serializer for supported currencies list
    """
    currency_code = serializers.CharField(source='currency.currency_code')
    currency_name = serializers.CharField(source='currency.currency_name_local')
    currency_symbol = serializers.CharField(source='currency.symbol')
    
    class Meta:
        model = SarafSupportedCurrency
        fields = [
            'currency_code',
            'currency_name',
            'currency_symbol',
            'is_active',
            'added_at'
        ]
