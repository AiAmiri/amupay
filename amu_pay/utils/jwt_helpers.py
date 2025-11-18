"""
Shared utilities for JWT token handling and user authentication.
This module provides consistent JWT handling across all apps.
"""

from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from saraf_account.models import SarafAccount, SarafEmployee


def get_user_info_from_token(request):
    """
    Extract user information from JWT token.
    
    Args:
        request: Django request object with JWT token
        
    Returns:
        dict: User information dictionary or None if invalid
    """
    try:
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        # Decode JWT token
        from rest_framework_simplejwt.tokens import AccessToken
        access_token = AccessToken(token)
        
        # Extract user information
        user_info = {
            'user_id': access_token.get('user_id'),
            'user_type': access_token.get('user_type'),
            'saraf_id': access_token.get('saraf_id'),
            'employee_id': access_token.get('employee_id'),
            'full_name': access_token.get('full_name'),
            'employee_name': access_token.get('employee_name'),
        }
        
        return user_info
        
    except Exception:
        return None


def require_authentication(view_func):
    """
    Decorator to require JWT authentication for views.
    
    Args:
        view_func: View function to decorate
        
    Returns:
        Decorated view function
    """
    def wrapper(request, *args, **kwargs):
        user_info = get_user_info_from_token(request)
        if not user_info:
            return Response({
                'error': 'Invalid or missing authentication token'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Add user_info to request for use in view
        request.user_info = user_info
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_saraf_permission(permission_name):
    """
    Decorator to require specific saraf permission for views.
    
    Args:
        permission_name (str): Name of permission required
        
    Returns:
        Decorator function
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user_info = get_user_info_from_token(request)
            if not user_info:
                return Response({
                    'error': 'Invalid or missing authentication token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user has saraf_id
            if not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get saraf account
            try:
                saraf_account = SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
            except SarafAccount.DoesNotExist:
                return Response({
                    'error': 'Saraf account not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check permission for employees
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission(permission_name):
                        return Response({
                            'error': f'You do not have permission to {permission_name}'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Add user_info and saraf_account to request
            request.user_info = user_info
            request.saraf_account = saraf_account
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def get_saraf_account_from_token(request):
    """
    Get saraf account from JWT token.
    
    Args:
        request: Django request object with JWT token
        
    Returns:
        SarafAccount: Saraf account object or None if invalid
    """
    user_info = get_user_info_from_token(request)
    if not user_info or not user_info.get('saraf_id'):
        return None
    
    try:
        return SarafAccount.objects.get(saraf_id=user_info['saraf_id'])
    except SarafAccount.DoesNotExist:
        return None


def get_employee_from_token(request):
    """
    Get employee from JWT token.
    
    Args:
        request: Django request object with JWT token
        
    Returns:
        SarafEmployee: Employee object or None if invalid/not employee
    """
    user_info = get_user_info_from_token(request)
    if not user_info or not user_info.get('employee_id'):
        return None
    
    try:
        return SarafEmployee.objects.get(employee_id=user_info['employee_id'])
    except SarafEmployee.DoesNotExist:
        return None


def create_error_response(message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Create standardized error response.
    
    Args:
        message (str): Error message
        details (str): Additional error details
        status_code (int): HTTP status code
        
    Returns:
        Response: Standardized error response
    """
    response_data = {'error': message}
    if details:
        response_data['details'] = details
    
    return Response(response_data, status=status_code)


def create_success_response(message, data=None, status_code=status.HTTP_200_OK):
    """
    Create standardized success response.
    
    Args:
        message (str): Success message
        data (dict): Additional data
        status_code (int): HTTP status code
        
    Returns:
        Response: Standardized success response
    """
    response_data = {'message': message}
    if data:
        response_data.update(data)
    
    return Response(response_data, status=status_code)
