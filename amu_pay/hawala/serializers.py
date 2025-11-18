from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import HawalaTransaction, HawalaReceipt
from saraf_account.models import SarafAccount, SarafEmployee
from currency.models import Currency, SarafSupportedCurrency


class HawalaTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for HawalaTransaction model
    Used for creating and updating hawala transactions
    """
    
    # Read-only fields
    hawala_number = serializers.CharField(required=True, help_text="Hawala number manually entered by saraf (primary key)")
    created_at = serializers.DateTimeField(read_only=True)
    sent_at = serializers.DateTimeField(read_only=True)
    received_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    # Foreign key fields with validation
    currency_code = serializers.CharField(write_only=True, help_text="Currency code (e.g., USD, AFN)")
    sender_exchange_id = serializers.IntegerField(
        required=False, 
        write_only=True, 
        help_text="Sender exchange ID (auto-set from authenticated user)"
    )
    destination_exchange_id = serializers.IntegerField(
        required=False, 
        allow_null=True, 
        write_only=True,
        help_text="Destination exchange ID (if using app)"
    )
    
    # Fields that are auto-set by the serializer
    sender_exchange = serializers.PrimaryKeyRelatedField(
        queryset=SarafAccount.objects.all(),
        required=False,
        write_only=True,
        help_text="Sender exchange (auto-set from authenticated user)"
    )
    sender_exchange_name = serializers.CharField(
        required=False,
        write_only=True,
        help_text="Sender exchange name (auto-set from authenticated user)"
    )
    mode = serializers.ChoiceField(
        choices=[
            ('internal', 'Internal (Both sarafs use app)'),
            ('external_sender', 'External (Only sender uses app)'),
            ('external_receiver', 'External (Only receiver uses app)'),
        ],
        required=False,
        write_only=True,
        help_text="Transaction mode (auto-determined)"
    )
    
    # Computed fields
    total_amount = serializers.SerializerMethodField()
    currency_display = serializers.SerializerMethodField()
    sender_exchange_display = serializers.SerializerMethodField()
    destination_exchange_display = serializers.SerializerMethodField()
    supported_currencies = serializers.SerializerMethodField()
    
    class Meta:
        model = HawalaTransaction
        fields = [
            'hawala_number', 'sender_name', 'sender_phone',
            'receiver_name', 'receiver_phone', 'receiver_photo', 'amount',
            'currency', 'currency_code', 'transfer_fee', 'total_amount',
            'sender_exchange', 'sender_exchange_id', 'sender_exchange_name',
            'sender_exchange_display', 'destination_exchange_id',
            'destination_exchange_name', 'destination_exchange_address',
            'destination_exchange_display', 'status', 'mode',
            'destination_saraf_uses_app', 'notes', 'created_at', 'sent_at',
            'received_at', 'completed_at', 'updated_at', 'currency_display',
            'supported_currencies'
        ]
        read_only_fields = [
            'currency', 'sender_exchange', 'sender_exchange_name', 'mode',
            'created_at', 'sent_at', 'received_at', 'completed_at', 'updated_at'
        ]

    def get_total_amount(self, obj):
        """Get total amount including transfer fee"""
        return obj.get_total_amount()

    def get_currency_display(self, obj):
        """Get currency display information"""
        if obj.currency:
            return {
                'code': obj.currency.currency_code,
                'name': obj.currency.currency_name,
                'name_local': obj.currency.currency_name_local,
                'symbol': obj.currency.symbol
            }
        return None

    def get_sender_exchange_display(self, obj):
        """Get sender exchange display information"""
        if obj.sender_exchange:
            return {
                'id': obj.sender_exchange.saraf_id,
                'name': obj.sender_exchange.exchange_name,
                'full_name': obj.sender_exchange.full_name,
                'amu_pay_code': obj.sender_exchange.amu_pay_code
            }
        return None

    def get_destination_exchange_display(self, obj):
        """Get destination exchange display information"""
        if obj.destination_exchange_id:
            try:
                destination_exchange = SarafAccount.objects.get(saraf_id=obj.destination_exchange_id)
                return {
                    'id': destination_exchange.saraf_id,
                    'name': destination_exchange.exchange_name,
                    'full_name': destination_exchange.full_name,
                    'amu_pay_code': destination_exchange.amu_pay_code
                }
            except SarafAccount.DoesNotExist:
                return None
        return None

    def get_supported_currencies(self, obj):
        """Get currencies supported by the saraf"""
        saraf_account = self.context.get('saraf_account')
        if saraf_account:
            supported_currencies = SarafSupportedCurrency.objects.filter(
                saraf_account=saraf_account,
                is_active=True
            ).select_related('currency')
            
            return [
                {
                    'code': sc.currency.currency_code,
                    'name': sc.currency.currency_name,
                    'name_local': sc.currency.currency_name_local,
                    'symbol': sc.currency.symbol
                }
                for sc in supported_currencies
            ]
        return []

    def validate_currency_code(self, value):
        """Validate currency code - must be supported by the saraf"""
        try:
            currency = Currency.objects.get(currency_code=value.upper(), is_active=True)
            
            # Get saraf account from context
            saraf_account = self.context.get('saraf_account')
            if saraf_account:
                # Check if saraf supports this currency
                if not SarafSupportedCurrency.objects.filter(
                    saraf_account=saraf_account,
                    currency=currency,
                    is_active=True
                ).exists():
                    raise serializers.ValidationError(
                        f"Currency '{value}' is not supported by your exchange. "
                        f"Please add this currency to your supported currencies first."
                    )
            
            return value.upper()
        except Currency.DoesNotExist:
            raise serializers.ValidationError(f"Currency '{value}' is not supported or inactive.")

    def validate_sender_exchange_id(self, value):
        """Validate sender exchange ID"""
        try:
            exchange = SarafAccount.objects.get(saraf_id=value, is_active=True)
            return value
        except SarafAccount.DoesNotExist:
            raise serializers.ValidationError(f"Sender exchange with ID '{value}' not found or inactive.")

    def validate_destination_exchange_id(self, value):
        """Validate destination exchange ID"""
        if value is not None:
            try:
                exchange = SarafAccount.objects.get(saraf_id=value, is_active=True)
                return value
            except SarafAccount.DoesNotExist:
                raise serializers.ValidationError(f"Destination exchange with ID '{value}' not found or inactive.")
        return value

    def validate_hawala_number(self, value):
        """Validate hawala number uniqueness"""
        if not value:
            raise serializers.ValidationError("Hawala number is required.")
        
        # Check if this is an update operation and hawala_number hasn't changed
        if self.instance and self.instance.hawala_number == value:
            return value
        
        # Check if hawala_number already exists
        if HawalaTransaction.objects.filter(hawala_number=value).exists():
            raise serializers.ValidationError("Hawala number already exists. Please use a different number.")
        
        return value

    def validate_amount(self, value):
        """Validate amount"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_transfer_fee(self, value):
        """Validate transfer fee"""
        if value < 0:
            raise serializers.ValidationError("Transfer fee cannot be negative.")
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        # Validate destination_saraf_uses_app and destination_exchange_id consistency
        destination_saraf_uses_app = attrs.get('destination_saraf_uses_app', True)
        destination_exchange_id = attrs.get('destination_exchange_id')
        
        if destination_saraf_uses_app and not destination_exchange_id:
            raise serializers.ValidationError(
                "Destination exchange ID is required when destination saraf uses the app."
            )
        
        if not destination_saraf_uses_app and destination_exchange_id:
            raise serializers.ValidationError(
                "Destination exchange ID should not be provided when destination saraf doesn't use the app."
            )
        
        # Set mode based on destination_saraf_uses_app
        if destination_saraf_uses_app:
            attrs['mode'] = 'internal'
        else:
            attrs['mode'] = 'external_sender'
        
        return attrs

    def create(self, validated_data):
        """Create hawala transaction"""
        # Extract foreign key data
        currency_code = validated_data.pop('currency_code')
        sender_exchange_id = validated_data.pop('sender_exchange_id', None)
        destination_exchange_id = validated_data.pop('destination_exchange_id', None)
        
        # Get foreign key objects
        currency = Currency.objects.get(currency_code=currency_code)
        
        # Handle sender exchange - either from sender_exchange_id or from context
        if sender_exchange_id:
            sender_exchange = SarafAccount.objects.get(saraf_id=sender_exchange_id)
        else:
            # Get from context (set by view)
            saraf_account = self.context.get('saraf_account')
            if not saraf_account:
                raise serializers.ValidationError("Sender exchange information is required")
            sender_exchange = saraf_account
        
        # Set foreign key fields
        validated_data['currency'] = currency
        validated_data['sender_exchange'] = sender_exchange
        validated_data['destination_exchange_id'] = destination_exchange_id
        
        # Set sender exchange name if not already set
        if 'sender_exchange_name' not in validated_data:
            validated_data['sender_exchange_name'] = sender_exchange.exchange_name or sender_exchange.full_name
        
        # Get employee from context if available
        employee = self.context.get('employee')
        if employee:
            validated_data['created_by_employee'] = employee
        
        # Determine mode if not provided
        if 'mode' not in validated_data:
            if destination_exchange_id and validated_data.get('destination_saraf_uses_app', True):
                validated_data['mode'] = 'internal'
            else:
                validated_data['mode'] = 'external_sender'
        
        return super().create(validated_data)


