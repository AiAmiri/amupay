from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime, timedelta
import logging

from .models import ExchangeTransaction
from .serializers import (
    ExchangeTransactionSerializer,
    ExchangeTransactionCreateSerializer,
    ExchangeTransactionListSerializer,
    ExchangeTransactionUpdateSerializer
)
from saraf_account.models import SarafAccount, SarafEmployee, ActionLog

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
            'full_name': token.get('full_name'),
            'email_or_whatsapp_number': token.get('email_or_whatsapp_number'),
            'employee_name': token.get('employee_name')
        }
        
        return user_info
    except Exception as e:
        logger.error(f"Error extracting user info from token: {str(e)}")
        return None


class ExchangeTransactionListView(APIView):
    """
    List and filter exchange transactions
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of exchange transactions with filters"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Get query parameters for filtering
            sell_currency = request.query_params.get('sell_currency', '').upper()
            buy_currency = request.query_params.get('buy_currency', '').upper()
            transaction_type = request.query_params.get('transaction_type', '')
            name_search = request.query_params.get('name', '')
            performed_by = request.query_params.get('performed_by', '')
            
            # Performer filters (similar to hawala history)
            performer = request.query_params.get('performer', '')  # Filter by performer name (case-insensitive search)
            performer_id = request.query_params.get('performer_id', '')  # Filter by performer employee ID
            performer_type = request.query_params.get('performer_type', '')  # Filter by performer type (saraf/employee)
            employee_id = request.query_params.get('employee_id', '')  # Filter by employee ID
            
            # Time filters
            time_filter = request.query_params.get('time_filter', '')
            time_range = request.query_params.get('time_range', '')  # Alternative time filter (today, week, month, all)
            start_date = request.query_params.get('start_date', '')
            end_date = request.query_params.get('end_date', '')
            
            # Build query
            query = Q(saraf_account=saraf_account)
            
            # Currency filters
            if sell_currency:
                query &= Q(sell_currency=sell_currency)
            if buy_currency:
                query &= Q(buy_currency=buy_currency)
            
            # Transaction type filter
            if transaction_type:
                query &= Q(transaction_type=transaction_type)
            
            # Name search
            if name_search:
                query &= Q(name__icontains=name_search)
            
            # Performed by filter (legacy - kept for backward compatibility)
            if performed_by:
                query &= (
                    Q(performed_by_saraf__full_name__icontains=performed_by) |
                    Q(performed_by_employee__full_name__icontains=performed_by)
                )
            
            # Performer filters (new structured filters)
            if performer:
                # Filter by performer name (case-insensitive search)
                query &= (
                    Q(performed_by_saraf__full_name__icontains=performer) |
                    Q(performed_by_employee__full_name__icontains=performer)
                )
            
            if performer_id:
                try:
                    performer_id_int = int(performer_id)
                    query &= (
                        Q(performed_by_saraf__saraf_id=performer_id_int) |
                        Q(performed_by_employee__employee_id=performer_id_int)
                    )
                except ValueError:
                    pass  # Ignore invalid performer_id
            
            if performer_type and performer_type in ['saraf', 'employee']:
                if performer_type == 'saraf':
                    # Filter for transactions performed by saraf (no employee)
                    query &= Q(performed_by_employee__isnull=True)
                elif performer_type == 'employee':
                    # Filter for transactions performed by employee
                    query &= Q(performed_by_employee__isnull=False)
            
            if employee_id:
                try:
                    employee_id_int = int(employee_id)
                    query &= Q(performed_by_employee__employee_id=employee_id_int)
                except ValueError:
                    pass  # Ignore invalid employee_id
            
            # Time filters
            # Support both time_filter (legacy) and time_range (new)
            time_filter_to_use = time_range if time_range else time_filter
            if time_filter_to_use:
                now = datetime.now()
                if time_filter_to_use == 'today':
                    query &= Q(transaction_date__date=now.date())
                elif time_filter_to_use == 'week':
                    week_ago = now - timedelta(days=7)
                    query &= Q(transaction_date__gte=week_ago)
                elif time_filter_to_use == 'month':
                    month_ago = now - timedelta(days=30)
                    query &= Q(transaction_date__gte=month_ago)
                # 'all' means no time filter, so we don't add anything
            
            # Date range filter
            if start_date:
                try:
                    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                    query &= Q(transaction_date__gte=start_datetime)
                except ValueError:
                    return Response({
                        'error': 'Invalid start_date format. Use YYYY-MM-DD'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if end_date:
                try:
                    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                    # Add one day to include the entire end date
                    end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
                    query &= Q(transaction_date__lte=end_datetime)
                except ValueError:
                    return Response({
                        'error': 'Invalid end_date format. Use YYYY-MM-DD'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get transactions
            transactions = ExchangeTransaction.objects.filter(query).select_related(
                'saraf_account',
                'performed_by_saraf',
                'performed_by_employee'
            ).order_by('-transaction_date', '-created_at')
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            total_count = transactions.count()
            transactions_page = transactions[start_index:end_index]
            
            serializer = ExchangeTransactionListSerializer(transactions_page, many=True)
            
            # Build filters_applied dictionary
            filters_applied = {}
            if sell_currency:
                filters_applied['sell_currency'] = sell_currency
            if buy_currency:
                filters_applied['buy_currency'] = buy_currency
            if transaction_type:
                filters_applied['transaction_type'] = transaction_type
            if name_search:
                filters_applied['name'] = name_search
            if performed_by:
                filters_applied['performed_by'] = performed_by
            if performer:
                filters_applied['performer'] = performer
            if performer_id:
                filters_applied['performer_id'] = performer_id
            if performer_type:
                filters_applied['performer_type'] = performer_type
            if employee_id:
                filters_applied['employee_id'] = employee_id
            if time_filter_to_use:
                filters_applied['time_filter'] = time_filter_to_use
            if start_date:
                filters_applied['start_date'] = start_date
            if end_date:
                filters_applied['end_date'] = end_date
            
            return Response({
                'message': 'Exchange transactions list',
                'transactions': serializer.data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size
                },
                'filters_applied': filters_applied
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting exchange transactions: {str(e)}")
            return Response({
                'error': 'Error getting exchange transactions',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExchangeTransactionCreateView(APIView):
    """
    Create new exchange transaction
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create new exchange transaction"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check permission to create exchange
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('create_exchange'):
                        return Response({
                            'error': 'You do not have permission to create exchange transactions'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Data validation
            serializer = ExchangeTransactionCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate customer account if provided
            customer_account_id = request.data.get('customer_account_id')
            if customer_account_id:
                from saraf_create_accounts.models import SarafCustomerAccount
                try:
                    customer_account = SarafCustomerAccount.objects.get(account_id=customer_account_id)
                    # Verify the customer account belongs to the same saraf
                    if customer_account.saraf_account != saraf_account:
                        return Response({
                            'error': 'Customer account does not belong to your saraf'
                        }, status=status.HTTP_400_BAD_REQUEST)
                except SarafCustomerAccount.DoesNotExist:
                    return Response({
                        'error': 'Customer account not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            with transaction.atomic():
                # Create new exchange transaction
                exchange_transaction = serializer.save(
                    saraf_account=saraf_account,
                    performed_by_saraf=saraf_account if not user_info.get('employee_id') else None,
                    performed_by_employee=SarafEmployee.objects.get(employee_id=user_info['employee_id']) if user_info.get('employee_id') else None
                )
                
                # Update balances based on transaction type
                self._update_balances_for_exchange(exchange_transaction, saraf_account)
                
                # Log the action
                ActionLog.objects.create(
                    saraf=saraf_account,
                    user_type='employee' if user_info.get('employee_id') else 'saraf',
                    user_id=user_info.get('employee_id') or saraf_id,
                    user_name=user_info.get('full_name', 'Unknown'),
                    action_type='create_exchange',
                    description=f'Create exchange: {exchange_transaction.sell_amount} {exchange_transaction.sell_currency} → {exchange_transaction.buy_amount} {exchange_transaction.buy_currency}'
                )
                
                # Return created transaction
                response_serializer = ExchangeTransactionSerializer(exchange_transaction)
                
                return Response({
                    'message': 'Exchange transaction created successfully',
                    'transaction': response_serializer.data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error creating exchange transaction: {str(e)}")
            return Response({
                'error': 'Error creating exchange transaction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_balances_for_exchange(self, exchange_transaction, saraf_account):
        """Update balances based on transaction type"""
        try:
            from saraf_balance.models import SarafBalance
            from saraf_create_accounts.models import CustomerBalance
            from transaction.models import Transaction
            
            transaction_type = exchange_transaction.transaction_type
            customer_account = exchange_transaction.customer_account
            
            # Get currency objects
            from currency.models import Currency
            sell_currency = Currency.objects.get(currency_code=exchange_transaction.sell_currency)
            buy_currency = Currency.objects.get(currency_code=exchange_transaction.buy_currency)
            
            if transaction_type == 'customer' and customer_account:
                # Customer transaction: Update customer balance and saraf balance
                # From customer's perspective: saraf sells = customer buys (deposit), saraf buys = customer sells (withdrawal)
                self._update_customer_and_saraf_balances(
                    customer_account, saraf_account, 
                    sell_currency, exchange_transaction.sell_amount, 'deposit',
                    buy_currency, exchange_transaction.buy_amount, 'withdrawal',
                    exchange_transaction
                )
                
            elif transaction_type == 'exchanger' and customer_account:
                # Exchanger transaction: Update exchanger balance and saraf balance
                # From exchanger's perspective: saraf sells = exchanger buys (deposit), saraf buys = exchanger sells (withdrawal)
                self._update_customer_and_saraf_balances(
                    customer_account, saraf_account,
                    sell_currency, exchange_transaction.sell_amount, 'deposit',
                    buy_currency, exchange_transaction.buy_amount, 'withdrawal',
                    exchange_transaction
                )
                
            elif transaction_type == 'person':
                # Person transaction: Update only saraf balance
                self._update_saraf_balance_only(
                    saraf_account, sell_currency, exchange_transaction.sell_amount, 'withdrawal',
                    buy_currency, exchange_transaction.buy_amount, 'deposit',
                    exchange_transaction
                )
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating balances for exchange transaction: {str(e)}")
            # Don't fail the transaction, just log the error
    
    def _update_customer_and_saraf_balances(self, customer_account, saraf_account, 
                                          sell_currency, sell_amount, sell_type,
                                          buy_currency, buy_amount, buy_type,
                                          exchange_transaction):
        """Update both customer and saraf balances"""
        from saraf_balance.models import SarafBalance
        from saraf_create_accounts.models import CustomerBalance
        from transaction.models import Transaction
        
        # Update customer balance for sell currency (deposit - customer buys what saraf sells)
        customer_balance_sell, _ = CustomerBalance.get_or_create_balance(customer_account, sell_currency)
        customer_balance_sell.update_balance(sell_amount, sell_type)
        
        # Update customer balance for buy currency (withdrawal - customer sells what saraf buys)
        customer_balance_buy, _ = CustomerBalance.get_or_create_balance(customer_account, buy_currency)
        customer_balance_buy.update_balance(buy_amount, buy_type)
        
        # Update saraf balance for sell currency (withdrawal - saraf sells)
        saraf_balance_sell, _ = SarafBalance.get_or_create_balance(saraf_account, sell_currency)
        saraf_balance_sell.update_balance(sell_amount, 'withdrawal')
        
        # Update saraf balance for buy currency (deposit - saraf buys)
        saraf_balance_buy, _ = SarafBalance.get_or_create_balance(saraf_account, buy_currency)
        saraf_balance_buy.update_balance(buy_amount, 'deposit')
        
        # Log transactions
        Transaction.objects.create(
            transaction_type='exchange_sell',
            amount=sell_amount,
            currency=sell_currency,
            saraf_account=saraf_account,
            performer_user_id=saraf_account.saraf_id,
            performer_user_type='saraf',
            performer_full_name=saraf_account.full_name,
            performer_employee_id=None,
            performer_employee_name=None,
            description=f"Exchange transaction: {exchange_transaction.name} - Sell {sell_amount} {sell_currency.currency_code}"
        )
        
        Transaction.objects.create(
            transaction_type='exchange_buy',
            amount=buy_amount,
            currency=buy_currency,
            saraf_account=saraf_account,
            performer_user_id=saraf_account.saraf_id,
            performer_user_type='saraf',
            performer_full_name=saraf_account.full_name,
            performer_employee_id=None,
            performer_employee_name=None,
            description=f"Exchange transaction: {exchange_transaction.name} - Buy {buy_amount} {buy_currency.currency_code}"
        )
    
    def _update_saraf_balance_only(self, saraf_account, sell_currency, sell_amount, sell_type,
                                 buy_currency, buy_amount, buy_type, exchange_transaction):
        """Update only saraf balance for person transactions"""
        from saraf_balance.models import SarafBalance
        from transaction.models import Transaction
        
        # Update saraf balance for sell currency (saraf sells - withdrawal)
        saraf_balance_sell, _ = SarafBalance.get_or_create_balance(saraf_account, sell_currency)
        saraf_balance_sell.update_balance(sell_amount, sell_type)
        
        # Update saraf balance for buy currency (saraf buys - deposit)
        saraf_balance_buy, _ = SarafBalance.get_or_create_balance(saraf_account, buy_currency)
        saraf_balance_buy.update_balance(buy_amount, buy_type)
        
        # Log transactions
        Transaction.objects.create(
            transaction_type='exchange_person_sell',
            amount=sell_amount,
            currency=sell_currency,
            saraf_account=saraf_account,
            performer_user_id=saraf_account.saraf_id,
            performer_user_type='saraf',
            performer_full_name=saraf_account.full_name,
            performer_employee_id=None,
            performer_employee_name=None,
            description=f"Person exchange transaction: {exchange_transaction.name} - Sell {sell_amount} {sell_currency.currency_code}"
        )
        
        Transaction.objects.create(
            transaction_type='exchange_person_buy',
            amount=buy_amount,
            currency=buy_currency,
            saraf_account=saraf_account,
            performer_user_id=saraf_account.saraf_id,
            performer_user_type='saraf',
            performer_full_name=saraf_account.full_name,
            performer_employee_id=None,
            performer_employee_name=None,
            description=f"Person exchange transaction: {exchange_transaction.name} - Buy {buy_amount} {buy_currency.currency_code}"
        )


class ExchangeTransactionDetailView(APIView):
    """
    Retrieve, update or delete exchange transaction
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, exchange_id):
        """Get specific exchange transaction"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Get exchange transaction
            exchange_transaction = get_object_or_404(
                ExchangeTransaction,
                id=exchange_id,
                saraf_account=saraf_account
            )
            
            serializer = ExchangeTransactionSerializer(exchange_transaction)
            
            return Response({
                'message': 'Exchange transaction details',
                'transaction': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting exchange transaction: {str(e)}")
            return Response({
                'error': 'Error getting exchange transaction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, exchange_id):
        """Update exchange transaction"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check permission to update exchange
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('create_exchange'):
                        return Response({
                            'error': 'You do not have permission to update exchange transactions'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Get exchange transaction
            exchange_transaction = get_object_or_404(
                ExchangeTransaction,
                id=exchange_id,
                saraf_account=saraf_account
            )
            
            # Data validation
            serializer = ExchangeTransactionUpdateSerializer(exchange_transaction, data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # Update exchange transaction
                updated_transaction = serializer.save()
                
                # Log the action
                ActionLog.objects.create(
                    saraf=saraf_account,
                    user_type='employee' if user_info.get('employee_id') else 'saraf',
                    user_id=user_info.get('employee_id') or saraf_id,
                    user_name=user_info.get('full_name', 'Unknown'),
                    action_type='update_exchange',
                    description=f'Update exchange: {updated_transaction.sell_amount} {updated_transaction.sell_currency} → {updated_transaction.buy_amount} {updated_transaction.buy_currency}'
                )
                
                # Return updated transaction
                response_serializer = ExchangeTransactionSerializer(updated_transaction)
                
                return Response({
                    'message': 'Exchange transaction updated successfully',
                    'transaction': response_serializer.data
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error updating exchange transaction: {str(e)}")
            return Response({
                'error': 'Error updating exchange transaction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, exchange_id):
        """Delete exchange transaction"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check permission to delete exchange
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('create_exchange'):
                        return Response({
                            'error': 'You do not have permission to delete exchange transactions'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Get exchange transaction
            exchange_transaction = get_object_or_404(
                ExchangeTransaction,
                id=exchange_id,
                saraf_account=saraf_account
            )
            
            with transaction.atomic():
                # Log the action before deletion
                ActionLog.objects.create(
                    saraf=saraf_account,
                    user_type='employee' if user_info.get('employee_id') else 'saraf',
                    user_id=user_info.get('employee_id') or saraf_id,
                    user_name=user_info.get('full_name', 'Unknown'),
                    action_type='delete_exchange',
                    description=f'Delete exchange: {exchange_transaction.sell_amount} {exchange_transaction.sell_currency} → {exchange_transaction.buy_amount} {exchange_transaction.buy_currency}'
                )
                
                # Delete exchange transaction
                exchange_transaction.delete()
                
                return Response({
                    'message': 'Exchange transaction deleted successfully'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error deleting exchange transaction: {str(e)}")
            return Response({
                'error': 'Error deleting exchange transaction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExchangeTransactionCreateWithBalanceView(APIView):
    """
    Create exchange transaction and update saraf balances
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create exchange transaction and update balances"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Validate serializer
            serializer = ExchangeTransactionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Use database transaction to ensure consistency
            with transaction.atomic():
                # Create exchange transaction
                exchange_transaction = serializer.save(
                    saraf_account=saraf_account,
                    performed_by_saraf=saraf_account if user_info.get('user_type') == 'saraf' else None,
                    performed_by_employee=get_object_or_404(SarafEmployee, employee_id=user_info['employee_id']) if user_info.get('user_type') == 'employee' else None
                )
                
                # Update saraf balances
                self._update_saraf_balances(saraf_account, exchange_transaction)
                
                return Response({
                    'message': 'Exchange transaction created successfully',
                    'transaction': ExchangeTransactionSerializer(exchange_transaction).data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error creating exchange transaction: {str(e)}")
            return Response({
                'error': 'Error creating exchange transaction',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_saraf_balances(self, saraf_account, exchange_transaction):
        """Update saraf balances based on exchange transaction"""
        from saraf_balance.models import SarafBalance
        from currency.models import Currency
        
        # Get currency objects
        sell_currency = Currency.objects.get(currency_code=exchange_transaction.sell_currency)
        buy_currency = Currency.objects.get(currency_code=exchange_transaction.buy_currency)
        
        # Update sell currency balance (decrease - saraf is selling)
        if exchange_transaction.sell_amount > 0:
            sell_balance, _ = SarafBalance.get_or_create_balance(saraf_account, sell_currency)
            sell_balance.update_balance(exchange_transaction.sell_amount, 'withdrawal')
        
        # Update buy currency balance (increase - saraf is buying)
        if exchange_transaction.buy_amount > 0:
            buy_balance, _ = SarafBalance.get_or_create_balance(saraf_account, buy_currency)
            buy_balance.update_balance(exchange_transaction.buy_amount, 'deposit')


class CustomerExchangeListView(APIView):
    """
    Public endpoint to get all exchange transactions for a customer by phone number
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get all exchange transactions for a customer based on phone number"""
        try:
            # Get phone number from query parameters
            phone = request.query_params.get('phone', '').strip()
            
            if not phone:
                return Response({
                    'error': 'Phone number is required',
                    'message': 'Please provide a phone number as a query parameter (e.g., ?phone=0123456789)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate phone number format (10 digits starting with 0)
            import re
            if not re.match(r'^0\d{9}$', phone):
                return Response({
                    'error': 'Invalid phone number format',
                    'message': 'Phone number must be 10 digits and start with 0 (e.g., 0123456789)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Import SarafCustomerAccount model
            from saraf_create_accounts.models import SarafCustomerAccount
            
            # Find all customer accounts with this phone number
            customer_accounts = SarafCustomerAccount.objects.filter(
                phone=phone,
                is_active=True
            ).select_related('saraf_account')
            
            if not customer_accounts.exists():
                return Response({
                    'message': 'No customer accounts found for this phone number',
                    'phone': phone,
                    'exchanges': [],
                    'total_count': 0
                }, status=status.HTTP_200_OK)
            
            # Get all exchange transactions for these customer accounts
            exchange_transactions = ExchangeTransaction.objects.filter(
                customer_account__in=customer_accounts
            ).select_related(
                'customer_account',
                'saraf_account',
                'performed_by_saraf',
                'performed_by_employee'
            ).order_by('-transaction_date', '-created_at')
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            total_count = exchange_transactions.count()
            transactions_page = exchange_transactions[start_index:end_index]
            
            # Serialize the transactions
            serializer = ExchangeTransactionSerializer(transactions_page, many=True)
            
            # Get customer account information
            customer_info = []
            for account in customer_accounts:
                customer_info.append({
                    'account_id': account.account_id,
                    'account_number': account.account_number,
                    'full_name': account.full_name,
                    'account_type': account.account_type,
                    'phone': account.phone,
                    'saraf_name': account.saraf_account.full_name if account.saraf_account else None,
                    'saraf_id': account.saraf_account.saraf_id if account.saraf_account else None
                })
            
            return Response({
                'message': 'Exchange transactions retrieved successfully',
                'phone': phone,
                'customer_accounts': customer_info,
                'exchanges': serializer.data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size if total_count > 0 else 0
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting customer exchange transactions: {str(e)}")
            return Response({
                'error': 'Error getting exchange transactions',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
