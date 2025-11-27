from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import HawalaTransaction, HawalaReceipt
from .serializers import (
    HawalaTransactionSerializer,
    HawalaReceiveSerializer,
    HawalaExternalReceiveSerializer,
    HawalaListSerializer,
    HawalaStatusUpdateSerializer,
    HawalaReceiptSerializer,
    HawalaReceiptPublicSerializer
)
from saraf_account.models import SarafAccount, SarafEmployee
from saraf_account.authentication import SarafJWTAuthentication
from currency.models import SarafSupportedCurrency
from currency.models import Currency


class SendHawalaView(APIView):
    """
    API view for sending hawala transactions (Mode 1 & 2.1)
    Supports both internal and external transactions
    """
    authentication_classes = [SarafJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a new hawala transaction"""
        try:
            # Get the authenticated user (saraf or employee)
            authenticated_user = request.user
            
            # Get saraf account and employee from database based on token data
            if authenticated_user.user_type == 'employee':
                employee = SarafEmployee.objects.select_related('saraf_account').get(
                    employee_id=authenticated_user.employee_id,
                    is_active=True
                )
                saraf_account = employee.saraf_account
            else:
                saraf_account = SarafAccount.objects.get(
                    saraf_id=authenticated_user.saraf_id,
                    is_active=True
                )
                employee = None
            
            # Check if user has permission to send transfers
            if employee and not employee.has_permission('send_transfer'):
                return Response({
                    'error': 'Permission denied. You do not have permission to send transfers.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Add context for serializer with employee info
            serializer = HawalaTransactionSerializer(
                data=request.data,
                context={'employee': employee, 'saraf_account': saraf_account}
            )
            
            if serializer.is_valid():
                hawala = serializer.save()
                
                # Mark as sent if it's an internal transaction
                if hawala.is_internal_transaction():
                    hawala.mark_as_sent()
                
                # Update saraf balance - sending hawala increases balance
                self._update_saraf_balance(saraf_account, hawala.currency, hawala.amount, 'deposit', 'hawala_send', employee)
                
                return Response({
                    'message': 'Hawala transaction created successfully',
                    'hawala': HawalaTransactionSerializer(hawala, context={'saraf_account': saraf_account}).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Failed to create hawala transaction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_saraf_balance(self, saraf_account, currency, amount, transaction_type, description, employee=None):
        """Helper method to update saraf balance"""
        from django.db import transaction as db_transaction
        from decimal import Decimal
        
        try:
            from saraf_balance.models import SarafBalance
            from transaction.models import Transaction
            
            with db_transaction.atomic():
                # Get or create balance record
                balance, created = SarafBalance.get_or_create_balance(
                    saraf_account,
                    currency
                )
                
                # Determine performer information
                if employee:
                    performer_user_id = employee.employee_id
                    performer_user_type = 'employee'
                    performer_full_name = employee.full_name
                    performer_employee_id = employee.employee_id
                    performer_employee_name = employee.full_name
                else:
                    performer_user_id = saraf_account.saraf_id
                    performer_user_type = 'saraf'
                    performer_full_name = saraf_account.full_name
                    performer_employee_id = None
                    performer_employee_name = None
                
                # Create transaction - Transaction.save() will update the balance and calculate balance_before/balance_after
                # We provide placeholder values for required fields; save() will recalculate them correctly
                transaction = Transaction(
                    saraf_account=saraf_account,
                    currency=currency,
                    transaction_type=transaction_type,  # 'deposit' or 'withdrawal'
                    amount=amount,
                    performer_user_id=performer_user_id,
                    performer_user_type=performer_user_type,
                    performer_full_name=performer_full_name,
                    performer_employee_id=performer_employee_id,
                    performer_employee_name=performer_employee_name,
                    description=f"Hawala transaction: {description}",
                    balance_before=Decimal('0.00'),  # Placeholder, will be recalculated in save()
                    balance_after=Decimal('0.00')  # Placeholder, will be recalculated in save()
                )
                transaction.save()  # This will update the balance and set correct balance_before/balance_after
                
        except Exception as e:
            # Log error and re-raise to ensure transaction rollback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to update saraf balance: {str(e)}")
            raise


class ReceiveHawalaListView(APIView):
    """
    API view for listing hawala transactions that can be received
    Shows transactions where the current saraf is the destination
    """
    authentication_classes = [SarafJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get list of hawala transactions to receive"""
        try:
            # Get the authenticated user (saraf or employee)
            authenticated_user = request.user
            
            # Get saraf account and employee from database based on token data
            if authenticated_user.user_type == 'employee':
                employee = SarafEmployee.objects.select_related('saraf_account').get(
                    employee_id=authenticated_user.employee_id,
                    is_active=True
                )
                saraf_account = employee.saraf_account
            else:
                saraf_account = SarafAccount.objects.get(
                    saraf_id=authenticated_user.saraf_id,
                    is_active=True
                )
                employee = None
            
            # Check if user has permission to receive transfers
            if employee and not employee.has_permission('receive_transfer'):
                return Response({
                    'error': 'Permission denied. You do not have permission to receive transfers.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get saraf ID
            saraf_id = saraf_account.saraf_id
            
            # Query hawala transactions where this saraf is the destination
            # Include both normal received hawalas and external receive hawalas
            # Show both pending and sent status (sent is when sender marked it as sent internally)
            hawalas = HawalaTransaction.objects.filter(
                (
                    Q(destination_exchange_id=saraf_id) |
                    (Q(sender_exchange=saraf_id) & Q(mode='external_receiver'))
                ),
                status__in=['pending', 'sent']  # Show pending and sent hawalas
            ).order_by('-created_at')
            
            serializer = HawalaListSerializer(hawalas, many=True, context={'request': request})
            
            return Response({
                'message': 'Hawala transactions retrieved successfully',
                'hawalas': serializer.data,
                'count': hawalas.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve hawala transactions',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReceiveHawalaDetailView(APIView):
    """
    API view for receiving a specific hawala transaction (Mode 1)
    Updates transaction with receiver details
    """
    authentication_classes = [SarafJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, hawala_number):
        """Get hawala transaction details"""
        try:
            # Get the authenticated user (saraf or employee)
            authenticated_user = request.user
            
            # Get saraf account and employee from database based on token data
            if authenticated_user.user_type == 'employee':
                employee = SarafEmployee.objects.select_related('saraf_account').get(
                    employee_id=authenticated_user.employee_id,
                    is_active=True
                )
                saraf_account = employee.saraf_account
            else:
                saraf_account = SarafAccount.objects.get(
                    saraf_id=authenticated_user.saraf_id,
                    is_active=True
                )
                employee = None
            
            # Get saraf ID
            saraf_id = saraf_account.saraf_id
            
            # Get hawala transaction
            hawala = get_object_or_404(
                HawalaTransaction,
                hawala_number=hawala_number
            )
            
            # Validate exchange_id and hawala_number combination
            if hawala.destination_exchange_id != saraf_id:
                return Response({
                    'error': 'Access denied. This hawala transaction does not belong to your exchange.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = HawalaTransactionSerializer(hawala, context={'saraf_account': saraf_account})
            
            return Response({
                'message': 'Hawala transaction retrieved successfully',
                'hawala': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve hawala transaction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, hawala_number):
        """Update hawala transaction with receiver details"""
        try:
            # Get the authenticated user (saraf or employee)
            authenticated_user = request.user
            
            # Get saraf account and employee from database based on token data
            if authenticated_user.user_type == 'employee':
                employee = SarafEmployee.objects.select_related('saraf_account').get(
                    employee_id=authenticated_user.employee_id,
                    is_active=True
                )
                saraf_account = employee.saraf_account
            else:
                saraf_account = SarafAccount.objects.get(
                    saraf_id=authenticated_user.saraf_id,
                    is_active=True
                )
                employee = None
            
            # Check if user has permission to receive transfers
            if employee and not employee.has_permission('receive_transfer'):
                return Response({
                    'error': 'Permission denied. You do not have permission to receive transfers.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get saraf ID
            saraf_id = saraf_account.saraf_id
            
            # Get hawala transaction
            hawala = get_object_or_404(
                HawalaTransaction,
                hawala_number=hawala_number
            )
            
            # Validate exchange_id and hawala_number combination
            if hawala.destination_exchange_id != saraf_id:
                return Response({
                    'error': 'Access denied. This hawala transaction does not belong to your exchange.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Validate that transaction can be received
            if not hawala.can_be_received():
                return Response({
                    'error': 'This transaction cannot be received in its current status'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = HawalaReceiveSerializer(hawala, data=request.data, partial=True)
            
            if serializer.is_valid():
                # Update transaction with receiver details
                hawala.mark_as_received(
                    receiver_phone=serializer.validated_data.get('receiver_phone'),
                    receiver_photo=serializer.validated_data.get('receiver_photo'),
                    employee=employee
                )
                
                # Update notes if provided
                if 'notes' in serializer.validated_data:
                    hawala.notes = serializer.validated_data['notes']
                    hawala.save(update_fields=['notes'])
                
                # Update saraf balance - receiving hawala decreases balance
                self._update_saraf_balance(saraf_account, hawala.currency, hawala.amount, 'withdrawal', 'hawala_receive', employee)
                
                return Response({
                    'message': 'Hawala transaction received successfully',
                    'hawala': HawalaTransactionSerializer(hawala, context={'saraf_account': saraf_account}).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Failed to receive hawala transaction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_saraf_balance(self, saraf_account, currency, amount, transaction_type, description, employee=None):
        """Helper method to update saraf balance"""
        from django.db import transaction as db_transaction
        from decimal import Decimal
        
        try:
            from saraf_balance.models import SarafBalance
            from transaction.models import Transaction
            
            with db_transaction.atomic():
                # Get or create balance record
                balance, created = SarafBalance.get_or_create_balance(
                    saraf_account,
                    currency
                )
                
                # Determine performer information
                if employee:
                    performer_user_id = employee.employee_id
                    performer_user_type = 'employee'
                    performer_full_name = employee.full_name
                    performer_employee_id = employee.employee_id
                    performer_employee_name = employee.full_name
                else:
                    performer_user_id = saraf_account.saraf_id
                    performer_user_type = 'saraf'
                    performer_full_name = saraf_account.full_name
                    performer_employee_id = None
                    performer_employee_name = None
                
                # Create transaction - Transaction.save() will update the balance and calculate balance_before/balance_after
                # We provide placeholder values for required fields; save() will recalculate them correctly
                transaction = Transaction(
                    saraf_account=saraf_account,
                    currency=currency,
                    transaction_type=transaction_type,  # 'deposit' or 'withdrawal'
                    amount=amount,
                    performer_user_id=performer_user_id,
                    performer_user_type=performer_user_type,
                    performer_full_name=performer_full_name,
                    performer_employee_id=performer_employee_id,
                    performer_employee_name=performer_employee_name,
                    description=f"Hawala transaction: {description}",
                    balance_before=Decimal('0.00'),  # Placeholder, will be recalculated in save()
                    balance_after=Decimal('0.00')  # Placeholder, will be recalculated in save()
                )
                transaction.save()  # This will update the balance and set correct balance_before/balance_after
                
        except Exception as e:
            # Log error and re-raise to ensure transaction rollback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to update saraf balance: {str(e)}")
            raise


class ExternalReceiveHawalaView(APIView):
    """
    API view for external hawala transactions (Mode 2.2)
    Used when only the receiving saraf uses the app
    """
    authentication_classes = [SarafJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create external hawala transaction"""
        try:
            # Get the authenticated user (saraf or employee)
            authenticated_user = request.user
            
            # Get saraf account and employee from database based on token data
            if authenticated_user.user_type == 'employee':
                employee = SarafEmployee.objects.select_related('saraf_account').get(
                    employee_id=authenticated_user.employee_id,
                    is_active=True
                )
                saraf_account = employee.saraf_account
            else:
                saraf_account = SarafAccount.objects.get(
                    saraf_id=authenticated_user.saraf_id,
                    is_active=True
                )
                employee = None
            
            # Check if user has permission to receive transfers
            if employee and not employee.has_permission('receive_transfer'):
                return Response({
                    'error': 'Permission denied. You do not have permission to receive transfers.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Add receiver exchange ID to request data
            request_data = request.data.copy()
            request_data['receiver_exchange_id'] = saraf_account.saraf_id
            
            serializer = HawalaExternalReceiveSerializer(
                data=request_data,
                context={'employee': employee, 'saraf_account': saraf_account}
            )
            
            if serializer.is_valid():
                hawala = serializer.save()
                
                return Response({
                    'message': 'External hawala transaction created successfully',
                    'hawala': HawalaTransactionSerializer(hawala, context={'saraf_account': saraf_account}).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Failed to create external hawala transaction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HawalaHistoryView(APIView):
    """
    API view for retrieving hawala transaction history
    Shows both sent and received transactions
    """
    authentication_classes = [SarafJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get hawala transaction history"""
        try:
            # Get the authenticated user (saraf or employee)
            authenticated_user = request.user
            
            # Get saraf account and employee from database based on token data
            if authenticated_user.user_type == 'employee':
                employee = SarafEmployee.objects.select_related('saraf_account').get(
                    employee_id=authenticated_user.employee_id,
                    is_active=True
                )
                saraf_account = employee.saraf_account
            else:
                saraf_account = SarafAccount.objects.get(
                    saraf_id=authenticated_user.saraf_id,
                    is_active=True
                )
                employee = None
            
            # Get saraf ID
            saraf_id = saraf_account.saraf_id
            
            # Query parameters
            transaction_type = request.query_params.get('type', 'all')  # 'sent', 'received', 'all'
            status_filter = request.query_params.get('status', 'all')  # 'pending', 'completed', 'all'
            time_range = request.query_params.get('time_range', 'all')  # 'today', 'week', 'month', 'all'
            
            # Performer filters
            performer = request.query_params.get('performer', '')  # Filter by performer name (case-insensitive search)
            performer_id = request.query_params.get('performer_id', '')  # Filter by performer employee ID
            performer_type = request.query_params.get('performer_type', '')  # Filter by performer type (saraf/employee)
            employee_id = request.query_params.get('employee_id', '')  # Filter by employee ID
            
            limit = int(request.query_params.get('limit', 50))
            offset = int(request.query_params.get('offset', 0))
            
            # Build query
            query = Q()
            
            if transaction_type == 'sent':
                query &= Q(sender_exchange=saraf_id)
            elif transaction_type == 'received':
                # Include both:
                # 1. Normal received hawalas (destination_exchange_id matches)
                # 2. External receive hawalas (sender_exchange matches with mode='external_receiver')
                query &= (
                    Q(destination_exchange_id=saraf_id) |
                    (Q(sender_exchange=saraf_id) & Q(mode='external_receiver'))
                )
            else:  # 'all'
                query &= (Q(sender_exchange=saraf_id) | Q(destination_exchange_id=saraf_id))
            
            if status_filter != 'all':
                query &= Q(status=status_filter)
            
            # Apply performer filters
            if performer:
                # Filter by performer name (case-insensitive search)
                # For sent hawalas: created_by_employee
                # For received hawalas: received_by_employee
                query &= (
                    Q(created_by_employee__full_name__icontains=performer) |
                    Q(received_by_employee__full_name__icontains=performer)
                )
            
            if performer_id:
                try:
                    performer_id_int = int(performer_id)
                    query &= (
                        Q(created_by_employee__employee_id=performer_id_int) |
                        Q(received_by_employee__employee_id=performer_id_int)
                    )
                except ValueError:
                    pass  # Ignore invalid performer_id
            
            if performer_type and performer_type in ['saraf', 'employee']:
                if performer_type == 'saraf':
                    # Filter for hawalas performed by saraf (no employee)
                    query &= Q(created_by_employee__isnull=True) & Q(received_by_employee__isnull=True)
                elif performer_type == 'employee':
                    # Filter for hawalas performed by employee
                    query &= (
                        Q(created_by_employee__isnull=False) |
                        Q(received_by_employee__isnull=False)
                    )
            
            if employee_id:
                try:
                    employee_id_int = int(employee_id)
                    query &= (
                        Q(created_by_employee__employee_id=employee_id_int) |
                        Q(received_by_employee__employee_id=employee_id_int)
                    )
                except ValueError:
                    pass  # Ignore invalid employee_id
            
            # Apply time range filter
            if time_range != 'all':
                from datetime import datetime, timedelta
                now = datetime.now()
                
                if time_range == 'today':
                    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                elif time_range == 'week':
                    start_date = now - timedelta(days=7)
                elif time_range == 'month':
                    start_date = now - timedelta(days=30)
                else:
                    start_date = None
                
                if start_date:
                    query &= Q(created_at__gte=start_date)
            
            # Execute query
            hawalas = HawalaTransaction.objects.filter(query).order_by('-created_at')[offset:offset+limit]
            total_count = HawalaTransaction.objects.filter(query).count()
            
            serializer = HawalaListSerializer(hawalas, many=True, context={'request': request})
            
            # Build filters_applied dictionary
            filters_applied = {
                'type': transaction_type,
                'status': status_filter,
                'time_range': time_range,
            }
            if performer:
                filters_applied['performer'] = performer
            if performer_id:
                filters_applied['performer_id'] = performer_id
            if performer_type:
                filters_applied['performer_type'] = performer_type
            if employee_id:
                filters_applied['employee_id'] = employee_id
            
            return Response({
                'message': 'Hawala transaction history retrieved successfully',
                'hawalas': serializer.data,
                'count': len(serializer.data),
                'total_count': total_count,
                'offset': offset,
                'limit': limit,
                'filters_applied': filters_applied
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve hawala transaction history',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HawalaStatusUpdateView(APIView):
    """
    API view for updating hawala transaction status
    """
    authentication_classes = [SarafJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request, hawala_number):
        """Update hawala transaction status"""
        try:
            # Get the authenticated user (saraf or employee)
            authenticated_user = request.user
            
            # Get saraf account and employee from database based on token data
            if authenticated_user.user_type == 'employee':
                employee = SarafEmployee.objects.select_related('saraf_account').get(
                    employee_id=authenticated_user.employee_id,
                    is_active=True
                )
                saraf_account = employee.saraf_account
            else:
                saraf_account = SarafAccount.objects.get(
                    saraf_id=authenticated_user.saraf_id,
                    is_active=True
                )
                employee = None
            
            # Get saraf ID
            saraf_id = saraf_account.saraf_id
            
            # Get hawala transaction
            hawala = get_object_or_404(
                HawalaTransaction,
                hawala_number=hawala_number
            )
            
            # Verify access - check if saraf owns this hawala
            if hawala.sender_exchange.saraf_id != saraf_id and hawala.destination_exchange_id != saraf_id:
                return Response({
                    'error': 'Access denied. You can only access your own hawala transactions.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = HawalaStatusUpdateSerializer(hawala, data=request.data, partial=True)
            
            if serializer.is_valid():
                # Update status
                new_status = serializer.validated_data.get('status')
                if new_status:
                    if new_status == 'completed':
                        hawala.mark_as_completed(employee)
                    else:
                        hawala.status = new_status
                        hawala.save(update_fields=['status'])
                
                # Update notes if provided
                if 'notes' in serializer.validated_data:
                    hawala.notes = serializer.validated_data['notes']
                    hawala.save(update_fields=['notes'])
                
                return Response({
                    'message': 'Hawala transaction status updated successfully',
                    'hawala': HawalaTransactionSerializer(hawala, context={'saraf_account': saraf_account}).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Failed to update hawala transaction status',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListAllHawalasView(APIView):
    """
    API view for listing all hawalas belonging to a specific saraf
    Supports filtering by employee and time range
    """
    authentication_classes = [SarafJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all hawalas for the authenticated saraf with optional filters"""
        try:
            # Get the authenticated user (saraf or employee)
            authenticated_user = request.user
            
            # Get saraf account and employee from database based on token data
            if authenticated_user.user_type == 'employee':
                employee = SarafEmployee.objects.select_related('saraf_account').get(
                    employee_id=authenticated_user.employee_id,
                    is_active=True
                )
                saraf_account = employee.saraf_account
            else:
                saraf_account = SarafAccount.objects.get(
                    saraf_id=authenticated_user.saraf_id,
                    is_active=True
                )
                employee = None
            
            # Get saraf ID
            saraf_id = saraf_account.saraf_id
            
            # Get query parameters
            employee_filter = request.query_params.get('employee', 'all')
            time_range = request.query_params.get('time_range', 'all')
            status_filter = request.query_params.get('status', 'all')  # 'pending', 'completed', 'all'
            limit = int(request.query_params.get('limit', 50))
            offset = int(request.query_params.get('offset', 0))
            
            # Build base query - only hawalas belonging to this saraf
            query = Q(sender_exchange=saraf_id) | Q(destination_exchange_id=saraf_id)
            
            # Apply employee filter
            if employee_filter != 'all':
                if employee_filter == 'EN2':
                    # Filter by specific employee names or patterns
                    query &= Q(created_by_employee__full_name__icontains=employee_filter) | \
                             Q(received_by_employee__full_name__icontains=employee_filter)
                else:
                    # Filter by employee name
                    query &= Q(created_by_employee__full_name__icontains=employee_filter) | \
                             Q(received_by_employee__full_name__icontains=employee_filter)
            
            # Apply time range filter
            if time_range != 'all':
                from datetime import datetime, timedelta
                now = datetime.now()
                
                if time_range == 'today':
                    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                elif time_range == 'week':
                    start_date = now - timedelta(days=7)
                elif time_range == 'month':
                    start_date = now - timedelta(days=30)
                else:
                    start_date = None
                
                if start_date:
                    query &= Q(created_at__gte=start_date)
            
            # Apply status filter
            if status_filter != 'all':
                query &= Q(status=status_filter)
            
            # Execute query
            hawalas = HawalaTransaction.objects.filter(query).order_by('-created_at')[offset:offset+limit]
            total_count = HawalaTransaction.objects.filter(query).count()
            
            serializer = HawalaListSerializer(hawalas, many=True, context={'request': request})
            
            return Response({
                'message': 'All hawalas retrieved successfully',
                'hawalas': serializer.data,
                'count': len(serializer.data),
                'total_count': total_count,
                'offset': offset,
                'limit': limit,
                'filters': {
                    'employee': employee_filter,
                    'time_range': time_range
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve hawalas',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def hawala_statistics(request):
    """
    API endpoint for hawala transaction statistics
    """
    try:
        # Get the authenticated user (saraf or employee)
        authenticated_user = request.user
        
        # Get saraf account and employee from database based on token data
        if authenticated_user.user_type == 'employee':
            employee = SarafEmployee.objects.select_related('saraf_account').get(
                employee_id=authenticated_user.employee_id,
                is_active=True
            )
            saraf_account = employee.saraf_account
        else:
            saraf_account = SarafAccount.objects.get(
                saraf_id=authenticated_user.saraf_id,
                is_active=True
            )
            employee = None
        
        # Get saraf ID
        saraf_id = saraf_account.saraf_id
        
        # Calculate statistics
        sent_hawalas = HawalaTransaction.objects.filter(sender_exchange=saraf_id)
        # Include both normal received hawalas and external receive hawalas
        received_hawalas = HawalaTransaction.objects.filter(
            Q(destination_exchange_id=saraf_id) |
            (Q(sender_exchange=saraf_id) & Q(mode='external_receiver'))
        )
        
        stats = {
            'total_sent': sent_hawalas.count(),
            'total_received': received_hawalas.count(),
            'pending_sent': sent_hawalas.filter(status='pending').count(),
            'pending_received': received_hawalas.filter(status='pending').count(),
            'completed_sent': sent_hawalas.filter(status='completed').count(),
            'completed_received': received_hawalas.filter(status='completed').count(),
            'total_amount_sent': sum(h.amount for h in sent_hawalas.filter(status='completed')),
            'total_amount_received': sum(h.amount for h in received_hawalas.filter(status='completed')),
            'total_fees_collected': sum(h.transfer_fee for h in sent_hawalas.filter(status='completed')),
        }
        
        return Response({
            'message': 'Hawala statistics retrieved successfully',
            'statistics': stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Failed to retrieve hawala statistics',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HawalaReceiptView(APIView):
    """
    API view for retrieving hawala receipts
    """
    authentication_classes = [SarafJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, hawala_number):
        """Get receipt for a completed hawala transaction"""
        try:
            # Get the authenticated user (saraf or employee)
            authenticated_user = request.user
            
            # Get saraf account and employee from database based on token data
            if authenticated_user.user_type == 'employee':
                employee = SarafEmployee.objects.select_related('saraf_account').get(
                    employee_id=authenticated_user.employee_id,
                    is_active=True
                )
                saraf_account = employee.saraf_account
            else:
                saraf_account = SarafAccount.objects.get(
                    saraf_id=authenticated_user.saraf_id,
                    is_active=True
                )
                employee = None
            
            # Get saraf ID
            saraf_id = saraf_account.saraf_id
            
            # Get hawala transaction
            hawala = get_object_or_404(
                HawalaTransaction,
                hawala_number=hawala_number
            )
            
            # Verify access - check if saraf owns this hawala
            if hawala.sender_exchange.saraf_id != saraf_id and hawala.destination_exchange_id != saraf_id:
                return Response({
                    'error': 'Access denied. You can only access receipts for your own hawala transactions.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check if transaction is completed
            if hawala.status != 'completed':
                return Response({
                    'error': 'Receipt can only be generated for completed transactions.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create receipt
            try:
                receipt = hawala.receipt
            except HawalaReceipt.DoesNotExist:
                # Generate receipt if it doesn't exist
                receipt = hawala.generate_receipt(employee)
            
            # Use public serializer for customer-facing receipt
            serializer = HawalaReceiptPublicSerializer(receipt)
            
            return Response({
                'message': 'Receipt retrieved successfully',
                'receipt': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to retrieve receipt',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateReceiptView(APIView):
    """
    API view for manually generating receipts for completed transactions
    """
    authentication_classes = [SarafJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, hawala_number):
        """Generate receipt for a completed hawala transaction"""
        try:
            # Get the authenticated user (saraf or employee)
            authenticated_user = request.user
            
            # Get saraf account and employee from database based on token data
            if authenticated_user.user_type == 'employee':
                employee = SarafEmployee.objects.select_related('saraf_account').get(
                    employee_id=authenticated_user.employee_id,
                    is_active=True
                )
                saraf_account = employee.saraf_account
            else:
                saraf_account = SarafAccount.objects.get(
                    saraf_id=authenticated_user.saraf_id,
                    is_active=True
                )
                employee = None
            
            # Get saraf ID
            saraf_id = saraf_account.saraf_id
            
            # Get hawala transaction
            hawala = get_object_or_404(
                HawalaTransaction,
                hawala_number=hawala_number
            )
            
            # Verify access - check if saraf owns this hawala
            if hawala.sender_exchange.saraf_id != saraf_id and hawala.destination_exchange_id != saraf_id:
                return Response({
                    'error': 'Access denied. You can only generate receipts for your own hawala transactions.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check if transaction is completed
            if hawala.status != 'completed':
                return Response({
                    'error': 'Receipt can only be generated for completed transactions.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if receipt already exists
            if hasattr(hawala, 'receipt') and hawala.receipt:
                return Response({
                    'error': 'Receipt already exists for this transaction.',
                    'receipt_id': str(hawala.receipt.receipt_id)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate receipt
            receipt = hawala.generate_receipt(employee)
            
            # Use public serializer for customer-facing receipt
            serializer = HawalaReceiptPublicSerializer(receipt)
            
            return Response({
                'message': 'Receipt generated successfully',
                'receipt': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': 'Failed to generate receipt',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SupportedCurrenciesView(APIView):
    """
    Get currencies supported by the authenticated saraf
    """
    authentication_classes = [SarafJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get list of currencies supported by the saraf"""
        try:
            # Get saraf account from authenticated user
            authenticated_user = request.user
            saraf_account = None
            
            if authenticated_user.user_type == 'saraf':
                saraf_account = SarafAccount.objects.get(saraf_id=authenticated_user.saraf_id)
            elif authenticated_user.user_type == 'employee':
                employee = SarafEmployee.objects.get(employee_id=authenticated_user.employee_id)
                saraf_account = employee.saraf_account
            
            if not saraf_account:
                return Response({
                    'error': 'Saraf account not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get supported currencies
            supported_currencies = SarafSupportedCurrency.objects.filter(
                saraf_account=saraf_account,
                is_active=True
            ).select_related('currency')
            
            currencies_data = [
                {
                    'code': sc.currency.currency_code,
                    'name': sc.currency.currency_name,
                    'name_local': sc.currency.currency_name_local,
                    'symbol': sc.currency.symbol,
                    'added_at': sc.added_at
                }
                for sc in supported_currencies
            ]
            
            return Response({
                'message': 'Supported currencies retrieved successfully',
                'currencies': currencies_data,
                'count': len(currencies_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Failed to retrieve supported currencies: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NormalUserHawalaLookupView(APIView):
    """
    API view for normal users to lookup hawala transactions by receiver phone number
    """
    permission_classes = [AllowAny]  # Allow any user to lookup by phone
    
    def post(self, request):
        """Lookup hawala transaction by receiver phone number"""
        try:
            receiver_phone = request.data.get('receiver_phone')
            
            if not receiver_phone:
                return Response({
                    'error': 'Receiver phone number is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Clean phone number (remove spaces, dashes, etc.)
            import re
            receiver_phone = re.sub(r'[^\d+]', '', receiver_phone)
            
            # Look for hawala transactions with this receiver phone
            hawala_transactions = HawalaTransaction.objects.filter(
                receiver_phone=receiver_phone,
                status__in=['pending', 'completed']  # Only show pending and completed transactions
            ).order_by('-created_at')
            
            if not hawala_transactions.exists():
                return Response({
                    'message': 'No hawala transactions found for this phone number',
                    'transactions': []
                }, status=status.HTTP_200_OK)
            
            # Serialize transactions with limited information for normal users
            transactions_data = []
            for hawala in hawala_transactions:
                transaction_data = {
                    'hawala_number': hawala.hawala_number,
                    'amount': float(hawala.amount),
                    'currency': hawala.currency.currency_code,
                    'currency_name': hawala.currency.currency_name,
                    'sender_name': hawala.sender_name,
                    'receiver_name': hawala.receiver_name,
                    'receiver_phone': hawala.receiver_phone,
                    'status': hawala.status,
                    'mode': hawala.mode,
                    'sender_exchange_name': hawala.sender_exchange_name,
                    'destination_exchange_name': hawala.destination_exchange_name,
                    'created_at': hawala.created_at.isoformat() if hawala.created_at else None,
                    'completed_at': hawala.completed_at.isoformat() if hawala.completed_at else None,
                    'notes': hawala.notes,
                    'transfer_fee': float(hawala.transfer_fee) if hawala.transfer_fee else None,
                }
                transactions_data.append(transaction_data)
            
            return Response({
                'message': f'Found {len(transactions_data)} hawala transaction(s)',
                'transactions': transactions_data,
                'count': len(transactions_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to lookup hawala transactions',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
