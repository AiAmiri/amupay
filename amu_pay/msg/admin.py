from django.contrib import admin
from .models import Conversation, Message, MessageDelivery, MessageNotification

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['conversation_id', 'conversation_type', 'title', 'is_active', 'created_at', 'updated_at']
    list_filter = ['conversation_type', 'is_active', 'created_at']
    search_fields = ['title', 'saraf_participants__full_name', 'normal_user_participants__full_name']
    readonly_fields = ['conversation_id', 'created_at', 'updated_at']
    filter_horizontal = ['saraf_participants', 'normal_user_participants']
    
    def get_participant_names(self, obj):
        return obj.get_participant_names()
    get_participant_names.short_description = 'Participants'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['message_id', 'get_sender_display', 'message_type', 'get_conversation_info', 'created_at']
    list_filter = ['message_type', 'created_at', 'sender_saraf', 'sender_normal_user']
    search_fields = ['content', 'sender_saraf__full_name', 'sender_normal_user__full_name', 'sender_employee__full_name']
    readonly_fields = ['message_id', 'created_at']
    
    def get_sender_display(self, obj):
        return obj.get_sender_display_name()
    get_sender_display.short_description = 'Sender'
    
    def get_conversation_info(self, obj):
        return f"Conv {obj.conversation.conversation_id} ({obj.conversation.conversation_type})"
    get_conversation_info.short_description = 'Conversation'

@admin.register(MessageDelivery)
class MessageDeliveryAdmin(admin.ModelAdmin):
    list_display = ['delivery_id', 'get_message_info', 'get_recipient_display', 'delivery_status', 'sent_at', 'read_at']
    list_filter = ['delivery_status', 'sent_at']
    search_fields = ['recipient_saraf__full_name', 'recipient_normal_user__full_name', 'message__content']
    readonly_fields = ['delivery_id', 'sent_at']
    
    def get_message_info(self, obj):
        return f"Msg {obj.message.message_id}: {obj.message.content[:30]}..."
    get_message_info.short_description = 'Message'
    
    def get_recipient_display(self, obj):
        return obj.get_recipient_name()
    get_recipient_display.short_description = 'Recipient'

@admin.register(MessageNotification)
class MessageNotificationAdmin(admin.ModelAdmin):
    list_display = ['notification_id', 'get_message_info', 'get_recipient_display', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['recipient_saraf__full_name', 'recipient_normal_user__full_name', 'message__content']
    readonly_fields = ['notification_id', 'created_at']
    
    def get_message_info(self, obj):
        return f"Msg {obj.message.message_id}: {obj.message.content[:30]}..."
    get_message_info.short_description = 'Message'
    
    def get_recipient_display(self, obj):
        return obj.get_recipient_name()
    get_recipient_display.short_description = 'Recipient'
