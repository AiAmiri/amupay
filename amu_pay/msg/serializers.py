from rest_framework import serializers
from .models import Conversation, Message, MessageDelivery, MessageNotification
from saraf_account.models import SarafAccount, SarafEmployee

class MessageDeliverySerializer(serializers.ModelSerializer):
    recipient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MessageDelivery
        fields = ['delivery_id', 'recipient_name', 'delivery_status', 'sent_at', 'delivered_at', 'read_at']
    
    def get_recipient_name(self, obj):
        try:
            return obj.get_recipient_name()
        except Exception:
            return "Unknown Recipient"

class MessageSerializer(serializers.ModelSerializer):
    sender_display_name = serializers.CharField(source='get_sender_display_name', read_only=True)
    sender_employee_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()
    deliveries = MessageDeliverySerializer(many=True, read_only=True)
    attachment_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'content', 'message_type', 'attachment', 'attachment_url',
            'sender_display_name', 'sender_employee_name', 'file_size',
            'created_at', 'deliveries'
        ]
        read_only_fields = ['message_id', 'created_at']
        extra_kwargs = {
            'content': {'allow_blank': True, 'required': False}
        }
    
    def get_sender_employee_name(self, obj):
        """Get employee name if exists"""
        try:
            return obj.sender_employee.full_name if obj.sender_employee else None
        except Exception:
            return None
    
    def get_file_size(self, obj):
        """Get human-readable file size"""
        if obj.attachment:
            try:
                size = obj.attachment.size
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0:
                        return f"{size:.1f} {unit}"
                    size /= 1024.0
            except Exception:
                return None
        return None
    
    def get_attachment_url(self, obj):
        """Return full URL for attachment if it exists"""
        try:
            if obj.attachment:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.attachment.url)
                return obj.attachment.url
            return None
        except Exception:
            return None

class ConversationSerializer(serializers.ModelSerializer):
    saraf_participants = serializers.StringRelatedField(many=True, read_only=True)
    normal_user_participants = serializers.StringRelatedField(many=True, read_only=True)
    participant_names = serializers.CharField(source='get_participant_names', read_only=True)
    last_message = MessageSerializer(source='get_last_message', read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'conversation_type', 'title', 
            'saraf_participants', 'normal_user_participants', 'participant_names', 
            'last_message', 'unread_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request:
            # Try to get user info from JWT token
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                token_string = str(request.auth)
                token = AccessToken(token_string)
                user_type = token.get('user_type')
                
                if user_type == 'normal_user':
                    from normal_user_account.models import NormalUser
                    normal_user_id = token.get('user_id')
                    try:
                        normal_user = NormalUser.objects.get(user_id=normal_user_id)
                        return obj.get_unread_count(normal_user)
                    except NormalUser.DoesNotExist:
                        pass
                elif user_type == 'saraf':
                    saraf_id = token.get('saraf_id')
                    if saraf_id:
                        try:
                            saraf_account = SarafAccount.objects.get(saraf_id=saraf_id)
                            return obj.get_unread_count(saraf_account)
                        except SarafAccount.DoesNotExist:
                            pass
            except Exception:
                pass
        return 0

class CreateConversationSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text="List of SarafAccount IDs to include in conversation (must be exactly 2 for direct conversations)"
    )
    
    class Meta:
        model = Conversation
        fields = ['title', 'participant_ids']
    
    def validate_participant_ids(self, value):
        # Basic validation - just check that IDs are provided
        if not value:
            raise serializers.ValidationError("At least one participant ID is required")
        
        # Validate that all participant IDs exist
        existing_saraf_ids = SarafAccount.objects.filter(saraf_id__in=value).values_list('saraf_id', flat=True)
        missing_ids = set(value) - set(existing_saraf_ids)
        
        if missing_ids:
            raise serializers.ValidationError(f"Invalid SarafAccount IDs: {list(missing_ids)}")
        
        return value
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        
        # Always create direct conversations
        conversation = Conversation.objects.create(
            conversation_type='direct',
            **validated_data
        )
        
        # Add participants
        participants = SarafAccount.objects.filter(saraf_id__in=participant_ids)
        conversation.saraf_participants.set(participants)
        
        return conversation

class FlexibleCharField(serializers.CharField):
    """A CharField that handles multipart form data arrays"""
    
    def to_internal_value(self, data):
        
        # Handle None
        if data is None:
            return ""
        
        # Handle lists (multipart form data)
        if isinstance(data, list):
            if len(data) == 0:
                return ""
            data = data[0]
        
        # Convert to string
        return str(data)

