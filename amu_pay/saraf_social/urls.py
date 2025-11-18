from django.urls import path
from .views import (
    LikeSarafView,
    CreateCommentView,
    DeleteCommentView,
    CommentListView,
    PublicSarafStatsView,
    SarafStatsListView,
    UserLikesView,
    UserCommentsView,
)

urlpatterns = [
    # Normal User Actions (Authentication Required)
    path('like/', LikeSarafView.as_view(), name='like_saraf'),
    path('comment/create/', CreateCommentView.as_view(), name='create_comment'),
    path('comment/<int:comment_id>/delete/', DeleteCommentView.as_view(), name='delete_comment'),
    path('user/likes/', UserLikesView.as_view(), name='user_likes'),
    path('user/comments/', UserCommentsView.as_view(), name='user_comments'),
    
    # Public Endpoints (No Authentication Required)
    path('saraf/<str:saraf_id>/stats/', PublicSarafStatsView.as_view(), name='saraf_stats'),
    path('saraf/<str:saraf_id>/comments/', CommentListView.as_view(), name='saraf_comments'),
    path('saraf/stats/', SarafStatsListView.as_view(), name='all_saraf_stats'),
]
