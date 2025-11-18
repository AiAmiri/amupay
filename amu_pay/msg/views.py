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
    ConversationSerializer, CreateConversationSerializer, MessageSerializer,
    SendMessageSerializer, MessageStatusSerializer,
    ConversationListSerializer, MessageNotificationSerializer
)
from saraf_account.models import SarafAccount, SarafEmployee, ActionLog
from normal_user_account.models import NormalUser
from .normal_user_views import (
    NormalUserConversationListView,
    NormalUserCreateConversationView,
    NormalUserConversationDetailView,
    NormalUserSendMessageView,
    NormalUserMessageStatusView,
    NormalUserInAppNotificationsView
)
# Removed external notification imports - keeping it simple with in-app notifications only
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

class ConversationListView(APIView):
    """
    List all conversations for the authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get user info from JWT token
            user_info = get_user_info_from_token(request)
            
            if not user_info or not user_info.get('saraf_id'):
                return Response({'error': 'Invalid user token - no saraf_id found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = SarafAccount.objects.get(saraf_id=saraf_id)
            
            # Check chat permission for employees
            if user_info.get('user_type') == 'employee' and user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('chat'):
                        return Response({'error': 'You do not have permission to chat'}, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get conversations where user is a participant and not deleted by them
            conversations = Conversation.objects.filter(
                saraf_participants__in=[saraf_account],
                is_active=True
            ).exclude(
                deleted_by_saraf_participants__in=[saraf_account]
            ).annotate(
                unread_count=Count(
                    'messages__deliveries',
                    filter=Q(
                        messages__deliveries__recipient_saraf=saraf_account,
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
            
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in ConversationListView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateConversationView(APIView):
    """
    Create a new conversation
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get saraf account from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({'error': 'Invalid user token - no saraf_id found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = SarafAccount.objects.get(saraf_id=saraf_id)
            
            # Check chat permission for employees
            if user_info.get('user_type') == 'employee' and user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('chat'):
                        return Response({'error': 'You do not have permission to chat'}, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = CreateConversationSerializer(data=request.data)
            if serializer.is_valid():
                # Add current user to participants
                participant_ids = serializer.validated_data['participant_ids'].copy()
                if saraf_id not in participant_ids:
                    participant_ids.append(saraf_id)
                
                # Ensure only direct conversations with exactly 2 participants
                if len(participant_ids) != 2:
                    return Response({'error': 'Direct conversations must have exactly 2 participants'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Validate that all participant IDs exist
                existing_saraf_ids = SarafAccount.objects.filter(saraf_id__in=participant_ids).values_list('saraf_id', flat=True)
                missing_ids = set(participant_ids) - set(existing_saraf_ids)
                
                if missing_ids:
                    return Response({'error': f'Invalid SarafAccount IDs: {list(missing_ids)}'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Check if conversation already exists between these two participants
                from django.db.models import Q, Count
                existing_conversation = Conversation.objects.annotate(
                    participant_count=Count('saraf_participants')
                ).filter(
                    conversation_type='direct',
                    is_active=True,
                    participant_count=2
                ).filter(
                    saraf_participants__saraf_id=participant_ids[0]
                ).filter(
                    saraf_participants__saraf_id=participant_ids[1]
                ).first()
                
                if existing_conversation:
                    response_serializer = ConversationSerializer(existing_conversation, context={'request': request})
                    return Response({
                        'message': 'Conversation already exists',
                        'conversation': response_serializer.data
                    }, status=status.HTTP_200_OK)
                
                serializer.validated_data['participant_ids'] = participant_ids
                
                conversation = serializer.save()
                
                # Log the action
                # Determine user_type and user_id from user_info extracted from token
                if user_info.get('user_type') == 'employee' and user_info.get('employee_id'):
                    action_user_type = 'employee'
                    action_user_id = user_info['employee_id']
                    # Get employee name for logging
                    try:
                        employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                        action_user_name = employee.full_name
                    except SarafEmployee.DoesNotExist:
                        action_user_name = saraf_account.full_name
                else:
                    action_user_type = 'saraf'
                    action_user_id = saraf_id
                    action_user_name = saraf_account.full_name
                
                ActionLog.objects.create(
                    saraf=saraf_account,
                    user_type=action_user_type,
                    user_id=action_user_id,
                    user_name=action_user_name,
                    action_type='create_conversation',
                    description=f'Created conversation {conversation.conversation_id}',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    metadata={'conversation_id': conversation.conversation_id, 'participant_count': len(participant_ids)}
                )
                
                response_serializer = ConversationSerializer(conversation, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in CreateConversationView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class ConversationDetailView(APIView):
    """
    Get conversation details and messages
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversation_id):
        try:
            # Get saraf account from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({'error': 'Invalid user token - no saraf_id found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = SarafAccount.objects.get(saraf_id=saraf_id)
            
            # Check chat permission for employees
            if user_info.get('user_type') == 'employee' and user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    
                    # Ensure permissions are initialized if empty
                    if not employee.permissions or len(employee.permissions) == 0:
                        from saraf_account.models import DEFAULT_EMPLOYEE_PERMISSIONS
                        employee.permissions = DEFAULT_EMPLOYEE_PERMISSIONS.copy()
                        employee.save(update_fields=['permissions'])
                    
                    if not employee.has_permission('chat'):
                        return Response({'error': 'You do not have permission to chat'}, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get conversation - use filter for ManyToMany field
            conversation = Conversation.objects.filter(
                conversation_id=conversation_id,
                saraf_participants__in=[saraf_account],
                is_active=True
            ).distinct().first()
            
            if not conversation:
                return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if conversation is visible to user (not deleted by them)
            if not conversation.is_visible_to_user(saraf_account):
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
                recipient_saraf=saraf_account,
                delivery_status__in=['sent', 'delivered']
            ).update(
                delivery_status='read',
                read_at=timezone.now()
            )
            
            conversation_serializer = ConversationSerializer(conversation, context={'request': request})
            
            # Serialize messages individually to catch errors
            try:
                messages_serializer = MessageSerializer(page_obj.object_list, many=True, context={'request': request})
                messages_data = messages_serializer.data
            except Exception as msg_error:
                logger.error(f"Error serializing messages: {str(msg_error)}")
                messages_data = []
            
            return Response({
                'conversation': conversation_serializer.data,
                'messages': messages_data,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }, status=status.HTTP_200_OK)
            
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in ConversationDetailView: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteConversationView(APIView):
    """Delete conversation for current user (soft delete)"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, conversation_id):
        try:
            # Get user info from token
            user_info = get_user_info_from_token(request)
            saraf_id = user_info.get('saraf_id')
            
            if not saraf_id:
                return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get SarafAccount
            try:
                saraf_account = SarafAccount.objects.get(saraf_id=saraf_id, is_active=True)
            except SarafAccount.DoesNotExist:
                return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check employee permission if employee_id is provided
            employee_id = user_info.get('employee_id')
            if employee_id:
                try:
                    employee = SarafEmployee.objects.get(employee_id=employee_id, saraf_account=saraf_account, is_active=True)
                    if not employee.has_permission('chat'):
                        return Response({'error': 'You do not have permission to chat'}, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get conversation
            conversation = Conversation.objects.filter(
                conversation_id=conversation_id,
                saraf_participants__in=[saraf_account],
                is_active=True
            ).distinct().first()
            
            if not conversation:
                return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Soft delete conversation for this user
            conversation.delete_for_user(saraf_account)
            
            return Response({
                'message': 'Conversation deleted successfully',
                'conversation_id': conversation_id
            })
            
        except Exception as e:
            logger.error(f"Error in DeleteConversationView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SendMessageView(APIView):
    """
    Send a message to a conversation
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        try:
            # Get user info from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({'error': 'Invalid user token - no saraf_id found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = SarafAccount.objects.get(saraf_id=saraf_id)
            
            # Check chat permission for employees
            employee = None
            if user_info.get('user_type') == 'employee' and user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('chat'):
                        return Response({'error': 'You do not have permission to chat'}, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = SendMessageSerializer(data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    # Get conversation
                    conversation_id = serializer.validated_data['conversation_id']
                    conversation = Conversation.objects.get(conversation_id=conversation_id)
                    
                    # Verify user is participant
                    if saraf_account not in conversation.saraf_participants.all():
                        return Response({'error': 'You are not a participant in this conversation'}, status=status.HTTP_403_FORBIDDEN)
                    
                    # Create message
                    message_data = {
                        'conversation': conversation,
                        'sender_saraf': saraf_account,
                        'content': serializer.validated_data['content'],
                        'message_type': serializer.validated_data['message_type'],
                        'attachment': serializer.validated_data.get('attachment')
                    }
                    
                    # Add employee if this is an employee login
                    if user_info.get('user_type') == 'employee' and user_info.get('employee_id'):
                        try:
                            employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'], saraf_account=saraf_account)
                            message_data['sender_employee'] = employee
                        except SarafEmployee.DoesNotExist:
                            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
                    
                    # Also check if employee_id is provided in request (for backward compatibility)
                    employee_id = serializer.validated_data.get('employee_id')
                    if employee_id and not message_data.get('sender_employee'):
                        try:
                            employee = SarafEmployee.objects.get(employee_id=employee_id, saraf_account=saraf_account)
                            message_data['sender_employee'] = employee
                        except SarafEmployee.DoesNotExist:
                            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
                    
                    message = Message.objects.create(**message_data)
                    
                    # Create delivery records for all saraf participants except sender
                    recipients = conversation.saraf_participants.exclude(saraf_id=saraf_id)
                    deliveries = []
                    for recipient in recipients:
                        deliveries.append(MessageDelivery(
                            message=message,
                            recipient_saraf=recipient,
                            delivery_status='sent'
                        ))
                    
                    # Also create delivery records for normal user participants
                    normal_recipients = conversation.normal_user_participants.all()
                    for recipient in normal_recipients:
                        deliveries.append(MessageDelivery(
                            message=message,
                            recipient_normal_user=recipient,
                            delivery_status='sent'
                        ))
                    
                    MessageDelivery.objects.bulk_create(deliveries)
                    
                    # Update conversation timestamp
                    conversation.updated_at = timezone.now()
                    conversation.save(update_fields=['updated_at'])
                    
                    # Create in-app notifications for recipients
                    self.create_in_app_notifications(message, recipients)
                    
                    # Log the action
                    employee = message_data.get('sender_employee')
                    ActionLog.objects.create(
                        saraf=saraf_account,
                        user_type='employee' if employee else 'saraf',
                        user_id=employee.employee_id if employee else saraf_id,
                        user_name=employee.full_name if employee else saraf_account.full_name,
                        action_type='send_message',
                        description=f'Sent message {message.message_id} in conversation {conversation_id}' + (f' (by employee: {employee.full_name})' if employee else ''),
                        ip_address=self.get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        metadata={
                            'message_id': message.message_id,
                            'conversation_id': conversation_id,
                            'message_type': message.message_type,
                            'recipient_count': len(recipients)
                        }
                    )
                
                response_serializer = MessageSerializer(message)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in SendMessageView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create_in_app_notifications(self, message, recipients):
        """Create simple in-app notifications for recipients"""
        notifications = []
        for recipient in recipients:
            # Check if it's a SarafAccount or NormalUser
            if hasattr(recipient, 'saraf_id'):
                notifications.append(MessageNotification(
                    message=message,
                    recipient_saraf=recipient,
                    is_read=False
                ))
            elif hasattr(recipient, 'user_id'):
                notifications.append(MessageNotification(
                    message=message,
                    recipient_normal_user=recipient,
                    is_read=False
                ))
        MessageNotification.objects.bulk_create(notifications)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class MessageStatusView(APIView):
    """
    Update message delivery status
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, message_id):
        try:
            # Get saraf account from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({'error': 'Invalid user token - no saraf_id found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            if not saraf_id:
                return Response({'error': 'Invalid user token - no saraf_id found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_account = SarafAccount.objects.get(saraf_id=saraf_id)
            
            # Get message delivery record
            try:
                delivery = MessageDelivery.objects.get(
                    message_id=message_id,
                    recipient_saraf=saraf_account
                )
            except MessageDelivery.DoesNotExist:
                # Check if the user is the sender of the message
                try:
                    message = Message.objects.get(message_id=message_id, sender_saraf=saraf_account)
                    # User is the sender, they can't update delivery status for their own messages
                    return Response({'error': 'You cannot update delivery status for messages you sent'}, status=status.HTTP_400_BAD_REQUEST)
                except Message.DoesNotExist:
                    return Response({'error': 'Message not found or you are not authorized to update its status'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = MessageStatusSerializer(delivery, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Status updated successfully'}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in MessageStatusView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MessageSearchView(APIView):
    """
    Search messages across conversations
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get saraf account from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({'error': 'Invalid user token - no saraf_id found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = SarafAccount.objects.get(saraf_id=saraf_id)
            
            # Check chat permission for employees
            if user_info.get('user_type') == 'employee' and user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('chat'):
                        return Response({'error': 'You do not have permission to chat'}, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
            
            query = request.GET.get('q', '').strip()
            if not query:
                return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Search messages in user's conversations
            messages = Message.objects.filter(
                conversation__saraf_participants__in=[saraf_account],
                content__icontains=query
            ).order_by('-created_at')
            
            # Pagination
            page = request.GET.get('page', 1)
            page_size = request.GET.get('page_size', 20)
            paginator = Paginator(messages, page_size)
            page_obj = paginator.get_page(page)
            
            serializer = MessageSerializer(page_obj.object_list, many=True)
            
            return Response({
                'messages': serializer.data,
                'query': query,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            }, status=status.HTTP_200_OK)
            
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in MessageSearchView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MessageStatsView(APIView):
    """
    Get messaging statistics for the user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get saraf account from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({'error': 'Invalid user token - no saraf_id found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = SarafAccount.objects.get(saraf_id=saraf_id)
            
            # Check chat permission for employees
            if user_info.get('user_type') == 'employee' and user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('chat'):
                        return Response({'error': 'You do not have permission to chat'}, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get statistics
            total_conversations = Conversation.objects.filter(saraf_participants__in=[saraf_account], is_active=True).count()
            total_messages_sent = Message.objects.filter(sender_saraf=saraf_account).count()
            unread_messages = MessageDelivery.objects.filter(
                recipient_saraf=saraf_account,
                delivery_status__in=['sent', 'delivered']
            ).count()
            
            # Messages by type
            messages_by_type = Message.objects.filter(sender_saraf=saraf_account).values('message_type').annotate(count=Count('message_id'))
            
            # Recent activity
            recent_messages = Message.objects.filter(
                conversation__saraf_participants__in=[saraf_account]
            ).order_by('-created_at')[:5]
            
            recent_serializer = MessageSerializer(recent_messages, many=True)
            
            return Response({
                'total_conversations': total_conversations,
                'total_messages_sent': total_messages_sent,
                'unread_messages': unread_messages,
                'messages_by_type': list(messages_by_type),
                'recent_messages': recent_serializer.data
            }, status=status.HTTP_200_OK)
            
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in MessageStatsView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InAppNotificationsView(APIView):
    """
    Get in-app notifications for the authenticated user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get saraf account from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({'error': 'Invalid user token - no saraf_id found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = SarafAccount.objects.get(saraf_id=saraf_id)
            
            # Check chat permission for employees
            if user_info.get('user_type') == 'employee' and user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('chat'):
                        return Response({'error': 'You do not have permission to chat'}, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get unread notifications
            notifications = MessageNotification.objects.filter(
                recipient_saraf=saraf_account,
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
            
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in InAppNotificationsView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, notification_id=None):
        """Mark notification as read"""
        try:
            # Get user info from JWT token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({'error': 'Invalid user token - no saraf_id found'}, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = SarafAccount.objects.get(saraf_id=saraf_id)
            
            if notification_id:
                # Mark specific notification as read
                try:
                    notification = MessageNotification.objects.get(
                        notification_id=notification_id,
                        recipient_saraf=saraf_account
                    )
                    notification.is_read = True
                    notification.save()
                    return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
                except MessageNotification.DoesNotExist:
                    return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Mark all notifications as read
                MessageNotification.objects.filter(
                    recipient_saraf=saraf_account,
                    is_read=False
                ).update(is_read=True)
                return Response({'message': 'All notifications marked as read'}, status=status.HTTP_200_OK)
            
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in InAppNotificationsView: {str(e)}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
