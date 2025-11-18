# ============================================================================
# NORMAL USER MESSAGING VIEWS
# ============================================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count

from .models import Conversation, Message, MessageDelivery, MessageNotification
from .serializers import (
    ConversationSerializer, SendMessageSerializer, MessageSerializer,
    MessageStatusSerializer, ConversationListSerializer, MessageNotificationSerializer
)
from saraf_account.models import SarafAccount, SarafEmployee, ActionLog
from normal_user_account.models import NormalUser
import logging

logger = logging.getLogger(__name__)

def get_user_info_from_token(request):
    """Helper function to extract user info from JWT token"""
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        
        # Get the raw token string
        token_string = str(request.auth)
        
        # Create AccessToken object
        token = AccessToken(token_string)
        
        user_info = {
            'saraf_id': token.get('saraf_id'),
            'employee_id': token.get('employee_id'),
            'user_type': token.get('user_type'),
            'user_id': token.get('user_id'),
            'normal_user_id': token.get('user_id') if token.get('user_type') == 'normal_user' else None,
            'full_name': token.get('full_name'),
            'email': token.get('email'),
            'whatsapp_number': token.get('whatsapp_number')
        }
        
        return user_info
    except Exception as e:
        logger.error(f"Error extracting user info from token: {str(e)}")
        return None