class HawalaReceiveSerializer(serializers.ModelSerializer):
    """
    Serializer for receiving hawala transactions
    Used when receiving saraf updates transaction with receiver details
    """
    
    receiver_phone = serializers.CharField(
        required=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')]
    )
    receiver_photo = serializers.ImageField(required=True)
    
    class Meta:
        model = HawalaTransaction
        fields = ['receiver_phone', 'receiver_photo', 'notes']
    
    def validate_receiver_phone(self, value):
        """Validate receiver phone number"""
        if not value:
            raise serializers.ValidationError("Receiver phone number is required.")
        return value
    
    def validate_receiver_photo(self, value):
        """Validate receiver photo"""
        if not value:
            raise serializers.ValidationError("Receiver photo is required.")
        return value


class HawalaExternalReceiveSerializer(serializers.ModelSerializer):
    """
    Serializer for external hawala transactions (Mode 2.2)
    Used when only receiving saraf uses the app
    """
    
    # Read-only fields
    hawala_number = serializers.CharField(required=True, help_text="Hawala number manually entered by saraf (primary key)")
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    # Foreign key fields
    currency_code = serializers.CharField(write_only=True)
    receiver_exchange_id = serializers.IntegerField(write_only=True)
    
    # Required fields for external receive
    receiver_phone = serializers.CharField(required=True)
    receiver_photo = serializers.ImageField(required=True)
    
    class Meta:
        model = HawalaTransaction
        fields = [
            'hawala_number', 'sender_name',
            'receiver_name', 'receiver_phone', 'receiver_photo', 'amount',
            'currency', 'currency_code', 'transfer_fee', 'sender_exchange',
            'sender_exchange_name', 'destination_exchange_name',
            'destination_exchange_address', 'receiver_exchange_id', 'status',
            'mode', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'hawala_number', 'currency', 'sender_exchange', 'sender_exchange_name',
            'status', 'mode', 'created_at', 'updated_at'
        ]
    
    def validate_currency_code(self, value):
        """Validate currency code - must be supported by the saraf"""
        try:
            currency = Currency.objects.get(currency_code=value.upper(), is_active=True)
            
            # Get saraf account from context
            saraf_account = self.context.get('saraf_account')
            if saraf_account:
                # Check if saraf supports this currency
                if not SarafSupportedCurrency.objects.filter(
                    saraf_account=saraf_account,
                    currency=currency,
                    is_active=True
                ).exists():
                    raise serializers.ValidationError(
                        f"Currency '{value}' is not supported by your exchange. "
                        f"Please add this currency to your supported currencies first."
                    )
            
            return value.upper()
        except Currency.DoesNotExist:
            raise serializers.ValidationError(f"Currency '{value}' is not supported or inactive.")
    
    def validate_receiver_exchange_id(self, value):
        """Validate receiver exchange ID"""
        try:
            exchange = SarafAccount.objects.get(saraf_id=value, is_active=True)
            return value
        except SarafAccount.DoesNotExist:
            raise serializers.ValidationError(f"Receiver exchange with ID '{value}' not found or inactive.")
    
    def validate_hawala_number(self, value):
        """Validate hawala number uniqueness"""
        if not value:
            raise serializers.ValidationError("Hawala number is required.")
        
        # Check if hawala number already exists
        if HawalaTransaction.objects.filter(hawala_number=value).exists():
            raise serializers.ValidationError("Hawala number already exists. Please use a different number.")
        
        return value
    
    def create(self, validated_data):
        """Create external hawala transaction"""
        # Extract foreign key data
        currency_code = validated_data.pop('currency_code')
        receiver_exchange_id = validated_data.pop('receiver_exchange_id')
        
        # Get foreign key objects
        currency = Currency.objects.get(currency_code=currency_code)
        receiver_exchange = SarafAccount.objects.get(saraf_id=receiver_exchange_id)
        
        # Set foreign key fields
        validated_data['currency'] = currency
        validated_data['sender_exchange'] = receiver_exchange  # In external mode, receiver exchange is the sender
        validated_data['mode'] = 'external_receiver'
        validated_data['status'] = 'received'
        validated_data['destination_saraf_uses_app'] = False
        
        # Set default values for excluded fields
        if 'sender_phone' not in validated_data:
            validated_data['sender_phone'] = '+0000000000'  # Default for external sender
        if 'notes' not in validated_data:
            validated_data['notes'] = ''  # Empty notes for external receive
        
        # Set exchange names
        validated_data['sender_exchange_name'] = receiver_exchange.exchange_name or receiver_exchange.full_name
        validated_data['destination_exchange_name'] = validated_data.get('destination_exchange_name', 'External Exchange')
        
        # Get employee from context if available
        employee = self.context.get('employee')
        if employee:
            validated_data['created_by_employee'] = employee
            validated_data['received_by_employee'] = employee
        
        return super().create(validated_data)


class HawalaListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing hawala transactions
    Provides summary information for transaction lists
    """
    
    currency_display = serializers.SerializerMethodField()
    sender_exchange_display = serializers.SerializerMethodField()
    destination_exchange_display = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    receiver_photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = HawalaTransaction
        fields = [
            'hawala_number', 'sender_name', 'receiver_name',
            'amount', 'transfer_fee', 'total_amount', 'currency_display',
            'sender_exchange_display', 'destination_exchange_display',
            'status', 'mode', 'created_at', 'sent_at', 'received_at',
            'completed_at', 'receiver_photo_url'
        ]
    
    def get_currency_display(self, obj):
        """Get currency display information"""
        if obj.currency:
            return {
                'code': obj.currency.currency_code,
                'symbol': obj.currency.symbol
            }
        return None
    
    def get_sender_exchange_display(self, obj):
        """Get sender exchange display information"""
        # For external receive hawalas, sender_exchange is actually the receiver
        # The actual sender is stored in destination_exchange_name
        if obj.mode == 'external_receiver':
            # For external receive, show the actual external sender from destination_exchange_name
            if obj.destination_exchange_name:
                return {
                    'id': None,  # External sender doesn't have an ID in the system
                    'name': obj.destination_exchange_name
                }
            return None
        
        # For normal hawalas, show sender_exchange
        if obj.sender_exchange:
            return {
                'id': obj.sender_exchange.saraf_id,
                'name': obj.sender_exchange.exchange_name
            }
        return None
    
    def get_destination_exchange_display(self, obj):
        """Get destination exchange display information"""
        # For external receive hawalas, destination is the current saraf (receiver)
        if obj.mode == 'external_receiver':
            # For external receive, destination is the receiver (stored in sender_exchange)
            if obj.sender_exchange:
                return {
                    'id': obj.sender_exchange.saraf_id,
                    'name': obj.sender_exchange.exchange_name
                }
            return None
        
        # For normal hawalas, show destination_exchange
        if obj.destination_exchange_id:
            try:
                destination_exchange = SarafAccount.objects.get(saraf_id=obj.destination_exchange_id)
                return {
                    'id': destination_exchange.saraf_id,
                    'name': destination_exchange.exchange_name
                }
            except SarafAccount.DoesNotExist:
                return None
        return None
    
    def get_total_amount(self, obj):
        """Get total amount including transfer fee"""
        return obj.get_total_amount()
    
    def get_receiver_photo_url(self, obj):
        """
        Return full URL for receiver_photo if it exists
        """
        if obj.receiver_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.receiver_photo.url)
            return obj.receiver_photo.url
        return None


class HawalaStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating hawala transaction status
    """
    
    class Meta:
        model = HawalaTransaction
        fields = ['status', 'notes']
    
    def validate_status(self, value):
        """Validate status transitions"""
        instance = self.instance
        if instance:
            current_status = instance.status
            
            # Define valid status transitions - simplified to only pending and completed
            valid_transitions = {
                'pending': ['completed'],
                'completed': []  # No transitions from completed
            }
            
            if value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot transition from '{current_status}' to '{value}'"
                )
        
        return value


