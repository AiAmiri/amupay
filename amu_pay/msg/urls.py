from django.urls import path
from .views import (
    ConversationListView,
    CreateConversationView,
    ConversationDetailView,
    DeleteConversationView,
    SendMessageView,
    MessageStatusView,
    MessageSearchView,
    MessageStatsView,
    InAppNotificationsView,
)
from .normal_user_views import (
    NormalUserConversationListView,
    NormalUserCreateConversationView,
    NormalUserConversationDetailView,
    NormalUserDeleteConversationView,
    NormalUserSendMessageView,
    NormalUserMessageStatusView,
    NormalUserInAppNotificationsView,
)

urlpatterns = [
    # Saraf Account Conversation management
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('conversations/create/', CreateConversationView.as_view(), name='create_conversation'),
    path('conversations/<int:conversation_id>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('conversations/<int:conversation_id>/delete/', DeleteConversationView.as_view(), name='delete_conversation'),
    
    # Saraf Account Message management
    path('messages/send/', SendMessageView.as_view(), name='send_message'),
    path('messages/<int:message_id>/status/', MessageStatusView.as_view(), name='message_status'),
    
    # Saraf Account Search and statistics
    path('messages/search/', MessageSearchView.as_view(), name='message_search'),
    path('messages/stats/', MessageStatsView.as_view(), name='message_stats'),
    
    # Saraf Account In-app notifications
    path('notifications/', InAppNotificationsView.as_view(), name='in_app_notifications'),
    path('notifications/<int:notification_id>/', InAppNotificationsView.as_view(), name='mark_notification_read'),
    
    # Normal User Conversation management
    path('normal-user/conversations/', NormalUserConversationListView.as_view(), name='normal_user_conversation_list'),
    path('normal-user/conversations/create/', NormalUserCreateConversationView.as_view(), name='normal_user_create_conversation'),
    path('normal-user/conversations/<int:conversation_id>/', NormalUserConversationDetailView.as_view(), name='normal_user_conversation_detail'),
    path('normal-user/conversations/<int:conversation_id>/delete/', NormalUserDeleteConversationView.as_view(), name='normal_user_delete_conversation'),
    
    # Normal User Message management
    path('normal-user/messages/send/', NormalUserSendMessageView.as_view(), name='normal_user_send_message'),
    path('normal-user/messages/<int:message_id>/status/', NormalUserMessageStatusView.as_view(), name='normal_user_message_status'),
    
    # Normal User In-app notifications
    path('normal-user/notifications/', NormalUserInAppNotificationsView.as_view(), name='normal_user_in_app_notifications'),
    path('normal-user/notifications/<int:notification_id>/', NormalUserInAppNotificationsView.as_view(), name='normal_user_mark_notification_read'),
]
