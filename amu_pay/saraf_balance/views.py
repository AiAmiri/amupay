from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import SarafBalance
from saraf_account.models import SarafAccount, SarafEmployee
from currency.models import Currency, SarafSupportedCurrency
import logging

logger = logging.getLogger(__name__)


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


class SarafBalanceListView(APIView):
    """Display list of exchange balances"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of exchange balances"""
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
                            'error': 'You do not have permission to view balance'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Get balances
            balances = SarafBalance.objects.filter(
                saraf_account=saraf_account
            ).select_related('currency').order_by('currency__currency_code')
            
            balance_data = []
            for balance in balances:
                balance_data.append({
                    'currency_code': balance.currency.currency_code,
                    'currency_name': balance.currency.currency_name_local,
                    'currency_symbol': balance.currency.symbol,
                    'balance': balance.balance,
                    'total_deposits': balance.total_deposits,
                    'total_withdrawals': balance.total_withdrawals,
                    'transaction_count': balance.transaction_count,
                    'last_updated': balance.last_updated
                })
            
            return Response({
                'message': 'Exchange balances list',
                'saraf_name': saraf_account.full_name,
                'balances': balance_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error getting balances',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SarafBalanceDetailView(APIView):
    """Display balance details for a specific currency"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, currency_code):
        """Get balance for a specific currency"""
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
                            'error': 'You do not have permission to view balance'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Find currency
            currency = get_object_or_404(Currency, currency_code=currency_code.upper())
            
            # Check supported currency
            if not SarafSupportedCurrency.objects.filter(
                saraf_account=saraf_account,
                currency=currency,
                is_active=True
            ).exists():
                return Response({
                    'error': f'Currency {currency_code} is not supported by this exchange'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create balance
            balance, created = SarafBalance.get_or_create_balance(saraf_account, currency)
            
            balance_data = {
                'currency_code': balance.currency.currency_code,
                'currency_name': balance.currency.currency_name_local,
                'currency_symbol': balance.currency.symbol,
                'balance': balance.balance,
                'total_deposits': balance.total_deposits,
                'total_withdrawals': balance.total_withdrawals,
                'transaction_count': balance.transaction_count,
                'last_updated': balance.last_updated,
                'created_at': balance.created_at
            }
            
            return Response({
                'message': f'Balance for currency {currency_code}',
                'balance': balance_data,
                'is_new': created
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error getting balance',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteSarafBalanceView(APIView):
    """Delete balance for a specific currency"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, currency_code):
        """Delete balance for a specific currency"""
        try:
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check balance deletion permissions
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('delete_balance'):
                        return Response({
                            'error': 'You do not have permission to delete balance'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Find currency
            currency = get_object_or_404(Currency, currency_code=currency_code.upper())
            
            # Find balance
            balance = get_object_or_404(
                SarafBalance,
                saraf_account=saraf_account,
                currency=currency
            )
            
            # Check if there are transactions for this currency
            from transaction.models import Transaction
            transaction_count = Transaction.objects.filter(
                saraf_account=saraf_account,
                currency=currency
            ).count()
            
            if transaction_count > 0:
                return Response({
                    'error': f'Cannot delete balance for currency {currency_code} because {transaction_count} transactions exist for this currency. Please delete transactions first.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Save information for log
            balance_amount = balance.balance
            
            # Delete balance
            balance.delete()
            
            # Log the action
            from saraf_account.models import ActionLog
            ActionLog.objects.create(
                saraf=saraf_account,
                user_type='employee' if user_info.get('employee_id') else 'saraf',
                user_id=user_info.get('employee_id') or saraf_id,
                user_name=user_info.get('full_name', 'Unknown'),
                action_type='delete_balance',
                description=f'Delete balance for currency {currency_code} with amount {balance_amount}'
            )
            
            return Response({
                'message': f'Balance for currency {currency_code} successfully deleted'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in DeleteSarafBalanceView: {str(e)}")
            return Response({
                'error': 'Error deleting balance',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