class HawalaReceiptSerializer(serializers.ModelSerializer):
    """
    Serializer for HawalaReceipt model
    Provides secure receipt data without sensitive information
    """
    
    receipt_id = serializers.UUIDField(read_only=True)
    generated_at = serializers.DateTimeField(read_only=True)
    hawala_number = serializers.CharField(source='hawala_transaction.hawala_number', read_only=True)
    
    class Meta:
        model = HawalaReceipt
        fields = [
            'receipt_id', 'generated_at', 'hawala_number',
            'receipt_data', 'is_active'
        ]
        read_only_fields = [
            'receipt_id', 'generated_at', 'hawala_number',
            'receipt_data', 'is_active'
        ]

    def to_representation(self, instance):
        """Custom representation to ensure no sensitive data is exposed"""
        data = super().to_representation(instance)
        
        # Ensure receipt_data contains only public information
        if 'receipt_data' in data and data['receipt_data']:
            receipt_data = data['receipt_data']
            
            # Remove any sensitive information from sender_saraf
            if 'sender_saraf' in receipt_data:
                sender_info = receipt_data['sender_saraf']
                # Only keep public information
                safe_sender_info = {
                    'saraf_name': sender_info.get('saraf_name'),
                    'exchange_name': sender_info.get('exchange_name'),
                    'saraf_id': sender_info.get('saraf_id'),
                    'phone': sender_info.get('phone'),
                    'email': sender_info.get('email'),
                    'amu_pay_code': sender_info.get('amu_pay_code'),
                    'address': sender_info.get('address'),
                    'province': sender_info.get('province')
                }
                receipt_data['sender_saraf'] = safe_sender_info
            
            # Ensure employee info only contains names (no sensitive data)
            if 'employee_info' in receipt_data:
                employee_info = receipt_data['employee_info']
                safe_employee_info = {}
                for key, value in employee_info.items():
                    if isinstance(value, dict):
                        safe_employee_info[key] = {
                            'name': value.get('name'),
                            'username': value.get('username')
                        }
                    else:
                        safe_employee_info[key] = value
                receipt_data['employee_info'] = safe_employee_info
            
            data['receipt_data'] = receipt_data
        
        return data


