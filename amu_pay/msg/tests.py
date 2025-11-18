from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

from .models import Conversation, Message, MessageDelivery, MessageNotification
from saraf_account.models import SarafAccount, SarafEmployee

class MessageModelTests(TestCase):
    def setUp(self):
        # Create test saraf accounts
        self.saraf1 = SarafAccount.objects.create(
            full_name="Test Saraf 1",
            exchange_name="Test Exchange 1",
            email="test1@example.com",
            license_no="LIC001",
            amu_pay_code="TEST001",
            province="Test Province"
        )
        self.saraf1.set_password("TestPass123!")
        
        self.saraf2 = SarafAccount.objects.create(
            full_name="Test Saraf 2",
            exchange_name="Test Exchange 2",
            email="test2@example.com",
            license_no="LIC002",
            amu_pay_code="TEST002",
            province="Test Province"
        )
        self.saraf2.set_password("TestPass123!")
        
        # Create test employee
        self.employee = SarafEmployee.objects.create(
            saraf_account=self.saraf1,
            username="test_employee",
            full_name="Test Employee",
        )
        self.employee.set_password("TestPass123!")
    
    def test_conversation_creation(self):
        """Test creating a conversation"""
        conversation = Conversation.objects.create(
            conversation_type='direct',
            title='Test Conversation'
        )
        conversation.participants.set([self.saraf1, self.saraf2])
        
        self.assertEqual(conversation.conversation_type, 'direct')
        self.assertEqual(conversation.participants.count(), 2)
        self.assertIn(self.saraf1, conversation.participants.all())
        self.assertIn(self.saraf2, conversation.participants.all())
    
    def test_message_creation(self):
        """Test creating a message"""
        conversation = Conversation.objects.create(conversation_type='direct')
        conversation.participants.set([self.saraf1, self.saraf2])
        
        message = Message.objects.create(
            conversation=conversation,
            sender_saraf=self.saraf1,
            content="Hello, this is a test message",
            message_type='text'
        )
        
        self.assertEqual(message.content, "Hello, this is a test message")
        self.assertEqual(message.sender_saraf, self.saraf1)
        self.assertEqual(message.message_type, 'text')
        self.assertEqual(message.get_sender_display_name(), self.saraf1.full_name)
    
    def test_employee_message_creation(self):
        """Test creating a message by an employee"""
        conversation = Conversation.objects.create(conversation_type='direct')
        conversation.participants.set([self.saraf1, self.saraf2])
        
        message = Message.objects.create(
            conversation=conversation,
            sender_saraf=self.saraf1,
            sender_employee=self.employee,
            content="Hello from employee",
            message_type='text'
        )
        
        expected_display_name = f"{self.saraf1.full_name} ({self.employee.full_name})"
        self.assertEqual(message.get_sender_display_name(), expected_display_name)
    
    def test_message_delivery(self):
        """Test message delivery tracking"""
        conversation = Conversation.objects.create(conversation_type='direct')
        conversation.participants.set([self.saraf1, self.saraf2])
        
        message = Message.objects.create(
            conversation=conversation,
            sender_saraf=self.saraf1,
            content="Test message",
            message_type='text'
        )
        
        delivery = MessageDelivery.objects.create(
            message=message,
            recipient=self.saraf2,
            delivery_status='sent'
        )
        
        self.assertEqual(delivery.delivery_status, 'sent')
        self.assertEqual(delivery.recipient, self.saraf2)
        
        # Test marking as read
        delivery.mark_as_read()
        self.assertEqual(delivery.delivery_status, 'read')
        self.assertIsNotNone(delivery.read_at)

