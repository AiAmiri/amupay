"""
Custom JWT Authentication for SarafAccount and SarafEmployee
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from .models import SarafAccount, SarafEmployee
from normal_user_account.models import NormalUser


class CustomUser:
    """
    Custom user object to replace Django User for JWT authentication
    """
    def __init__(self, user_data):
        self.id = user_data.get('user_id')
        self.user_id = user_data.get('user_id')
        self.saraf_id = user_data.get('saraf_id')
        self.employee_id = user_data.get('employee_id')
        self.normal_user_id = user_data.get('normal_user_id')  # Add normal_user_id support
        self.user_type = user_data.get('user_type')
        self.full_name = user_data.get('full_name', '')
        self.email = user_data.get('email', '')
        self.username = self.full_name  # Use full_name as username
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        
    def __str__(self):
        return f"{self.full_name} ({self.user_type})"


class SarafJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that works with SarafAccount and SarafEmployee
    """
    
    def get_user(self, validated_token):
        """
        Get user from validated token
        """
        try:
            user_type = validated_token.get('user_type')
            user_id = validated_token.get('user_id')
            saraf_id_raw = validated_token.get('saraf_id')
            
            if not user_type or not user_id:
                raise InvalidToken('Token does not contain required user information')
            
            # Ensure saraf_id is an integer if it exists
            saraf_id = None
            if saraf_id_raw is not None:
                try:
                    # Convert to integer - ensure it's not a string or object
                    if isinstance(saraf_id_raw, int):
                        saraf_id = saraf_id_raw
                    elif isinstance(saraf_id_raw, str):
                        saraf_id = int(saraf_id_raw)
                    else:
                        # If it's something else, try to convert it
                        saraf_id = int(saraf_id_raw)
                except (ValueError, TypeError) as e:
                    raise InvalidToken(f'Invalid saraf_id format in token: {type(saraf_id_raw)} = {saraf_id_raw}')
            
            # Create custom user object with token data
            user_data = {
                'user_id': user_id,
                'saraf_id': saraf_id,  # Now guaranteed to be int or None
                'employee_id': validated_token.get('employee_id'),
                'user_type': user_type,
                'full_name': validated_token.get('full_name', ''),
                'email': validated_token.get('email_or_whatsapp_number', ''),
            }
            
            # Verify the user still exists in database
            if user_type == 'saraf':
                if saraf_id is None:
                    raise InvalidToken('Saraf ID is required in token for saraf user type')
                try:
                    saraf = SarafAccount.objects.get(saraf_id=saraf_id, is_active=True)
                    user_data['full_name'] = saraf.full_name
                    user_data['email'] = saraf.email_or_whatsapp_number
                except SarafAccount.DoesNotExist:
                    raise InvalidToken('Saraf account not found or inactive')
                    
            elif user_type == 'employee':
                # For employees, saraf_id should come from the employee's saraf_account
                employee_id = validated_token.get('employee_id')
                if not employee_id:
                    raise InvalidToken('Employee ID is required in token for employee user type')
                try:
                    employee = SarafEmployee.objects.select_related('saraf_account').get(
                        employee_id=employee_id,
                        is_active=True
                    )
                    # Ensure saraf_id is set from employee's saraf_account
                    if employee.saraf_account:
                        user_data['saraf_id'] = employee.saraf_account.saraf_id
                    user_data['full_name'] = employee.full_name
                    user_data['email'] = employee.saraf_account.email_or_whatsapp_number
                except SarafEmployee.DoesNotExist:
                    raise InvalidToken('Employee not found or inactive')
            elif user_type == 'normal_user':
                try:
                    normal_user = NormalUser.objects.get(user_id=user_id, is_active=True)
                    user_data['full_name'] = normal_user.full_name
                    user_data['email'] = normal_user.email or normal_user.email_or_whatsapp
                    user_data['normal_user_id'] = user_id  # Add this for saraf_social compatibility
                except NormalUser.DoesNotExist:
                    raise InvalidToken('Normal user not found or inactive')
            else:
                raise InvalidToken('Invalid user type in token')
            
            return CustomUser(user_data)
            
        except Exception as e:
            raise InvalidToken(f'Token authentication failed: {str(e)}')