class NormalUserConversationListView(APIView):
    """
    List all conversations for the authenticated normal user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get user info from JWT token
            user_info = get_user_info_from_token(request)
            
            if not user_info or user_info.get('user_type') != 'normal_user' or not user_info.get('normal_user_id'):
                return Response({'error': 'Invalid normal user token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            normal_user_id = user_info['normal_user_id']
            normal_user = NormalUser.objects.get(user_id=normal_user_id)
            
            # Get conversations where user is a participant and not deleted by them
            conversations = Conversation.objects.filter(
                normal_user_participants=normal_user,
                is_active=True
            ).exclude(
                deleted_by_normal_user_participants=normal_user
            ).annotate(
                unread_count=Count(
                    'messages__deliveries',
                    filter=Q(
                        messages__deliveries__recipient_normal_user=normal_user,
                        messages__deliveries__delivery_status__in=['sent', 'delivered']
                    )
                )
            ).order_by('-updated_at')
            
            # Pagination
            page = request.GET.get('page', 1)
            page_size = request.GET.get('page_size', 20)
            paginator = Paginator(conversations, page_size)
            page_obj = paginator.get_page(page)
            
            serializer = ConversationListSerializer(page_obj.object_list, many=True, context={'request': request})
            
            return Response({
                'conversations': serializer.data,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }, status=status.HTTP_200_OK)
            
        except NormalUser.DoesNotExist:
            return Response({'error': 'Normal user account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in NormalUserConversationListView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NormalUserCreateConversationView(APIView):
    """
    Create a new conversation between normal user and saraf
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get normal user from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or user_info.get('user_type') != 'normal_user' or not user_info.get('normal_user_id'):
                return Response({'error': 'Invalid normal user token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            normal_user_id = user_info['normal_user_id']
            normal_user = NormalUser.objects.get(user_id=normal_user_id)
            
            # Get saraf_id from request
            saraf_id = request.data.get('saraf_id')
            if not saraf_id:
                return Response({'error': 'saraf_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                saraf_account = SarafAccount.objects.get(saraf_id=saraf_id, is_active=True)
            except SarafAccount.DoesNotExist:
                return Response({'error': 'Saraf account not found or inactive'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if conversation already exists
            existing_conversation = Conversation.objects.filter(
                saraf_participants=saraf_account,
                normal_user_participants=normal_user,
                is_active=True
            ).first()
            
            if existing_conversation:
                serializer = ConversationSerializer(existing_conversation, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            # Create new conversation
            conversation = Conversation.objects.create(
                conversation_type='normal_to_saraf',
                title=f"Chat with {saraf_account.full_name}"
            )
            
            # Add participants
            conversation.saraf_participants.add(saraf_account)
            conversation.normal_user_participants.add(normal_user)
            
            serializer = ConversationSerializer(conversation, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except NormalUser.DoesNotExist:
            return Response({'error': 'Normal user account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in NormalUserCreateConversationView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NormalUserConversationDetailView(APIView):
    """
    Get conversation details and messages for normal user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversation_id):
        try:
            # Get normal user from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or user_info.get('user_type') != 'normal_user' or not user_info.get('normal_user_id'):
                return Response({'error': 'Invalid normal user token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            normal_user_id = user_info['normal_user_id']
            normal_user = NormalUser.objects.get(user_id=normal_user_id)
            
            # Get conversation
            try:
                conversation = Conversation.objects.get(
                    conversation_id=conversation_id,
                    normal_user_participants=normal_user,
                    is_active=True
                )
                # Check if conversation is visible to user (not deleted by them)
                if not conversation.is_visible_to_user(normal_user):
                    return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
            except Conversation.DoesNotExist:
                return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get messages with pagination
            messages = conversation.messages.all().order_by('created_at')
            
            page = request.GET.get('page', 1)
            page_size = request.GET.get('page_size', 50)
            paginator = Paginator(messages, page_size)
            page_obj = paginator.get_page(page)
            
            # Mark messages as read for this user
            MessageDelivery.objects.filter(
                message__conversation=conversation,
                recipient_normal_user=normal_user,
                delivery_status__in=['sent', 'delivered']
            ).update(
                delivery_status='read',
                read_at=timezone.now()
            )
            
            conversation_serializer = ConversationSerializer(conversation, context={'request': request})
            messages_serializer = MessageSerializer(page_obj.object_list, many=True)
            
            return Response({
                'conversation': conversation_serializer.data,
                'messages': messages_serializer.data,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }, status=status.HTTP_200_OK)
            
        except NormalUser.DoesNotExist:
            return Response({'error': 'Normal user account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in NormalUserConversationDetailView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NormalUserDeleteConversationView(APIView):
    """Delete conversation for normal user (soft delete)"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, conversation_id):
        try:
            # Get user info from token
            user_info = get_user_info_from_token(request)
            
            if user_info.get('user_type') != 'normal_user':
                return Response({'error': 'Invalid normal user token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            normal_user_id = user_info['normal_user_id']
            normal_user = NormalUser.objects.get(user_id=normal_user_id)
            
            # Get conversation
            try:
                conversation = Conversation.objects.get(
                    conversation_id=conversation_id,
                    normal_user_participants=normal_user,
                    is_active=True
                )
            except Conversation.DoesNotExist:
                return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Soft delete conversation for this user
            conversation.delete_for_user(normal_user)
            
            return Response({
                'message': 'Conversation deleted successfully',
                'conversation_id': conversation_id
            })
            
        except Exception as e:
            logger.error(f"Error in NormalUserDeleteConversationView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NormalUserSendMessageView(APIView):
    """
    Send a message from normal user to saraf
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        try:
            # Get normal user from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or user_info.get('user_type') != 'normal_user' or not user_info.get('normal_user_id'):
                return Response({'error': 'Invalid normal user token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            normal_user_id = user_info['normal_user_id']
            normal_user = NormalUser.objects.get(user_id=normal_user_id)
            
            serializer = SendMessageSerializer(data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    # Get conversation
                    conversation_id = serializer.validated_data['conversation_id']
                    conversation = Conversation.objects.get(conversation_id=conversation_id)
                    
                    # Verify user is participant
                    if normal_user not in conversation.normal_user_participants.all():
                        return Response({'error': 'You are not a participant in this conversation'}, status=status.HTTP_403_FORBIDDEN)
                    
                    # Create message
                    message = Message.objects.create(
                        conversation=conversation,
                        sender_normal_user=normal_user,
                        content=serializer.validated_data['content'],
                        message_type=serializer.validated_data['message_type'],
                        attachment=serializer.validated_data.get('attachment')
                    )
                    
                    # Create delivery records for saraf participants
                    saraf_recipients = conversation.saraf_participants.all()
                    deliveries = []
                    for recipient in saraf_recipients:
                        deliveries.append(MessageDelivery(
                            message=message,
                            recipient_saraf=recipient,
                            delivery_status='sent'
                        ))
                    MessageDelivery.objects.bulk_create(deliveries)
                    
                    # Update conversation timestamp
                    conversation.updated_at = timezone.now()
                    conversation.save(update_fields=['updated_at'])
                    
                    # Create in-app notifications for saraf recipients
                    self.create_in_app_notifications(message, saraf_recipients)
                
                response_serializer = MessageSerializer(message)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except NormalUser.DoesNotExist:
            return Response({'error': 'Normal user account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in NormalUserSendMessageView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create_in_app_notifications(self, message, saraf_recipients):
        """Create in-app notifications for saraf recipients"""
        notifications = []
        for recipient in saraf_recipients:
            notifications.append(MessageNotification(
                message=message,
                recipient_saraf=recipient,
                is_read=False
            ))
        MessageNotification.objects.bulk_create(notifications)


class NormalUserMessageStatusView(APIView):
    """
    Update message delivery status for normal user
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, message_id):
        try:
            # Get normal user from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or user_info.get('user_type') != 'normal_user' or not user_info.get('normal_user_id'):
                return Response({'error': 'Invalid normal user token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            normal_user_id = user_info['normal_user_id']
            normal_user = NormalUser.objects.get(user_id=normal_user_id)
            
            # Get message delivery record
            try:
                delivery = MessageDelivery.objects.get(
                    message_id=message_id,
                    recipient_normal_user=normal_user
                )
            except MessageDelivery.DoesNotExist:
                # Check if the user is the sender of the message
                try:
                    message = Message.objects.get(message_id=message_id, sender_normal_user=normal_user)
                    # User is the sender, they can't update delivery status for their own messages
                    return Response({'error': 'You cannot update delivery status for messages you sent'}, status=status.HTTP_400_BAD_REQUEST)
                except Message.DoesNotExist:
                    return Response({'error': 'Message not found or you are not authorized to update its status'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = MessageStatusSerializer(delivery, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Status updated successfully'}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except NormalUser.DoesNotExist:
            return Response({'error': 'Normal user account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in NormalUserMessageStatusView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NormalUserInAppNotificationsView(APIView):
    """
    Get in-app notifications for normal user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get normal user from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or user_info.get('user_type') != 'normal_user' or not user_info.get('normal_user_id'):
                return Response({'error': 'Invalid normal user token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            normal_user_id = user_info['normal_user_id']
            normal_user = NormalUser.objects.get(user_id=normal_user_id)
            
            # Get unread notifications
            notifications = MessageNotification.objects.filter(
                recipient_normal_user=normal_user,
                is_read=False
            ).order_by('-created_at')
            
            # Pagination
            page = request.GET.get('page', 1)
            page_size = request.GET.get('page_size', 20)
            paginator = Paginator(notifications, page_size)
            page_obj = paginator.get_page(page)
            
            serializer = MessageNotificationSerializer(page_obj.object_list, many=True)
            
            return Response({
                'notifications': serializer.data,
                'unread_count': notifications.count(),
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }, status=status.HTTP_200_OK)
            
        except NormalUser.DoesNotExist:
            return Response({'error': 'Normal user account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in NormalUserInAppNotificationsView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, notification_id=None):
        """Mark notification as read"""
        try:
            # Get normal user from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or user_info.get('user_type') != 'normal_user' or not user_info.get('normal_user_id'):
                return Response({'error': 'Invalid normal user token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            normal_user_id = user_info['normal_user_id']
            normal_user = NormalUser.objects.get(user_id=normal_user_id)
            
            if notification_id:
                # Mark specific notification as read
                try:
                    notification = MessageNotification.objects.get(
                        notification_id=notification_id,
                        recipient_normal_user=normal_user
                    )
                    notification.is_read = True
                    notification.save()
                    return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
                except MessageNotification.DoesNotExist:
                    return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Mark all notifications as read
                MessageNotification.objects.filter(
                    recipient_normal_user=normal_user,
                    is_read=False
                ).update(is_read=True)
                return Response({'message': 'All notifications marked as read'}, status=status.HTTP_200_OK)
            
        except NormalUser.DoesNotExist:
            return Response({'error': 'Normal user account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in NormalUserInAppNotificationsView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
