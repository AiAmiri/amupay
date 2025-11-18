from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import logging

from .models import SarafLike, SarafComment, SarafSocialStats
from .serializers import (
    SarafLikeSerializer, 
    SarafCommentSerializer, 
    CreateSarafCommentSerializer,
    SarafSocialStatsSerializer,
    PublicSarafStatsSerializer,
    SarafCommentListSerializer,
    LikeToggleSerializer,
    CommentDeleteSerializer
)
from saraf_account.models import SarafAccount, SarafEmployee
from normal_user_account.models import NormalUser

logger = logging.getLogger(__name__)

def get_user_info_from_token(request):
    """Extract user info from JWT token"""
    try:
        token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        from rest_framework_simplejwt.tokens import AccessToken
        access_token = AccessToken(token)
        return access_token.payload
    except Exception as e:
        logger.error(f"Error extracting user info from token: {e}")
        return {}

class LikeSarafView(APIView):
    """Like a Saraf account (unlike removed)"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get user info from authenticated user (Django's authentication system)
            user = request.user
            
            if not user.is_authenticated:
                return Response({'error': 'Authentication required'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
            
            if user.user_type != 'normal_user':
                return Response({'error': 'Only normal users can like Saraf accounts'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            normal_user_id = user.normal_user_id
            normal_user = get_object_or_404(NormalUser, user_id=normal_user_id)
            
            serializer = LikeToggleSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            saraf_id = serializer.validated_data['saraf_id']
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id, is_active=True)
            
            with transaction.atomic():
                # Check if already liked
                like, created = SarafLike.objects.get_or_create(
                    saraf_account=saraf_account,
                    normal_user=normal_user
                )
                
                if created:
                    # Update stats
                    stats = SarafSocialStats.get_or_create_stats(saraf_account)
                    stats.update_stats()
                    
                    return Response({
                        'message': 'Successfully liked',
                        'liked': True,
                        'saraf_id': saraf_id,
                        'saraf_name': saraf_account.full_name
                    })
                else:
                    return Response({
                        'message': 'Already liked',
                        'liked': True,
                        'saraf_id': saraf_id,
                        'saraf_name': saraf_account.full_name
                    })
            
        except Exception as e:
            logger.error(f"Error in LikeSarafView: {str(e)}")
            return Response({'error': 'Internal server error'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateCommentView(APIView):
    """Create a new comment for a Saraf account"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get user info from authenticated user (Django's authentication system)
            user = request.user
            
            if not user.is_authenticated:
                return Response({'error': 'Authentication required'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
            
            if user.user_type != 'normal_user':
                return Response({'error': 'Only normal users can comment on Saraf accounts'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            normal_user_id = user.normal_user_id
            normal_user = get_object_or_404(NormalUser, user_id=normal_user_id)
            
            serializer = CreateSarafCommentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                comment = serializer.save(normal_user=normal_user)
                
                # Update stats
                stats = SarafSocialStats.get_or_create_stats(comment.saraf_account)
                stats.update_stats()
                
                response_serializer = SarafCommentSerializer(comment)
                return Response({
                    'message': 'Comment created successfully',
                    'comment': response_serializer.data
                }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error in CreateCommentView: {str(e)}")
            return Response({'error': 'Internal server error'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteCommentView(APIView):
    """Delete a comment (normal users can delete their own comments)"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, comment_id):
        try:
            # Get user info from authenticated user (Django's authentication system)
            user = request.user
            
            if not user.is_authenticated:
                return Response({'error': 'Authentication required'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
            
            if user.user_type != 'normal_user':
                return Response({'error': 'Only normal users can delete their comments'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            normal_user_id = user.normal_user_id
            normal_user = get_object_or_404(NormalUser, user_id=normal_user_id)
            
            # Get comment and verify ownership
            comment = get_object_or_404(SarafComment, comment_id=comment_id)
            
            if comment.normal_user != normal_user:
                return Response({'error': 'You can only delete your own comments'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            with transaction.atomic():
                saraf_account = comment.saraf_account
                comment.delete()
                
                # Update stats
                stats = SarafSocialStats.get_or_create_stats(saraf_account)
                stats.update_stats()
                
                return Response({
                    'message': 'Comment deleted successfully',
                    'comment_id': comment_id,
                    'saraf_id': saraf_account.saraf_id,
                    'saraf_name': saraf_account.full_name
                })
            
        except Exception as e:
            logger.error(f"Error in DeleteCommentView: {str(e)}")
            return Response({'error': 'Internal server error'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommentListView(APIView):
    """List comments for a Saraf account (public view)"""
    permission_classes = [AllowAny]
    
    def get(self, request, saraf_id):
        try:
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id, is_active=True)
            
            # Get all comments (no status filtering)
            comments = SarafComment.objects.filter(
                saraf_account=saraf_account
            ).order_by('-created_at')
            
            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 20
            page_obj = paginator.paginate_queryset(comments, request)
            
            serializer = SarafCommentListSerializer(page_obj, many=True)
            
            return Response({
                'saraf_id': saraf_id,
                'saraf_name': saraf_account.full_name,
                'comments': serializer.data,
                'pagination': {
                    'current_page': paginator.page.number,
                    'total_pages': paginator.page.paginator.num_pages,
                    'total_count': paginator.page.paginator.count,
                    'has_next': paginator.page.has_next(),
                    'has_previous': paginator.page.has_previous()
                }
            })
            
        except Exception as e:
            logger.error(f"Error in CommentListView: {str(e)}")
            return Response({'error': 'Internal server error'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PublicSarafStatsView(APIView):
    """Public endpoint to get Saraf statistics"""
    permission_classes = [AllowAny]
    
    def get(self, request, saraf_id):
        try:
            saraf_account = get_object_or_404(SarafAccount, saraf_id=saraf_id, is_active=True)
            
            # Get or create stats
            stats = SarafSocialStats.get_or_create_stats(saraf_account)
            
            serializer = PublicSarafStatsSerializer(stats)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error in PublicSarafStatsView: {str(e)}")
            return Response({'error': 'Internal server error'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SarafStatsListView(APIView):
    """List all Saraf statistics (public)"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            # Get all active Saraf accounts with stats
            stats = SarafSocialStats.objects.filter(
                saraf_account__is_active=True
            ).order_by('-total_likes', '-total_comments')
            
            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 50
            page_obj = paginator.paginate_queryset(stats, request)
            
            serializer = PublicSarafStatsSerializer(page_obj, many=True)
            
            return Response({
                'saraf_stats': serializer.data,
                'pagination': {
                    'current_page': paginator.page.number,
                    'total_pages': paginator.page.paginator.num_pages,
                    'total_count': paginator.page.paginator.count,
                    'has_next': paginator.page.has_next(),
                    'has_previous': paginator.page.has_previous()
                }
            })
            
        except Exception as e:
            logger.error(f"Error in SarafStatsListView: {str(e)}")
            return Response({'error': 'Internal server error'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserLikesView(APIView):
    """Get likes given by a normal user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get user info from authenticated user (Django's authentication system)
            user = request.user
            
            if not user.is_authenticated:
                return Response({'error': 'Authentication required'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
            
            if user.user_type != 'normal_user':
                return Response({'error': 'Only normal users can view their likes'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            normal_user_id = user.normal_user_id
            normal_user = get_object_or_404(NormalUser, user_id=normal_user_id)
            
            likes = SarafLike.objects.filter(normal_user=normal_user).order_by('-created_at')
            
            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 20
            page_obj = paginator.paginate_queryset(likes, request)
            
            serializer = SarafLikeSerializer(page_obj, many=True)
            
            return Response({
                'user_likes': serializer.data,
                'pagination': {
                    'current_page': paginator.page.number,
                    'total_pages': paginator.page.paginator.num_pages,
                    'total_count': paginator.page.paginator.count,
                    'has_next': paginator.page.has_next(),
                    'has_previous': paginator.page.has_previous()
                }
            })
            
        except Exception as e:
            logger.error(f"Error in UserLikesView: {str(e)}")
            return Response({'error': 'Internal server error'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserCommentsView(APIView):
    """Get comments made by a normal user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get user info from authenticated user (Django's authentication system)
            user = request.user
            
            if not user.is_authenticated:
                return Response({'error': 'Authentication required'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
            
            if user.user_type != 'normal_user':
                return Response({'error': 'Only normal users can view their comments'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            normal_user_id = user.normal_user_id
            normal_user = get_object_or_404(NormalUser, user_id=normal_user_id)
            
            comments = SarafComment.objects.filter(normal_user=normal_user).order_by('-created_at')
            
            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 20
            page_obj = paginator.paginate_queryset(comments, request)
            
            serializer = SarafCommentSerializer(page_obj, many=True)
            
            return Response({
                'user_comments': serializer.data,
                'pagination': {
                    'current_page': paginator.page.number,
                    'total_pages': paginator.page.paginator.num_pages,
                    'total_count': paginator.page.paginator.count,
                    'has_next': paginator.page.has_next(),
                    'has_previous': paginator.page.has_previous()
                }
            })
            
        except Exception as e:
            logger.error(f"Error in UserCommentsView: {str(e)}")
            return Response({'error': 'Internal server error'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)