class SendMessageSerializer(serializers.ModelSerializer):
    conversation_id = serializers.IntegerField(write_only=True)
    employee_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    content = FlexibleCharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Message
        fields = ['conversation_id', 'content', 'message_type', 'attachment', 'employee_id']
    
    def to_internal_value(self, data):
        """Override to handle multipart form data properly"""
        # Handle multipart form data that sends values as lists
        if hasattr(data, 'getlist'):
            # This is multipart form data
            processed_data = {}
            for field in self.Meta.fields:
                if field in data:
                    value = data.getlist(field)
                    if len(value) == 1:
                        processed_data[field] = value[0]
                    elif len(value) > 1:
                        processed_data[field] = value
                    else:
                        processed_data[field] = None
                else:
                    processed_data[field] = None
            return super().to_internal_value(processed_data)
        else:
            return super().to_internal_value(data)
    
    def validate_content(self, value):
        """Validate content field - very permissive"""
        # Handle None
        if value is None:
            return ""
        
        # Handle empty string
        if value == "":
            return ""
        
        # Handle lists (multipart form data)
        if isinstance(value, list):
            if len(value) == 0:
                return ""
            return str(value[0])
        
        # Convert anything else to string
        return str(value)
    
    def validate_conversation_id(self, value):
        try:
            conversation = Conversation.objects.get(conversation_id=value, is_active=True)
            return value
        except Conversation.DoesNotExist:
            raise serializers.ValidationError("Conversation not found or inactive")
    
    def validate_message_type(self, value):
        # Validate message type
        valid_types = ['text', 'image', 'audio']
        if value not in valid_types:
            raise serializers.ValidationError(f"Message type must be one of: {', '.join(valid_types)}")
        
        return value
    
    def validate_employee_id(self, value):
        if value is not None:
            try:
                SarafEmployee.objects.get(employee_id=value, is_active=True)
                return value
            except SarafEmployee.DoesNotExist:
                raise serializers.ValidationError("Employee not found or inactive")
        return value
    
    def validate(self, data):
        # Validate that either content or attachment is provided
        content = data.get('content', '')
        attachment = data.get('attachment')
        
        if not content and not attachment:
            raise serializers.ValidationError("Either content or attachment is required")
        
        # Validate file type based on message type
        message_type = data.get('message_type', 'text')
        
        if message_type == 'image' and attachment:
            allowed_image_extensions = ['jpg', 'jpeg', 'png', 'gif']
            file_extension = attachment.name.split('.')[-1].lower()
            if file_extension not in allowed_image_extensions:
                raise serializers.ValidationError("Invalid image file format")
        
        elif message_type == 'audio' and attachment:
            allowed_audio_extensions = ['mp3', 'wav', 'm4a', 'aac']
            file_extension = attachment.name.split('.')[-1].lower()
            if file_extension not in allowed_audio_extensions:
                raise serializers.ValidationError("Invalid audio file format")
        
        return data

class MessageStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageDelivery
        fields = ['delivery_status', 'read_at']
    
    def update(self, instance, validated_data):
        delivery_status = validated_data.get('delivery_status')
        
        if delivery_status == 'read':
            instance.mark_as_read()
        elif delivery_status == 'delivered':
            instance.mark_as_delivered()
        else:
            instance.delivery_status = delivery_status
            instance.save()
        
        return instance

class MessageNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageNotification
        fields = ['notification_id', 'is_read', 'created_at']

class ConversationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for conversation list view"""
    participant_names = serializers.CharField(source='get_participant_names', read_only=True)
    last_message_preview = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'conversation_type', 'title', 
            'participant_names', 'last_message_preview', 'unread_count',
            'updated_at'
        ]
    
    def get_last_message_preview(self, obj):
        last_message = obj.get_last_message()
        if last_message:
            preview = last_message.content[:100]
            if len(last_message.content) > 100:
                preview += "..."
            return {
                'content': preview,
                'sender': last_message.get_sender_display_name(),
                'message_type': last_message.message_type,
                'created_at': last_message.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request:
            # Try to get user info from JWT token
            try:
                from rest_framework_simplejwt.tokens import AccessToken
                token_string = str(request.auth)
                token = AccessToken(token_string)
                user_type = token.get('user_type')
                
                if user_type == 'normal_user':
                    from normal_user_account.models import NormalUser
                    normal_user_id = token.get('user_id')
                    try:
                        normal_user = NormalUser.objects.get(user_id=normal_user_id)
                        return obj.get_unread_count(normal_user)
                    except NormalUser.DoesNotExist:
                        pass
                elif user_type == 'saraf':
                    saraf_id = token.get('saraf_id')
                    if saraf_id:
                        try:
                            saraf_account = SarafAccount.objects.get(saraf_id=saraf_id)
                            return obj.get_unread_count(saraf_account)
                        except SarafAccount.DoesNotExist:
                            pass
            except Exception:
                pass
        return 0
