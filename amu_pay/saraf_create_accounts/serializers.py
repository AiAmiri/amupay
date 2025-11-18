from rest_framework import serializers
from .models import SarafCustomerAccount, CustomerTransaction, CustomerBalance


class SarafCustomerAccountSerializer(serializers.ModelSerializer):
    """Serializer for Saraf Customer Account"""
    photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SarafCustomerAccount
        fields = [
            'account_id', 'account_number', 'full_name', 'account_type',
            'phone', 'address', 'job', 'photo', 'photo_url',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['account_id', 'account_number', 'created_at', 'updated_at']
    
    def get_photo_url(self, obj):
        """Return full URL for photo if it exists"""
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None
    
    def validate_phone(self, value):
        """Validate phone number format"""
        import re
        if not re.match(r'^0\d{9}$', value):
            raise serializers.ValidationError('Phone must be 10 digits and start with 0')
        return value
    
    def validate_account_type(self, value):
        """Validate account type"""
        if value not in ['exchanger', 'customer']:
            raise serializers.ValidationError('Account type must be either "exchanger" or "customer"')
        return value


class CustomerTransactionSerializer(serializers.ModelSerializer):
    """Serializer for Customer Transactions"""
    currency_code = serializers.CharField(source='currency.currency_code', read_only=True)
    currency_name = serializers.CharField(source='currency.currency_name', read_only=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True)
    customer_name = serializers.CharField(source='customer_account.full_name', read_only=True)
    account_number = serializers.CharField(source='customer_account.account_number', read_only=True)
    account_type = serializers.CharField(source='customer_account.account_type', read_only=True)
    
    class Meta:
        model = CustomerTransaction
        fields = [
            'transaction_id', 'customer_account', 'account_number', 'customer_name', 'account_type',
            'currency', 'currency_code', 'currency_name', 'currency_symbol', 'transaction_type',
            'amount', 'description', 'performer_user_id', 'performer_user_type',
            'performer_full_name', 'performer_employee_id', 'performer_employee_name',
            'balance_before', 'balance_after', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'transaction_id', 'performer_user_id', 'performer_user_type',
            'performer_full_name', 'performer_employee_id', 'performer_employee_name',
            'balance_before', 'balance_after', 'created_at', 'updated_at'
        ]


class CustomerBalanceSerializer(serializers.ModelSerializer):
    """Serializer for Customer Balances"""
    currency_code = serializers.CharField(source='currency.currency_code', read_only=True)
    currency_name = serializers.CharField(source='currency.currency_name', read_only=True)
    currency_symbol = serializers.CharField(source='currency.symbol', read_only=True)
    customer_name = serializers.CharField(source='customer_account.full_name', read_only=True)
    account_number = serializers.CharField(source='customer_account.account_number', read_only=True)
    account_type = serializers.CharField(source='customer_account.account_type', read_only=True)
    
    class Meta:
        model = CustomerBalance
        fields = [
            'balance_id', 'customer_account', 'account_number', 'customer_name', 'account_type',
            'currency', 'currency_code', 'currency_name', 'currency_symbol', 'balance',
            'total_deposits', 'total_withdrawals', 'transaction_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['balance_id', 'created_at', 'updated_at']


class CreateCustomerAccountSerializer(serializers.ModelSerializer):
    """Serializer for creating customer accounts"""
    
    class Meta:
        model = SarafCustomerAccount
        fields = [
            'full_name', 'account_type', 'phone', 'address', 'job', 'photo'
        ]
    
    def validate_phone(self, value):
        """Validate phone number format"""
        import re
        if not re.match(r'^0\d{9}$', value):
            raise serializers.ValidationError('Phone must be 10 digits and start with 0')
        return value
    
    def validate_account_type(self, value):
        """Validate account type"""
        if value not in ['exchanger', 'customer']:
            raise serializers.ValidationError('Account type must be either "exchanger" or "customer"')
        return value


class CustomerTransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating customer transactions"""
    
    class Meta:
        model = CustomerTransaction
        fields = ['currency', 'transaction_type', 'amount', 'description']
    
    def validate_amount(self, value):
        """Validate amount is positive"""
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than 0')
        return value
    
    def validate_transaction_type(self, value):
        """Validate transaction type"""
        valid_types = ['deposit', 'withdrawal', 'take_money', 'give_money']
        if value not in valid_types:
            raise serializers.ValidationError(f'Transaction type must be one of: {", ".join(valid_types)}')
        return value
