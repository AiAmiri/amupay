from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Currency, SarafSupportedCurrency
from .serializers import (
    CurrencySerializer, 
    SarafSupportedCurrencySerializer,
    SarafSupportedCurrencyListSerializer
)
from saraf_account.models import SarafAccount, SarafEmployee, ActionLog
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


class AvailableCurrenciesView(APIView):
    """
    List of all currencies available in the system
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of all active currencies"""
        try:
            currencies = Currency.objects.filter(is_active=True).order_by('currency_code')
            serializer = CurrencySerializer(currencies, many=True)
            
            return Response({
                'message': 'Available currencies list',
                'currencies': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error getting currency list',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SarafSupportedCurrenciesView(APIView):
    """
    Management of exchange supported currencies
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of exchange supported currencies"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Get supported currencies
            supported_currencies = SarafSupportedCurrency.objects.filter(
                saraf_account=saraf_account,
                is_active=True
            ).select_related('currency')
            
            serializer = SarafSupportedCurrencyListSerializer(supported_currencies, many=True)
            
            return Response({
                'message': 'Supported currencies list',
                'saraf_name': saraf_account.full_name,
                'supported_currencies': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error getting supported currencies',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Add new currency to supported list"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check permission to add currency
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('add_currency'):
                        return Response({
                            'error': 'You do not have permission to add currency'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Data validation
            serializer = SarafSupportedCurrencySerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            currency_code = request.data.get('currency_code', '').upper()
            
            # Check if this currency has already been added
            existing = SarafSupportedCurrency.objects.filter(
                saraf_account=saraf_account,
                currency__currency_code=currency_code
            ).first()
            
            if existing:
                if existing.is_active:
                    return Response({
                        'error': f'Currency {currency_code} has already been added to the list'
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Activate inactive currency
                    existing.is_active = True
                    existing.save()
                    
                    # Log the action
                    ActionLog.objects.create(
                        saraf=saraf_account,
                        user_type='employee' if user_info.get('employee_id') else 'saraf',
                        user_id=user_info.get('employee_id') or saraf_id,
                        user_name=user_info.get('full_name', 'Unknown'),
                        action_type='activate_currency',
                        description=f'Activate currency {currency_code}'
                    )
                    
                    return Response({
                        'message': f'Currency {currency_code} successfully activated',
                        'currency': SarafSupportedCurrencyListSerializer(existing).data
                    }, status=status.HTTP_200_OK)
            
            with transaction.atomic():
                # Create new supported currency
                supported_currency = serializer.save(
                    saraf_account=saraf_account,
                    added_by_saraf=saraf_account if not user_info.get('employee_id') else None,
                    added_by_employee=SarafEmployee.objects.get(employee_id=user_info['employee_id']) if user_info.get('employee_id') else None
                )
                
                # Log the action
                ActionLog.objects.create(
                    saraf=saraf_account,
                    user_type='employee' if user_info.get('employee_id') else 'saraf',
                    user_id=user_info.get('employee_id') or saraf_id,
                    user_name=user_info.get('full_name', 'Unknown'),
                    action_type='add_currency',
                    description=f'Add currency {currency_code}'
                )
                
                return Response({
                    'message': f'Currency {currency_code} successfully added',
                    'currency': SarafSupportedCurrencyListSerializer(supported_currency).data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'error': 'Error adding currency',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        """Remove (deactivate) currency from supported list"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check permission to remove currency
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('add_currency'):  # Same permission for removal
                        return Response({
                            'error': 'You do not have permission to remove currency'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            currency_code = request.data.get('currency_code', '').upper()
            if not currency_code:
                return Response({
                    'error': 'Currency code is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find supported currency
            supported_currency = get_object_or_404(
                SarafSupportedCurrency,
                saraf_account=saraf_account,
                currency__currency_code=currency_code,
                is_active=True
            )
            
            # Deactivate currency
            supported_currency.is_active = False
            supported_currency.save()
            
            # ثبت در لاگ
            ActionLog.objects.create(
                saraf=saraf_account,
                user_type='employee' if user_info.get('employee_id') else 'saraf',
                user_id=user_info.get('employee_id') or saraf_id,
                user_name=user_info.get('full_name', 'Unknown'),
                action_type='remove_currency',
                description=f'Remove currency {currency_code}'
            )
            
            return Response({
                'message': f'Currency {currency_code} successfully removed'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error removing currency',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)