class HawalaReceiptPublicSerializer(serializers.ModelSerializer):
    """
    Public serializer for receipt data - contains only customer-facing information
    """
    
    class Meta:
        model = HawalaReceipt
        fields = ['receipt_data']
    
    def to_representation(self, instance):
        """Return only customer-facing receipt data"""
        if not instance.receipt_data:
            return {}
        
        receipt_data = instance.receipt_data.copy()
        
        # Create customer-facing receipt with only necessary information
        customer_receipt = {
            'receipt_id': receipt_data.get('receipt_id'),
            'generated_at': receipt_data.get('generated_at'),
            'receipt_type': receipt_data.get('receipt_type'),
            'hawala_details': {
                'hawala_number': receipt_data.get('hawala_details', {}).get('hawala_number'),
                'amount': receipt_data.get('hawala_details', {}).get('amount'),
                'currency': receipt_data.get('hawala_details', {}).get('currency'),
                'transfer_fee': receipt_data.get('hawala_details', {}).get('transfer_fee'),
                'total_amount': receipt_data.get('hawala_details', {}).get('total_amount'),
                'created_at': receipt_data.get('hawala_details', {}).get('created_at'),
                'completed_at': receipt_data.get('hawala_details', {}).get('completed_at'),
                'status': receipt_data.get('hawala_details', {}).get('status')
            },
            'sender_saraf': {
                'saraf_name': receipt_data.get('sender_saraf', {}).get('saraf_name'),
                'exchange_name': receipt_data.get('sender_saraf', {}).get('exchange_name'),
                'phone': receipt_data.get('sender_saraf', {}).get('phone'),
                'address': receipt_data.get('sender_saraf', {}).get('address')
            },
            'receiver_info': receipt_data.get('receiver_info', {}),
            'destination_exchange': {
                'exchange_name': receipt_data.get('destination_exchange', {}).get('exchange_name'),
                'exchange_address': receipt_data.get('destination_exchange', {}).get('exchange_address')
            },
            'employee_info': {
                'handled_by': receipt_data.get('employee_info', {}).get('generated_by', {}).get('name')
            }
        }
        
        return customer_receipt