class MessageAPITests(TestCase):
    """Simplified API tests focusing on model functionality"""
    def setUp(self):
        # Create test saraf accounts
        self.saraf1 = SarafAccount.objects.create(
            full_name="Test Saraf 1",
            exchange_name="Test Exchange 1",
            email="test1@example.com",
            license_no="LIC001",
            amu_pay_code="TEST001",
            province="Test Province"
        )
        self.saraf1.set_password("TestPass123!")
        
        self.saraf2 = SarafAccount.objects.create(
            full_name="Test Saraf 2",
            exchange_name="Test Exchange 2",
            email="test2@example.com",
            license_no="LIC002",
            amu_pay_code="TEST002",
            province="Test Province"
        )
        self.saraf2.set_password("TestPass123!")
        
        # Create conversation
        self.conversation = Conversation.objects.create(conversation_type='direct')
        self.conversation.participants.set([self.saraf1, self.saraf2])
    
    def test_conversation_functionality(self):
        """Test conversation model functionality"""
        # Test conversation creation
        self.assertEqual(self.conversation.conversation_type, 'direct')
        self.assertEqual(self.conversation.participants.count(), 2)
        
        # Test participant names
        participant_names = self.conversation.get_participant_names()
        self.assertIn('Test Saraf 1', participant_names)
        self.assertIn('Test Saraf 2', participant_names)
    
    def test_message_creation_and_delivery(self):
        """Test message creation and delivery tracking"""
        # Create a message
        message = Message.objects.create(
            conversation=self.conversation,
            sender_saraf=self.saraf1,
            content='Test message for delivery',
            message_type='text'
        )
        
        # Create delivery record
        delivery = MessageDelivery.objects.create(
            message=message,
            recipient=self.saraf2,
            delivery_status='sent'
        )
        
        # Test delivery tracking
        self.assertEqual(delivery.delivery_status, 'sent')
        self.assertEqual(delivery.recipient, self.saraf2)
        
        # Test marking as delivered
        delivery.mark_as_delivered()
        self.assertEqual(delivery.delivery_status, 'delivered')
        self.assertIsNotNone(delivery.delivered_at)
        
        # Test marking as read
        delivery.mark_as_read()
        self.assertEqual(delivery.delivery_status, 'read')
        self.assertIsNotNone(delivery.read_at)
    
    def test_in_app_notifications(self):
        """Test in-app notification system"""
        # Create a message
        message = Message.objects.create(
            conversation=self.conversation,
            sender_saraf=self.saraf1,
            content='Test notification message',
            message_type='text'
        )
        
        # Create notification
        notification = MessageNotification.objects.create(
            message=message,
            recipient=self.saraf2,
            is_read=False
        )
        
        # Test notification creation
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.recipient, self.saraf2)
        self.assertEqual(notification.message, message)
        
        # Test marking as read
        notification.is_read = True
        notification.save()
        self.assertTrue(notification.is_read)
    
    def test_employee_message_tracking(self):
        """Test employee message tracking"""
        # Create employee
        employee = SarafEmployee.objects.create(
            saraf_account=self.saraf1,
            username="test_employee",
            full_name="Test Employee",
        )
        employee.set_password("TestPass123!")
        
        # Create message by employee
        message = Message.objects.create(
            conversation=self.conversation,
            sender_saraf=self.saraf1,
            sender_employee=employee,
            content='Message from employee',
            message_type='text'
        )
        
        # Test employee tracking
        expected_display_name = f"{self.saraf1.full_name} ({employee.full_name})"
        self.assertEqual(message.get_sender_display_name(), expected_display_name)
        self.assertEqual(message.sender_employee, employee)
    
    def test_message_search_functionality(self):
        """Test message search functionality"""
        # Create test messages
        Message.objects.create(
            conversation=self.conversation,
            sender_saraf=self.saraf1,
            content='Searchable test message',
            message_type='text'
        )
        
        Message.objects.create(
            conversation=self.conversation,
            sender_saraf=self.saraf1,
            content='Another message',
            message_type='text'
        )
        
        # Test search functionality
        searchable_messages = Message.objects.filter(content__icontains='Searchable')
        self.assertEqual(searchable_messages.count(), 1)
        self.assertEqual(searchable_messages.first().content, 'Searchable test message')
    
    def test_conversation_statistics(self):
        """Test conversation statistics"""
        # Create multiple messages
        Message.objects.create(
            conversation=self.conversation,
            sender_saraf=self.saraf1,
            content='Message 1',
            message_type='text'
        )
        
        Message.objects.create(
            conversation=self.conversation,
            sender_saraf=self.saraf1,
            content='Message 2',
            message_type='text'
        )
        
        # Test statistics
        total_messages = Message.objects.filter(sender_saraf=self.saraf1).count()
        self.assertEqual(total_messages, 2)
        
        # Test unread count
        unread_count = self.conversation.get_unread_count(self.saraf2)
        self.assertEqual(unread_count, 0)  # No deliveries created in this test