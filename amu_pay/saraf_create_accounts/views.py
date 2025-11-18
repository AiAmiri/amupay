from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import models

from .models import SarafCustomerAccount, CustomerTransaction, CustomerBalance
from .serializers import (
    SarafCustomerAccountSerializer, CustomerTransactionSerializer, 
    CustomerBalanceSerializer, CreateCustomerAccountSerializer,
    CustomerTransactionCreateSerializer
)
from utils.jwt_helpers import get_user_info_from_token, create_error_response, create_success_response
import logging

logger = logging.getLogger(__name__)




class CreateCustomerAccountView(APIView):
    """Create customer accounts for Saraf"""
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def post(self, request):
        """Create a new customer account"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user has permission to create accounts
        if user_info['user_type'] == 'employee':
            from saraf_account.models import SarafEmployee
            try:
                employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                if not employee.has_permission('create_accounts'):
                    return Response({
                        'error': 'You do not have permission to create accounts'
                    }, status=status.HTTP_403_FORBIDDEN)
            except SarafEmployee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate required fields
        full_name = request.data.get('full_name', '').strip()
        account_type = request.data.get('account_type', '').strip()
        phone = request.data.get('phone', '').strip()
        
        if not account_type or not phone:
            return Response({
                'error': 'account_type and phone are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if account_type not in ['exchanger', 'customer']:
            return Response({
                'error': 'account_type must be either "exchanger" or "customer"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate phone format
        import re
        if not re.match(r'^0\d{9}$', phone):
            return Response({
                'error': 'Phone must be 10 digits and start with 0'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if phone already exists for this saraf
        if SarafCustomerAccount.objects.filter(saraf_account=saraf_account, phone=phone).exists():
            return Response({
                'error': 'A customer account with this phone number already exists for your saraf'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # Create customer account
                customer_account = SarafCustomerAccount(
                    saraf_account=saraf_account,
                    full_name=full_name or None,
                    account_type=account_type,
                    phone=phone,
                    address=request.data.get('address', '').strip() or None,
                    job=request.data.get('job', '').strip() or None,
                    photo=request.FILES.get('photo')
                )
                customer_account.save()
                
                # Initialize balances for all currencies
                from currency.models import Currency
                currencies = Currency.objects.all()
                for currency in currencies:
                    CustomerBalance.get_or_create_balance(customer_account, currency)
                
                # Serialize response
                serializer = SarafCustomerAccountSerializer(customer_account, context={'request': request})
                
                return Response({
                    'message': 'Customer account created successfully',
                    'account': serializer.data
                }, status=status.HTTP_201_CREATED)
                
        except ValidationError as e:
            return Response({
                'error': 'Validation error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating customer account: {str(e)}")
            return Response({
                'error': 'Failed to create customer account',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListCustomerAccountsView(APIView):
    """List customer accounts for Saraf"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List all customer accounts for the authenticated saraf"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get filter parameters
        account_type = request.query_params.get('account_type')
        search = request.query_params.get('search')
        
        # Build queryset
        queryset = SarafCustomerAccount.objects.filter(saraf_account=saraf_account)
        
        if account_type:
            queryset = queryset.filter(account_type=account_type)
        
        if search:
            queryset = queryset.filter(
                models.Q(full_name__icontains=search) |
                models.Q(phone__icontains=search) |
                models.Q(account_number__icontains=search)
            )
        
        # Order by creation date (newest first)
        queryset = queryset.order_by('-created_at')
        
        # Serialize response
        serializer = SarafCustomerAccountSerializer(queryset, many=True, context={'request': request})
        
        return Response({
            'message': 'Customer accounts retrieved successfully',
            'count': len(serializer.data),
            'accounts': serializer.data
        }, status=status.HTTP_200_OK)


