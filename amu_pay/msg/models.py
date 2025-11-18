from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import os

def message_file_upload_path(instance, filename):
    """Generate upload path for message files"""
    return f'message_files/{instance.conversation.conversation_id}/{filename}'

class Conversation(models.Model):
    """
    Direct conversation between SarafAccounts and/or NormalUsers
    """
    CONVERSATION_TYPE_CHOICES = [
        ('direct', 'Direct Message'),
        ('saraf_to_normal', 'Saraf to Normal User'),
        ('normal_to_saraf', 'Normal User to Saraf'),
    ]
    
    conversation_id = models.BigAutoField(primary_key=True)
    saraf_participants = models.ManyToManyField('saraf_account.SarafAccount', related_name='conversations', blank=True)
    normal_user_participants = models.ManyToManyField('normal_user_account.NormalUser', related_name='conversations', blank=True)
    conversation_type = models.CharField(max_length=20, choices=CONVERSATION_TYPE_CHOICES, default='direct')
    title = models.CharField(max_length=255, blank=True, help_text="Optional title for the conversation")
    is_active = models.BooleanField(default=True)
    
    # Soft delete fields for individual users
    deleted_by_saraf_participants = models.ManyToManyField('saraf_account.SarafAccount', related_name='deleted_conversations', blank=True)
    deleted_by_normal_user_participants = models.ManyToManyField('normal_user_account.NormalUser', related_name='deleted_conversations', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['conversation_type', 'is_active']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        if self.title:
            return f"{self.title} ({self.conversation_type})"
        return f"Conversation {self.conversation_id} ({self.conversation_type})"
    
    def get_participant_names(self):
        """Get comma-separated list of participant names"""
        saraf_names = [p.full_name for p in self.saraf_participants.all()]
        normal_names = [p.full_name for p in self.normal_user_participants.all()]
        return ', '.join(saraf_names + normal_names)
    
    def get_all_participants(self):
        """Get all participants (both Saraf and NormalUser)"""
        participants = []
        participants.extend(self.saraf_participants.all())
        participants.extend(self.normal_user_participants.all())
        return participants
    
    def get_last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.order_by('-created_at').first()
    
    def get_unread_count(self, user):
        """Get unread message count for a specific user"""
        # Handle both SarafAccount and NormalUser
        if hasattr(user, 'saraf_id'):
            # SarafAccount
            return self.messages.filter(
                deliveries__recipient_saraf=user,
                deliveries__delivery_status__in=['sent', 'delivered']
            ).count()
        elif hasattr(user, 'user_id'):
            # NormalUser
            return self.messages.filter(
                deliveries__recipient_normal_user=user,
                deliveries__delivery_status__in=['sent', 'delivered']
            ).count()
        return 0
    
    def is_deleted_by_user(self, user):
        """Check if conversation is deleted by specific user"""
        if hasattr(user, 'saraf_id'):
            # SarafAccount
            return self.deleted_by_saraf_participants.filter(saraf_id=user.saraf_id).exists()
        elif hasattr(user, 'user_id'):
            # NormalUser
            return self.deleted_by_normal_user_participants.filter(user_id=user.user_id).exists()
        return False
    
    def delete_for_user(self, user):
        """Soft delete conversation for specific user"""
        if hasattr(user, 'saraf_id'):
            # SarafAccount
            self.deleted_by_saraf_participants.add(user)
        elif hasattr(user, 'user_id'):
            # NormalUser
            self.deleted_by_normal_user_participants.add(user)
        self.save()
    
    def restore_for_user(self, user):
        """Restore conversation for specific user"""
        if hasattr(user, 'saraf_id'):
            # SarafAccount
            self.deleted_by_saraf_participants.remove(user)
        elif hasattr(user, 'user_id'):
            # NormalUser
            self.deleted_by_normal_user_participants.remove(user)
        self.save()
    
    def is_visible_to_user(self, user):
        """Check if conversation is visible to specific user (not deleted by them)"""
        return not self.is_deleted_by_user(user)

class Message(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('audio', 'Audio'),
    ]
    
    message_id = models.BigAutoField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender_saraf = models.ForeignKey('saraf_account.SarafAccount', on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    sender_normal_user = models.ForeignKey('normal_user_account.NormalUser', on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    sender_employee = models.ForeignKey('saraf_account.SarafEmployee', on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_messages')
    content = models.TextField(help_text="Text content of the message")
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text')
    attachment = models.FileField(
        upload_to=message_file_upload_path,
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'mp3', 'wav', 'm4a', 'aac'])
        ],
        help_text="Audio or image file attachment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender_saraf', 'created_at']),
            models.Index(fields=['message_type']),
        ]
    
    def __str__(self):
        sender_name = self.get_sender_display_name()
        return f"{sender_name}: {self.content[:50]}{'...' if len(self.content) > 50 else ''}"
    
    def get_sender_display_name(self):
        """Get the display name of the sender"""
        if self.sender_employee:
            return f"{self.sender_saraf.full_name} ({self.sender_employee.full_name})"
        elif self.sender_saraf:
            return self.sender_saraf.full_name
        elif self.sender_normal_user:
            return self.sender_normal_user.full_name
        return "Unknown Sender"
    
    def get_file_size(self):
        """Get human-readable file size"""
        if self.attachment:
            size = self.attachment.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return None
    
    def is_file_message(self):
        """Check if this message has a file attachment"""
        return bool(self.attachment)

class MessageDelivery(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    delivery_id = models.BigAutoField(primary_key=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='deliveries')
    recipient_saraf = models.ForeignKey('saraf_account.SarafAccount', on_delete=models.CASCADE, related_name='message_deliveries', null=True, blank=True)
    recipient_normal_user = models.ForeignKey('normal_user_account.NormalUser', on_delete=models.CASCADE, related_name='message_deliveries', null=True, blank=True)
    delivery_status = models.CharField(max_length=10, choices=DELIVERY_STATUS_CHOICES, default='sent')
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Message Delivery'
        verbose_name_plural = 'Message Deliveries'
        indexes = [
            models.Index(fields=['recipient_saraf', 'delivery_status']),
            models.Index(fields=['recipient_normal_user', 'delivery_status']),
            models.Index(fields=['message', 'recipient_saraf']),
            models.Index(fields=['message', 'recipient_normal_user']),
        ]
    
    def get_recipient(self):
        """Get the recipient (either SarafAccount or NormalUser)"""
        if self.recipient_saraf:
            return self.recipient_saraf
        elif self.recipient_normal_user:
            return self.recipient_normal_user
        return None
    
    def get_recipient_name(self):
        """Get the recipient's name"""
        recipient = self.get_recipient()
        if recipient:
            return recipient.full_name
        return "Unknown Recipient"
    
    def __str__(self):
        return f"{self.message} -> {self.get_recipient_name()} ({self.delivery_status})"
    
    def mark_as_delivered(self):
        """Mark message as delivered"""
        self.delivery_status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['delivery_status', 'delivered_at'])
    
    def mark_as_read(self):
        """Mark message as read"""
        self.delivery_status = 'read'
        self.read_at = timezone.now()
        if not self.delivered_at:
            self.delivered_at = self.read_at
        self.save(update_fields=['delivery_status', 'read_at', 'delivered_at'])

class MessageNotification(models.Model):
    """
    Simple in-app notification system for new messages
    """
    notification_id = models.BigAutoField(primary_key=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    recipient_saraf = models.ForeignKey('saraf_account.SarafAccount', on_delete=models.CASCADE, related_name='message_notifications', null=True, blank=True)
    recipient_normal_user = models.ForeignKey('normal_user_account.NormalUser', on_delete=models.CASCADE, related_name='message_notifications', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Message Notification'
        verbose_name_plural = 'Message Notifications'
        indexes = [
            models.Index(fields=['recipient_saraf', 'is_read']),
            models.Index(fields=['recipient_normal_user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def get_recipient(self):
        """Get the recipient (either SarafAccount or NormalUser)"""
        if self.recipient_saraf:
            return self.recipient_saraf
        elif self.recipient_normal_user:
            return self.recipient_normal_user
        return None
    
    def get_recipient_name(self):
        """Get the recipient's name"""
        recipient = self.get_recipient()
        if recipient:
            return recipient.full_name
        return "Unknown Recipient"
    
    def __str__(self):
        return f"In-app notification for {self.message} to {self.get_recipient_name()}"
