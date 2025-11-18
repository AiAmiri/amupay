from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.files.storage import default_storage
import logging

from .models import SarafPost
from .serializers import (
    SarafPostSerializer,
    SarafPostCreateSerializer,
    SarafPostListSerializer,
    SarafPostUpdateSerializer,
    SarafPostDetailSerializer
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


class SarafPostListView(APIView):
    """
    List and filter saraf posts (Public endpoint)
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get list of saraf posts with filters (Public endpoint)"""
        try:
            # Get query parameters for filtering
            title_search = request.query_params.get('title', '')
            content_search = request.query_params.get('content', '')
            created_by = request.query_params.get('created_by', '')
            saraf_id = request.query_params.get('saraf_id', '')
            
            # Time filters
            start_date = request.query_params.get('start_date', '')
            end_date = request.query_params.get('end_date', '')
            
            # Build query - show all posts (public endpoint)
            query = Q()
            
            # Title search
            if title_search:
                query &= Q(title__icontains=title_search)
            
            # Content search
            if content_search:
                query &= Q(content__icontains=content_search)
            
            # Created by filter
            if created_by:
                query &= (
                    Q(created_by_saraf__full_name__icontains=created_by) |
                    Q(created_by_employee__full_name__icontains=created_by)
                )
            
            # Saraf ID filter
            if saraf_id:
                try:
                    saraf_id_int = int(saraf_id)
                    query &= Q(saraf_account__saraf_id=saraf_id_int)
                except ValueError:
                    return Response({
                        'error': 'Invalid saraf_id format. Must be a number.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Date range filter
            if start_date:
                try:
                    from datetime import datetime
                    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                    query &= Q(created_at__gte=start_datetime)
                except ValueError:
                    return Response({
                        'error': 'Invalid start_date format. Use YYYY-MM-DD'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if end_date:
                try:
                    from datetime import datetime
                    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                    # Add one day to include the entire end date
                    end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
                    query &= Q(created_at__lte=end_datetime)
                except ValueError:
                    return Response({
                        'error': 'Invalid end_date format. Use YYYY-MM-DD'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get posts
            posts = SarafPost.objects.filter(query).select_related(
                'saraf_account',
                'created_by_saraf',
                'created_by_employee'
            ).order_by('-published_at', '-created_at')
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            total_count = posts.count()
            posts_page = posts[start_index:end_index]
            
            serializer = SarafPostListSerializer(posts_page, many=True)
            
            return Response({
                'message': 'Saraf posts list (Public)',
                'posts': serializer.data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting saraf posts: {str(e)}")
            return Response({
                'error': 'Error getting saraf posts',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SarafPostCreateView(APIView):
    """
    Create new saraf post
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create new saraf post"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check permission to create post
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('add_posts'):
                        return Response({
                            'error': 'You do not have permission to create posts'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Data validation
            serializer = SarafPostCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # Create new post
                post = serializer.save(
                    saraf_account=saraf_account,
                    created_by_saraf=saraf_account if not user_info.get('employee_id') else None,
                    created_by_employee=SarafEmployee.objects.get(employee_id=user_info['employee_id']) if user_info.get('employee_id') else None
                )
                
                # Log the action
                ActionLog.objects.create(
                    saraf=saraf_account,
                    user_type='employee' if user_info.get('employee_id') else 'saraf',
                    user_id=user_info.get('employee_id') or saraf_id,
                    user_name=user_info.get('full_name', 'Unknown'),
                    action_type='create_post',
                    description=f'Create post: {post.title}'
                )
                
                # Return created post
                response_serializer = SarafPostDetailSerializer(post)
                
                return Response({
                    'message': 'Post created successfully',
                    'post': response_serializer.data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error creating saraf post: {str(e)}")
            return Response({
                'error': 'Error creating saraf post',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SarafPostDetailView(APIView):
    """
    Retrieve, update or delete saraf post
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, post_id):
        """Get specific saraf post"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Get post
            post = get_object_or_404(
                SarafPost,
                id=post_id,
                saraf_account=saraf_account
            )
            
            serializer = SarafPostDetailSerializer(post)
            
            return Response({
                'message': 'Post details',
                'post': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting saraf post: {str(e)}")
            return Response({
                'error': 'Error getting saraf post',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, post_id):
        """Update saraf post"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check permission to update post
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('add_posts'):
                        return Response({
                            'error': 'You do not have permission to update posts'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Get post
            post = get_object_or_404(
                SarafPost,
                id=post_id,
                saraf_account=saraf_account
            )
            
            # Data validation
            serializer = SarafPostUpdateSerializer(post, data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # Update post
                updated_post = serializer.save()
                
                # Log the action
                ActionLog.objects.create(
                    saraf=saraf_account,
                    user_type='employee' if user_info.get('employee_id') else 'saraf',
                    user_id=user_info.get('employee_id') or saraf_id,
                    user_name=user_info.get('full_name', 'Unknown'),
                    action_type='update_post',
                    description=f'Update post: {updated_post.title}'
                )
                
                # Return updated post
                response_serializer = SarafPostDetailSerializer(updated_post)
                
                return Response({
                    'message': 'Post updated successfully',
                    'post': response_serializer.data
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error updating saraf post: {str(e)}")
            return Response({
                'error': 'Error updating saraf post',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, post_id):
        """Delete saraf post"""
        try:
            # Get user information from token
            user_info = get_user_info_from_token(request)
            if not user_info or not user_info.get('saraf_id'):
                return Response({
                    'error': 'Invalid user information'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            saraf_id = user_info['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id)
            
            # Check permission to delete post
            if user_info.get('employee_id'):
                try:
                    employee = SarafEmployee.objects.get(employee_id=user_info['employee_id'])
                    if not employee.has_permission('add_posts'):
                        return Response({
                            'error': 'You do not have permission to delete posts'
                        }, status=status.HTTP_403_FORBIDDEN)
                except SarafEmployee.DoesNotExist:
                    return Response({
                        'error': 'Employee not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Get post
            post = get_object_or_404(
                SarafPost,
                id=post_id,
                saraf_account=saraf_account
            )
            
            with transaction.atomic():
                # Log the action before deletion
                ActionLog.objects.create(
                    saraf=saraf_account,
                    user_type='employee' if user_info.get('employee_id') else 'saraf',
                    user_id=user_info.get('employee_id') or saraf_id,
                    user_name=user_info.get('full_name', 'Unknown'),
                    action_type='delete_post',
                    description=f'Delete post: {post.title}'
                )
                
                # Delete post photo if exists
                if post.photo:
                    try:
                        default_storage.delete(post.photo.name)
                    except Exception as e:
                        logger.warning(f"Could not delete photo file: {str(e)}")
                
                # Delete post
                post.delete()
                
                return Response({
                    'message': 'Post deleted successfully'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error deleting saraf post: {str(e)}")
            return Response({
                'error': 'Error deleting saraf post',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)