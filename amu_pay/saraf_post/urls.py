from django.urls import path
from .views import (
    SarafPostListView,
    SarafPostCreateView,
    SarafPostDetailView
)

app_name = 'saraf_post'

urlpatterns = [
    # Saraf post management
    path('', SarafPostListView.as_view(), name='post_list'),
    path('create/', SarafPostCreateView.as_view(), name='post_create'),
    path('<int:post_id>/', SarafPostDetailView.as_view(), name='post_detail'),
]
