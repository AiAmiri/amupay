from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, datetime
import logging

logger = logging.getLogger(__name__)

from .models import Transaction
from .serializers import (
    TransactionSerializer,
    CreateTransactionSerializer,
    TransactionListSerializer
)
from saraf_account.models import SarafAccount, SarafEmployee
from currency.models import Currency, SarafSupportedCurrency


def get_user_info_from_token(request):
    """Helper function to extract user info from JWT token"""
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Get the raw token string
        token_string = str(request.auth)
        
        # Create AccessToken object
        token = AccessToken(token_string)
        
        user_info = {
            'saraf_id': token.get('saraf_id'),
            'employee_id': token.get('employee_id'),
            'user_type': token.get('user_type'),
            'user_id': token.get('user_id'),
            'full_name': token.get('full_name'),
            'email_or_whatsapp_number': token.get('email_or_whatsapp_number'),
            'employee_name': token.get('employee_name')
        }
        
        return user_info
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error extracting user info from token: {str(e)}")
        return None


class CreateTransactionView(APIView):
    """Create new transaction (deposit or withdrawal)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create new transaction"""
        try:
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check permissions
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    transaction_type = request.data.get('transaction_type')
                    
                    if transaction_type == 'deposit':
                        if not employee.has_permission('deposit_to_account'):
                            return Response({
                                'error': 'You do not have permission to deposit to account'
                            }, status=status.HTTP_403_FORBIDDEN)
                    elif transaction_type == 'withdrawal':
                        if not employee.has_permission('withdraw_from_account'):
                            return Response({
                                'error': 'You do not have permission to withdraw from account'
                            }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee information not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Data validation
            serializer = CreateTransactionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid data sent',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # Check currency support
            currency = get_object_or_404(Currency, currency_code=validated_data['currency_code'])
            if not SarafSupportedCurrency.objects.filter(
                saraf_account=saraf_account,
                currency=currency,
                is_active=True
            ).exists():
                return Response({
                    'error': f'Currency {currency.currency_code} is not in your supported currencies list'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create transaction
            with transaction.atomic():
                new_transaction = Transaction.create_transaction(
                    saraf_account=saraf_account,
                    currency=currency,
                    transaction_type=validated_data['transaction_type'],
                    amount=validated_data['amount'],
                    description=validated_data.get('description', ''),
                    user_info=user_info
                )
            
            # Return transaction information
            response_serializer = TransactionSerializer(new_transaction)
            return Response({
                'message': 'Transaction successfully recorded',
                'transaction': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except ValidationError as ve:
            return Response({
                'error': 'Transaction validation failed',
                'details': str(ve)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'Error recording transaction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionListView(APIView):
    """Display list of exchange transactions"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of transactions"""
        try:
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check permissions
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('view_history'):
                        return Response({
                            'error': 'You do not have permission to view history'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee information not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Filters
            currency_code = request.query_params.get('currency')
            transaction_type = request.query_params.get('type')
            time_filter = request.query_params.get('time', 'all')  # all, day, week, month
            limit = request.query_params.get('limit', 50)
            
            try:
                limit = int(limit)
                if limit > 100:
                    limit = 100
            except:
                limit = 50
            
            # Get transactions
            transactions = Transaction.objects.filter(saraf_account=saraf_account)
            
            # Apply time filter
            now = timezone.now()
            if time_filter == 'day':
                # Last 24 hours
                start_time = now - timedelta(days=1)
                transactions = transactions.filter(created_at__gte=start_time)
            elif time_filter == 'week':
                # Last 7 days
                start_time = now - timedelta(days=7)
                transactions = transactions.filter(created_at__gte=start_time)
            elif time_filter == 'month':
                # Last 30 days
                start_time = now - timedelta(days=30)
                transactions = transactions.filter(created_at__gte=start_time)
            # 'all' means no time filter applied
            
            if currency_code:
                transactions = transactions.filter(currency__currency_code=currency_code)
            
            if transaction_type and transaction_type in ['deposit', 'withdrawal']:
                transactions = transactions.filter(transaction_type=transaction_type)
            
            # Order by most recent first
            transactions = transactions.order_by('-created_at')
            transactions = transactions[:limit]
            
            # Serialize
            serializer = TransactionListSerializer(transactions, many=True)
            
            # Calculate time filter info for response
            time_info = {
                'filter': time_filter,
                'description': {
                    'all': 'All transactions',
                    'day': 'Last 24 hours',
                    'week': 'Last 7 days', 
                    'month': 'Last 30 days'
                }.get(time_filter, 'All transactions')
            }
            
            return Response({
                'transactions': serializer.data,
                'count': len(serializer.data),
                'saraf_name': saraf_account.full_name,
                'time_filter': time_info,
                'filters_applied': {
                    'currency': currency_code,
                    'type': transaction_type,
                    'time': time_filter,
                    'limit': limit
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error getting transaction list',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionDetailView(APIView):
    """Display details of a transaction"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, transaction_id):
        """Get transaction details"""
        try:
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check permissions
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('view_history'):
                        return Response({
                            'error': 'You do not have permission to view history'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee information not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Get transaction
            transaction_obj = get_object_or_404(
                Transaction,
                transaction_id=transaction_id,
                saraf_account=saraf_account
            )
            
            serializer = TransactionSerializer(transaction_obj)
            return Response({
                'transaction': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error getting transaction details',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteTransactionView(APIView):
    """Delete transaction"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, transaction_id):
        """Delete transaction and update balance"""
        try:
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check permissions for transaction deletion
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('delete_transaction'):
                        return Response({
                            'error': 'You do not have permission to delete transactions'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee information not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Get transaction
            transaction_obj = get_object_or_404(
                Transaction,
                transaction_id=transaction_id,
                saraf_account=saraf_account
            )
            
            # Save information for balance restoration
            currency = transaction_obj.currency
            amount = transaction_obj.amount
            transaction_type = transaction_obj.transaction_type
            
            with transaction.atomic():
                # Restore balance
                from saraf_balance.models import SarafBalance
                balance = SarafBalance.objects.get(
                    saraf_account=saraf_account,
                    currency=currency
                )
                
                # Reverse transaction
                if transaction_type == 'deposit':
                    # Check if reversing deposit would create negative balance
                    if balance.balance < amount:
                        return Response({
                            'error': 'Cannot delete deposit transaction',
                            'details': f'Current balance ({balance.balance} {currency.currency_code}) '
                                     f'is less than deposit amount ({amount} {currency.currency_code}). '
                                     f'This would result in negative balance.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    balance.balance -= amount
                    balance.total_deposits -= amount
                elif transaction_type == 'withdrawal':
                    balance.balance += amount
                    balance.total_withdrawals -= amount
                
                balance.transaction_count -= 1
                balance.save()
                
                # Delete transaction
                transaction_obj.delete()
                
                # Log the action
                from saraf_account.models import ActionLog
                ActionLog.objects.create(
                    saraf=saraf_account,
                    user_type='employee' if user_info.get('employee_id') else 'saraf',
                    user_id=user_info.get('employee_id') or saraf_id,
                    user_name=user_info.get('full_name', 'Unknown'),
                    action_type='delete_transaction',
                    description=f'Delete transaction {transaction_id} - {transaction_type} {amount} {currency.currency_code}'
                )
            
            return Response({
                'message': 'Transaction successfully deleted and balance updated'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in DeleteTransactionView: {str(e)}")
            return Response({
                'error': 'Error deleting transaction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)