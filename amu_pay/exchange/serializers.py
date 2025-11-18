from rest_framework import serializers
from .models import ExchangeTransaction


class ExchangeTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for ExchangeTransaction model
    """
    performed_by_info = serializers.SerializerMethodField()
    customer_account_info = serializers.SerializerMethodField()
    
    # Make amount fields optional with default values
    sell_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        default=0,
        help_text="Amount of currency being sold (default: 0)"
    )
    buy_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        default=0,
        help_text="Amount of currency being bought (default: 0)"
    )
    
    class Meta:
        model = ExchangeTransaction
        fields = [
            'id',
            'name',
            'transaction_type',
            'sell_currency',
            'sell_amount',
            'buy_currency',
            'buy_amount',
            'rate',
            'notes',
            'transaction_date',
            'saraf_account',
            'customer_account',
            'customer_account_info',
            'performed_by_info',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'performed_by_info', 'customer_account_info']
    
    def get_performed_by_info(self, obj):
        """Get information about who performed the transaction"""
        return obj.get_performed_by_info()
    
    def get_customer_account_info(self, obj):
        """Get information about the customer account if linked"""
        if obj.customer_account:
            return {
                'account_id': obj.customer_account.account_id,
                'account_number': obj.customer_account.account_number,
                'full_name': obj.customer_account.full_name,
                'account_type': obj.customer_account.account_type,
                'phone': obj.customer_account.phone
            }
        return None
    
    def validate_sell_currency(self, value):
        """Validate sell currency code"""
        if value:
            value = value.upper()
            if len(value) != 3:
                raise serializers.ValidationError("Currency code must be exactly 3 characters")
        return value
    
    def validate_buy_currency(self, value):
        """Validate buy currency code"""
        if value:
            value = value.upper()
            if len(value) != 3:
                raise serializers.ValidationError("Currency code must be exactly 3 characters")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        sell_currency = data.get('sell_currency', '').upper()
        buy_currency = data.get('buy_currency', '').upper()
        
        # Check if currencies are different
        if sell_currency == buy_currency:
            raise serializers.ValidationError("Sell and buy currencies must be different")
        
        # Validate amounts
        sell_amount = data.get('sell_amount')
        buy_amount = data.get('buy_amount')
        
        if sell_amount and sell_amount <= 0:
            raise serializers.ValidationError("Sell amount must be greater than 0")
        if buy_amount and buy_amount <= 0:
            raise serializers.ValidationError("Buy amount must be greater than 0")
        
        # Validate rate
        rate = data.get('rate')
        if rate and rate <= 0:
            raise serializers.ValidationError("Exchange rate must be greater than 0")
        
        return data


class ExchangeTransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating ExchangeTransaction
    """
    # Explicitly define amount fields as required
    sell_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=True,
        help_text="Amount of currency being sold"
    )
    buy_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=True,
        help_text="Amount of currency being bought"
    )
    
    # Customer account field (optional)
    customer_account_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID of customer account if transaction is with a registered customer"
    )
    
    class Meta:
        model = ExchangeTransaction
        fields = [
            'name',
            'transaction_type',
            'sell_currency',
            'sell_amount',
            'buy_currency',
            'buy_amount',
            'rate',
            'notes',
            'customer_account_id'
        ]
        read_only_fields = ['transaction_date']
    
    def validate_sell_currency(self, value):
        """Validate sell currency code"""
        if value:
            value = value.upper()
            if len(value) != 3:
                raise serializers.ValidationError("Currency code must be exactly 3 characters")
        return value
    
    def validate_buy_currency(self, value):
        """Validate buy currency code"""
        if value:
            value = value.upper()
            if len(value) != 3:
                raise serializers.ValidationError("Currency code must be exactly 3 characters")
        return value
    
    def validate_sell_amount(self, value):
        """Validate sell amount"""
        if value is None:
            raise serializers.ValidationError("Sell amount is required")
        if value <= 0:
            raise serializers.ValidationError("Sell amount must be greater than 0")
        return value
    
    def validate_buy_amount(self, value):
        """Validate buy amount"""
        if value is None:
            raise serializers.ValidationError("Buy amount is required")
        if value <= 0:
            raise serializers.ValidationError("Buy amount must be greater than 0")
        return value
    
    def validate_customer_account_id(self, value):
        """Validate customer account ID"""
        if value is not None:
            from saraf_create_accounts.models import SarafCustomerAccount
            try:
                customer_account = SarafCustomerAccount.objects.get(account_id=value)
                # Verify the customer account belongs to the same saraf
                # This will be checked in the view where we have access to saraf_account
                return value
            except SarafCustomerAccount.DoesNotExist:
                raise serializers.ValidationError("Customer account not found")
        return value
    
    def validate(self, data):
        """Cross-field validation including transaction type requirements"""
        sell_currency = data.get('sell_currency', '').upper()
        buy_currency = data.get('buy_currency', '').upper()
        transaction_type = data.get('transaction_type')
        customer_account_id = data.get('customer_account_id')
        
        # Check if currencies are different
        if sell_currency == buy_currency:
            raise serializers.ValidationError("Sell and buy currencies must be different")
        
        # Validate amounts are provided and positive
        sell_amount = data.get('sell_amount')
        buy_amount = data.get('buy_amount')
        
        if sell_amount is None:
            raise serializers.ValidationError("Sell amount is required")
        if buy_amount is None:
            raise serializers.ValidationError("Buy amount is required")
        
        if sell_amount <= 0:
            raise serializers.ValidationError("Sell amount must be greater than 0")
        if buy_amount <= 0:
            raise serializers.ValidationError("Buy amount must be greater than 0")
        
        # Validate transaction type requirements
        if transaction_type in ['customer', 'exchanger'] and not customer_account_id:
            raise serializers.ValidationError(f"Customer account ID is required for {transaction_type} transactions")
        
        if transaction_type == 'person' and customer_account_id:
            raise serializers.ValidationError("Customer account ID should not be provided for person transactions")
        
        # Validate rate
        rate = data.get('rate')
        if rate and rate <= 0:
            raise serializers.ValidationError("Exchange rate must be greater than 0")
        
        return data
    
    def create(self, validated_data):
        """Override create to automatically set transaction_date and handle customer account based on transaction type"""
        from django.utils import timezone
        from saraf_create_accounts.models import SarafCustomerAccount
        
        # Extract customer_account_id and remove it from validated_data
        customer_account_id = validated_data.pop('customer_account_id', None)
        transaction_type = validated_data.get('transaction_type')
        
        # Set transaction_date
        validated_data['transaction_date'] = timezone.now()
        
        # Handle customer account based on transaction type
        customer_account = None
        if transaction_type in ['customer', 'exchanger'] and customer_account_id:
            try:
                customer_account = SarafCustomerAccount.objects.get(account_id=customer_account_id)
                validated_data['customer_account'] = customer_account
            except SarafCustomerAccount.DoesNotExist:
                pass  # Will be handled by validation
        
        return super().create(validated_data)


class ExchangeTransactionListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing ExchangeTransactions
    """
    performed_by_name = serializers.SerializerMethodField()
    saraf_name = serializers.CharField(source='saraf_account.full_name', read_only=True)
    
    class Meta:
        model = ExchangeTransaction
        fields = [
            'id',
            'name',
            'transaction_type',
            'sell_currency',
            'sell_amount',
            'buy_currency',
            'buy_amount',
            'rate',
            'transaction_date',
            'saraf_name',
            'performed_by_name',
            'created_at'
        ]
    
    def get_performed_by_name(self, obj):
        """Get name of who performed the transaction"""
        performed_by_info = obj.get_performed_by_info()
        if performed_by_info:
            return performed_by_info['name']
        return None


class ExchangeTransactionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating ExchangeTransaction
    """
    class Meta:
        model = ExchangeTransaction
        fields = [
            'name',
            'transaction_type',
            'sell_currency',
            'sell_amount',
            'buy_currency',
            'buy_amount',
            'rate',
            'notes',
            'transaction_date'
        ]
    
    def validate_sell_currency(self, value):
        """Validate sell currency code"""
        if value:
            value = value.upper()
            if len(value) != 3:
                raise serializers.ValidationError("Currency code must be exactly 3 characters")
        return value
    
    def validate_buy_currency(self, value):
        """Validate buy currency code"""
        if value:
            value = value.upper()
            if len(value) != 3:
                raise serializers.ValidationError("Currency code must be exactly 3 characters")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        sell_currency = data.get('sell_currency', '').upper()
        buy_currency = data.get('buy_currency', '').upper()
        
        # Check if currencies are different
        if sell_currency == buy_currency:
            raise serializers.ValidationError("Sell and buy currencies must be different")
        
        # Validate amounts
        sell_amount = data.get('sell_amount')
        buy_amount = data.get('buy_amount')
        
        if sell_amount and sell_amount <= 0:
            raise serializers.ValidationError("Sell amount must be greater than 0")
        if buy_amount and buy_amount <= 0:
            raise serializers.ValidationError("Buy amount must be greater than 0")
        
        # Validate rate
        rate = data.get('rate')
        if rate and rate <= 0:
            raise serializers.ValidationError("Exchange rate must be greater than 0")
        
        return data