class CustomerAccountDetailView(APIView):
    """Get, update, or delete specific customer account"""
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get(self, request, account_id):
        """Get specific customer account details"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize response
        serializer = SarafCustomerAccountSerializer(customer_account, context={'request': request})
        
        return Response({
            'message': 'Customer account retrieved successfully',
            'account': serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request, account_id):
        """Update customer account"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user has permission to update accounts
        if user_info['user_type'] == 'employee':
            from saraf_account.models import SarafEmployee
            try:
                employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                if not employee.has_permission('create_accounts'):
                    return Response({
                        'error': 'You do not have permission to update accounts'
                    }, status=status.HTTP_403_FORBIDDEN)
            except SarafEmployee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Update fields
        if 'full_name' in request.data:
            customer_account.full_name = request.data.get('full_name', '').strip() or None
        if 'account_type' in request.data:
            account_type = request.data.get('account_type', '').strip()
            if account_type not in ['exchanger', 'customer']:
                return Response({
                    'error': 'account_type must be either "exchanger" or "customer"'
                }, status=status.HTTP_400_BAD_REQUEST)
            customer_account.account_type = account_type
        if 'phone' in request.data:
            phone = request.data.get('phone', '').strip()
            import re
            if not re.match(r'^0\d{9}$', phone):
                return Response({
                    'error': 'Phone must be 10 digits and start with 0'
                }, status=status.HTTP_400_BAD_REQUEST)
            # Check if phone already exists for this saraf (excluding current account)
            if SarafCustomerAccount.objects.filter(
                saraf_account=saraf_account, 
                phone=phone
            ).exclude(account_id=account_id).exists():
                return Response({
                    'error': 'A customer account with this phone number already exists for your saraf'
                }, status=status.HTTP_400_BAD_REQUEST)
            customer_account.phone = phone
        if 'address' in request.data:
            customer_account.address = request.data.get('address', '').strip() or None
        if 'job' in request.data:
            customer_account.job = request.data.get('job', '').strip() or None
        if 'photo' in request.FILES:
            customer_account.photo = request.FILES.get('photo')
        
        try:
            customer_account.save()
            
            # Serialize response
            serializer = SarafCustomerAccountSerializer(customer_account, context={'request': request})
            
            return Response({
                'message': 'Customer account updated successfully',
                'account': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response({
                'error': 'Validation error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating customer account: {str(e)}")
            return Response({
                'error': 'Failed to update customer account',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, account_id):
        """Delete customer account"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user has permission to delete accounts
        if user_info['user_type'] == 'employee':
            from saraf_account.models import SarafEmployee
            try:
                employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                if not employee.has_permission('delete_accounts'):
                    return Response({
                        'error': 'You do not have permission to delete accounts'
                    }, status=status.HTTP_403_FORBIDDEN)
            except SarafEmployee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            account_number = customer_account.account_number
            customer_account.delete()
            
            return Response({
                'message': f'Customer account {account_number} deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting customer account: {str(e)}")
            return Response({
                'error': 'Failed to delete customer account',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerDepositView(APIView):
    """Deposit money to customer account"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, account_id):
        """Deposit money to customer account"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user has permission to deposit money
        if user_info['user_type'] == 'employee':
            from saraf_account.models import SarafEmployee
            try:
                employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                if not employee.has_permission('deposit_to_customer'):
                    return Response({
                        'error': 'You do not have permission to deposit money to customers'
                    }, status=status.HTTP_403_FORBIDDEN)
            except SarafEmployee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate input
        currency_code = request.data.get('currency_code', '').strip().upper()
        amount = request.data.get('amount')
        description = request.data.get('description', '').strip()
        
        if not currency_code or not amount:
            return Response({
                'error': 'currency_code and amount are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({
                    'error': 'Amount must be greater than 0'
                }, status=status.HTTP_400_BAD_REQUEST)
            # Convert to Decimal for database operations
            from decimal import Decimal
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid amount format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get currency
        from currency.models import Currency
        try:
            currency = Currency.objects.get(currency_code=currency_code, is_active=True)
        except Currency.DoesNotExist:
            return Response({
                'error': f'Currency {currency_code} not found or not active'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                # Create transaction
                customer_transaction = CustomerTransaction.create_transaction(
                    customer_account=customer_account,
                    currency=currency,
                    transaction_type='deposit',
                    amount=amount,
                    description=description or f'Deposit {amount} {currency_code}',
                    user_info=user_info
                )
                
                # Serialize response
                serializer = CustomerTransactionSerializer(customer_transaction, context={'request': request})
                
                return Response({
                    'message': f'Deposit of {amount} {currency_code} successful',
                    'transaction': serializer.data
                }, status=status.HTTP_201_CREATED)
                
        except ValidationError as e:
            return Response({
                'error': 'Validation error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing deposit: {str(e)}")
            return Response({
                'error': 'Failed to process deposit',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerWithdrawView(APIView):
    """Withdraw money from customer account"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, account_id):
        """Withdraw money from customer account"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user has permission to withdraw money
        if user_info['user_type'] == 'employee':
            from saraf_account.models import SarafEmployee
            try:
                employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                if not employee.has_permission('withdraw_to_customer'):
                    return Response({
                        'error': 'You do not have permission to withdraw money from customers'
                    }, status=status.HTTP_403_FORBIDDEN)
            except SarafEmployee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate input
        currency_code = request.data.get('currency_code', '').strip().upper()
        amount = request.data.get('amount')
        description = request.data.get('description', '').strip()
        
        if not currency_code or not amount:
            return Response({
                'error': 'currency_code and amount are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({
                    'error': 'Amount must be greater than 0'
                }, status=status.HTTP_400_BAD_REQUEST)
            # Convert to Decimal for database operations
            from decimal import Decimal
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid amount format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get currency
        from currency.models import Currency
        try:
            currency = Currency.objects.get(currency_code=currency_code, is_active=True)
        except Currency.DoesNotExist:
            return Response({
                'error': f'Currency {currency_code} not found or not active'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                # Create transaction
                customer_transaction = CustomerTransaction.create_transaction(
                    customer_account=customer_account,
                    currency=currency,
                    transaction_type='withdrawal',
                    amount=amount,
                    description=description or f'Withdrawal {amount} {currency_code}',
                    user_info=user_info
                )
                
                # Serialize response
                serializer = CustomerTransactionSerializer(customer_transaction, context={'request': request})
                
                return Response({
                    'message': f'Withdrawal of {amount} {currency_code} successful',
                    'transaction': serializer.data
                }, status=status.HTTP_201_CREATED)
                
        except ValidationError as e:
            return Response({
                'error': 'Validation error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing withdrawal: {str(e)}")
            return Response({
                'error': 'Failed to process withdrawal',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExchangerGiveMoneyView(APIView):
    """Give money to exchanger account"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, account_id):
        """Give money to exchanger account"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user has permission to give money
        if user_info['user_type'] == 'employee':
            from saraf_account.models import SarafEmployee
            try:
                employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                if not employee.has_permission('give_money'):
                    return Response({
                        'error': 'You do not have permission to give money'
                    }, status=status.HTTP_403_FORBIDDEN)
            except SarafEmployee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account,
                account_type='exchanger'
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Exchanger account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate input
        currency_code = request.data.get('currency_code', '').strip().upper()
        amount = request.data.get('amount')
        description = request.data.get('description', '').strip()
        
        if not currency_code or not amount:
            return Response({
                'error': 'currency_code and amount are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({
                    'error': 'Amount must be greater than 0'
                }, status=status.HTTP_400_BAD_REQUEST)
            # Convert to Decimal for database operations
            from decimal import Decimal
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid amount format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get currency
        from currency.models import Currency
        try:
            currency = Currency.objects.get(currency_code=currency_code, is_active=True)
        except Currency.DoesNotExist:
            return Response({
                'error': f'Currency {currency_code} not found or not active'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                # Create transaction
                customer_transaction = CustomerTransaction.create_transaction(
                    customer_account=customer_account,
                    currency=currency,
                    transaction_type='give_money',
                    amount=amount,
                    description=description or f'Give money {amount} {currency_code}',
                    user_info=user_info
                )
                
                # Serialize response
                serializer = CustomerTransactionSerializer(customer_transaction, context={'request': request})
                
                return Response({
                    'message': f'Give money {amount} {currency_code} successful',
                    'transaction': serializer.data
                }, status=status.HTTP_201_CREATED)
                
        except ValidationError as e:
            return Response({
                'error': 'Validation error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing give money: {str(e)}")
            return Response({
                'error': 'Failed to process give money',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExchangerTakeMoneyView(APIView):
    """Take money from exchanger account"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, account_id):
        """Take money from exchanger account"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user has permission to take money
        if user_info['user_type'] == 'employee':
            from saraf_account.models import SarafEmployee
            try:
                employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                if not employee.has_permission('take_money'):
                    return Response({
                        'error': 'You do not have permission to take money'
                    }, status=status.HTTP_403_FORBIDDEN)
            except SarafEmployee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account,
                account_type='exchanger'
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Exchanger account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate input
        currency_code = request.data.get('currency_code', '').strip().upper()
        amount = request.data.get('amount')
        description = request.data.get('description', '').strip()
        
        if not currency_code or not amount:
            return Response({
                'error': 'currency_code and amount are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
            if amount <= 0:
                return Response({
                    'error': 'Amount must be greater than 0'
                }, status=status.HTTP_400_BAD_REQUEST)
            # Convert to Decimal for database operations
            from decimal import Decimal
            amount = Decimal(str(amount))
        except (ValueError, TypeError):
            return Response({
                'error': 'Invalid amount format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get currency
        from currency.models import Currency
        try:
            currency = Currency.objects.get(currency_code=currency_code, is_active=True)
        except Currency.DoesNotExist:
            return Response({
                'error': f'Currency {currency_code} not found or not active'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                # Create transaction
                customer_transaction = CustomerTransaction.create_transaction(
                    customer_account=customer_account,
                    currency=currency,
                    transaction_type='take_money',
                    amount=amount,
                    description=description or f'Take money {amount} {currency_code}',
                    user_info=user_info
                )
                
                # Serialize response
                serializer = CustomerTransactionSerializer(customer_transaction, context={'request': request})
                
                return Response({
                    'message': f'Take money {amount} {currency_code} successful',
                    'transaction': serializer.data
                }, status=status.HTTP_201_CREATED)
                
        except ValidationError as e:
            return Response({
                'error': 'Validation error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing take money: {str(e)}")
            return Response({
                'error': 'Failed to process take money',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerTransactionListView(APIView):
    """List transactions for a specific customer account"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, account_id):
        """List all transactions for a customer account"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get filter parameters
        transaction_type = request.query_params.get('transaction_type')
        currency_id = request.query_params.get('currency_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Performer filters
        performer = request.query_params.get('performer', '')  # Filter by performer name (case-insensitive search)
        performer_id = request.query_params.get('performer_id', '')  # Filter by performer user ID
        performer_type = request.query_params.get('performer_type', '')  # Filter by performer type (saraf/employee)
        employee_id = request.query_params.get('employee_id', '')  # Filter by employee ID
        
        # Build queryset
        queryset = CustomerTransaction.objects.filter(customer_account=customer_account)
        
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        if currency_id:
            queryset = queryset.filter(currency_id=currency_id)
        
        if date_from:
            from django.utils.dateparse import parse_datetime
            try:
                date_from_parsed = parse_datetime(date_from)
                if date_from_parsed:
                    queryset = queryset.filter(created_at__gte=date_from_parsed)
            except ValueError:
                pass
        
        if date_to:
            from django.utils.dateparse import parse_datetime
            try:
                date_to_parsed = parse_datetime(date_to)
                if date_to_parsed:
                    queryset = queryset.filter(created_at__lte=date_to_parsed)
            except ValueError:
                pass
        
        # Performer filters
        if performer:
            # Filter by performer name (case-insensitive search)
            queryset = queryset.filter(performer_full_name__icontains=performer)
        
        if performer_id:
            try:
                performer_id_int = int(performer_id)
                queryset = queryset.filter(performer_user_id=performer_id_int)
            except ValueError:
                pass  # Ignore invalid performer_id
        
        if performer_type and performer_type in ['saraf', 'employee']:
            queryset = queryset.filter(performer_user_type=performer_type)
        
        if employee_id:
            try:
                employee_id_int = int(employee_id)
                queryset = queryset.filter(performer_employee_id=employee_id_int)
            except ValueError:
                pass  # Ignore invalid employee_id
        
        # Order by creation date (newest first)
        queryset = queryset.order_by('-created_at')
        
        # Serialize response
        serializer = CustomerTransactionSerializer(queryset, many=True, context={'request': request})
        
        return Response({
            'message': 'Customer transactions retrieved successfully',
            'account_number': customer_account.account_number,
            'customer_name': customer_account.full_name,
            'count': len(serializer.data),
            'transactions': serializer.data,
            'filters_applied': {
                'transaction_type': transaction_type,
                'currency_id': currency_id,
                'date_from': date_from,
                'date_to': date_to,
                'performer': performer,
                'performer_id': performer_id,
                'performer_type': performer_type,
                'employee_id': employee_id
            }
        }, status=status.HTTP_200_OK)


class PublicCustomerTransactionListView(APIView):
    """Public endpoint for customers to view their own transactions"""
    permission_classes = [AllowAny]
    
    def get(self, request, phone):
        """List transactions for a customer by phone number"""
        # Validate phone format
        import re
        if not re.match(r'^0\d{9}$', phone):
            return Response({
                'error': 'Invalid phone number format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get customer account by phone
        try:
            customer_account = SarafCustomerAccount.objects.get(phone=phone, is_active=True)
        except SarafCustomerAccount.DoesNotExist:
            return Response({
                'error': 'No account found with this phone number'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get filter parameters
        transaction_type = request.query_params.get('transaction_type')
        currency_id = request.query_params.get('currency_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Build queryset
        queryset = CustomerTransaction.objects.filter(customer_account=customer_account)
        
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        if currency_id:
            queryset = queryset.filter(currency_id=currency_id)
        
        if date_from:
            from django.utils.dateparse import parse_datetime
            try:
                date_from_parsed = parse_datetime(date_from)
                if date_from_parsed:
                    queryset = queryset.filter(created_at__gte=date_from_parsed)
            except ValueError:
                pass
        
        if date_to:
            from django.utils.dateparse import parse_datetime
            try:
                date_to_parsed = parse_datetime(date_to)
                if date_to_parsed:
                    queryset = queryset.filter(created_at__lte=date_to_parsed)
            except ValueError:
                pass
        
        # Order by creation date (newest first)
        queryset = queryset.order_by('-created_at')
        
        # Serialize response
        serializer = CustomerTransactionSerializer(queryset, many=True, context={'request': request})
        
        return Response({
            'message': 'Your transactions retrieved successfully',
            'account_number': customer_account.account_number,
            'customer_name': customer_account.full_name,
            'account_type': customer_account.get_account_type_display(),
            'count': len(serializer.data),
            'transactions': serializer.data
        }, status=status.HTTP_200_OK)


class CustomerBalanceListView(APIView):
    """List balances for a specific customer account"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, account_id):
        """List all balances for a customer account"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get balances
        balances = CustomerBalance.objects.filter(customer_account=customer_account)
        
        # Serialize response
        serializer = CustomerBalanceSerializer(balances, many=True, context={'request': request})
        
        return Response({
            'message': 'Customer balances retrieved successfully',
            'account_number': customer_account.account_number,
            'customer_name': customer_account.full_name,
            'count': len(serializer.data),
            'balances': serializer.data
        }, status=status.HTTP_200_OK)


class CustomerWithdrawalAmountsView(APIView):
    """Get total withdrawal amounts for a customer account"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, account_id):
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get withdrawal amounts by currency
        withdrawals = CustomerTransaction.objects.filter(
            customer_account=customer_account,
            transaction_type='withdrawal'
        ).values('currency__currency_code', 'currency__currency_name', 'currency__symbol').annotate(
            total_amount=models.Sum('amount'),
            transaction_count=models.Count('transaction_id')
        ).order_by('currency__currency_code')
        
        return Response({
            'message': 'Withdrawal amounts retrieved successfully',
            'account_number': customer_account.account_number,
            'customer_name': customer_account.full_name,
            'withdrawals': list(withdrawals)
        }, status=status.HTTP_200_OK)


class CustomerDepositAmountsView(APIView):
    """Get total deposit amounts for a customer account"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, account_id):
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get deposit amounts by currency
        deposits = CustomerTransaction.objects.filter(
            customer_account=customer_account,
            transaction_type='deposit'
        ).values('currency__currency_code', 'currency__currency_name', 'currency__symbol').annotate(
            total_amount=models.Sum('amount'),
            transaction_count=models.Count('transaction_id')
        ).order_by('currency__currency_code')
        
        return Response({
            'message': 'Deposit amounts retrieved successfully',
            'account_number': customer_account.account_number,
            'customer_name': customer_account.full_name,
            'deposits': list(deposits)
        }, status=status.HTTP_200_OK)


class ExchangerGivenAmountsView(APIView):
    """Get total given amounts for an exchanger account"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, account_id):
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account,
                account_type='exchanger'
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Exchanger account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get given amounts by currency
        given_amounts = CustomerTransaction.objects.filter(
            customer_account=customer_account,
            transaction_type='give_money'
        ).values('currency__currency_code', 'currency__currency_name', 'currency__symbol').annotate(
            total_amount=models.Sum('amount'),
            transaction_count=models.Count('transaction_id')
        ).order_by('currency__currency_code')
        
        return Response({
            'message': 'Given amounts retrieved successfully',
            'account_number': customer_account.account_number,
            'customer_name': customer_account.full_name,
            'given_amounts': list(given_amounts)
        }, status=status.HTTP_200_OK)


class ExchangerBalanceView(APIView):
    """Get detailed balance for an exchanger account including saraf balance impact"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, account_id):
        """Get detailed exchanger balance with saraf balance impact"""
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account (must be exchanger type)
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account,
                account_type='exchanger'
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Exchanger account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get exchanger balances
        customer_balances = CustomerBalance.objects.filter(customer_account=customer_account)
        balances_serializer = CustomerBalanceSerializer(
            customer_balances, 
            many=True, 
            context={'request': request}
        )
        
        # Get saraf balances to show impact
        from saraf_balance.models import SarafBalance
        saraf_balances = SarafBalance.objects.filter(saraf_account=saraf_account)
        saraf_balances_data = []
        for sb in saraf_balances:
            saraf_balances_data.append({
                'currency_code': sb.currency.currency_code,
                'currency_name': sb.currency.currency_name,
                'currency_symbol': sb.currency.symbol,
                'saraf_balance': float(sb.balance),
                'total_deposits': float(sb.total_deposits),
                'total_withdrawals': float(sb.total_withdrawals),
                'transaction_count': sb.transaction_count
            })
        
        # Get exchanger statistics
        from django.db.models import Sum, Count, Q
        exchanger_stats = CustomerTransaction.objects.filter(
            customer_account=customer_account
        ).values('currency__currency_code', 'currency__currency_name', 'currency__symbol').annotate(
            total_given=Sum('amount', filter=Q(transaction_type='give_money')),
            total_taken=Sum('amount', filter=Q(transaction_type='take_money')),
            given_count=Count('transaction_id', filter=Q(transaction_type='give_money')),
            taken_count=Count('transaction_id', filter=Q(transaction_type='take_money'))
        ).order_by('currency__currency_code')
        
        return Response({
            'message': 'Exchanger balance retrieved successfully',
            'account': {
                'account_id': customer_account.account_id,
                'account_number': customer_account.account_number,
                'full_name': customer_account.full_name,
                'phone': customer_account.phone,
                'account_type': customer_account.account_type
            },
            'exchanger_balances': balances_serializer.data,
            'saraf_balances_impact': saraf_balances_data,
            'exchanger_statistics': list(exchanger_stats),
            'note': 'Saraf balances show the net impact of all exchanger transactions on the saraf account'
        }, status=status.HTTP_200_OK)


class ExchangerTakenAmountsView(APIView):
    """Get total taken amounts for an exchanger account"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, account_id):
        # Get user info from JWT token
        user_info = get_user_info_from_token(request)
        if not user_info:
            return create_error_response('Invalid user token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # Get saraf account
        from saraf_account.models import SarafAccount
        try:
            saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
        except SarafAccount.DoesNotExist:
            return Response({'error': 'Saraf account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get customer account
        try:
            customer_account = SarafCustomerAccount.objects.get(
                account_id=account_id,
                saraf_account=saraf_account,
                account_type='exchanger'
            )
        except SarafCustomerAccount.DoesNotExist:
            return Response({'error': 'Exchanger account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get taken amounts by currency
        taken_amounts = CustomerTransaction.objects.filter(
            customer_account=customer_account,
            transaction_type='take_money'
        ).values('currency__currency_code', 'currency__currency_name', 'currency__symbol').annotate(
            total_amount=models.Sum('amount'),
            transaction_count=models.Count('transaction_id')
        ).order_by('currency__currency_code')
        
        return Response({
            'message': 'Taken amounts retrieved successfully',
            'account_number': customer_account.account_number,
            'customer_name': customer_account.full_name,
            'taken_amounts': list(taken_amounts)
        }, status=status.HTTP_200_OK)


class PublicAllAccountsTransactionsView(APIView):
    """Public endpoint to get all accounts and transactions for a phone number across all sarafs"""
    permission_classes = [AllowAny]
    
    def get(self, request, phone):
        """Get all accounts and transactions for a phone number across all sarafs"""
        # Validate phone format
        import re
        if not re.match(r'^0\d{9}$', phone):
            return Response({
                'error': 'Invalid phone number format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all customer accounts by phone across all sarafs
        customer_accounts = SarafCustomerAccount.objects.filter(
            phone=phone, 
            is_active=True
        ).select_related('saraf_account').order_by('saraf_account__saraf_id')
        
        if not customer_accounts.exists():
            return Response({
                'error': 'No accounts found with this phone number'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get filter parameters
        transaction_type = request.query_params.get('transaction_type')
        currency_id = request.query_params.get('currency_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Build response data
        accounts_data = []
        total_transactions = 0
        
        for account in customer_accounts:
            # Get transactions for this account
            transactions_queryset = CustomerTransaction.objects.filter(
                customer_account=account
            ).select_related('currency')
            
            # Apply filters
            if transaction_type:
                transactions_queryset = transactions_queryset.filter(transaction_type=transaction_type)
            
            if currency_id:
                transactions_queryset = transactions_queryset.filter(currency_id=currency_id)
            
            if date_from:
                from django.utils.dateparse import parse_datetime
                try:
                    date_from_parsed = parse_datetime(date_from)
                    if date_from_parsed:
                        transactions_queryset = transactions_queryset.filter(created_at__gte=date_from_parsed)
                except ValueError:
                    pass
            
            if date_to:
                from django.utils.dateparse import parse_datetime
                try:
                    date_to_parsed = parse_datetime(date_to)
                    if date_to_parsed:
                        transactions_queryset = transactions_queryset.filter(created_at__lte=date_to_parsed)
                except ValueError:
                    pass
            
            # Order by creation date (newest first)
            transactions_queryset = transactions_queryset.order_by('-created_at')
            
            # Serialize transactions
            transactions_serializer = CustomerTransactionSerializer(
                transactions_queryset, 
                many=True, 
                context={'request': request}
            )
            
            # Get account balances
            balances = CustomerBalance.objects.filter(customer_account=account)
            balances_serializer = CustomerBalanceSerializer(
                balances, 
                many=True, 
                context={'request': request}
            )
            
            # Prepare account data
            account_data = {
                'account_id': account.account_id,
                'account_number': account.account_number,
                'account_type': account.get_account_type_display(),
                'account_type_code': account.account_type,
                'saraf_id': account.saraf_account.saraf_id,
                'saraf_name': account.saraf_account.full_name,
                'saraf_phone': account.saraf_account.email_or_whatsapp_number,
                'customer_name': account.full_name,
                'phone': account.phone,
                'address': account.address,
                'job': account.job,
                'created_at': account.created_at,
                'transaction_count': len(transactions_serializer.data),
                'transactions': transactions_serializer.data,
                'balances': balances_serializer.data
            }
            
            accounts_data.append(account_data)
            total_transactions += len(transactions_serializer.data)
        
        return Response({
            'message': 'All accounts and transactions retrieved successfully',
            'phone': phone,
            'total_accounts': len(accounts_data),
            'total_transactions': total_transactions,
            'accounts': accounts_data
        }, status=status.HTTP_200_OK)