
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from saraf_account.views import CustomTokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    # Saraf account endpoints
    path('api/saraf-social/', include('saraf_social.urls')),
    path('api/saraf/', include('saraf_account.urls')),
    
    # Currency management endpoints
    path('api/currency/', include('currency.urls')),
    
    # Saraf balance endpoints
    path('api/balance/', include('saraf_balance.urls')),
    
    # Transaction endpoints
    path('api/transaction/', include('transaction.urls')),
    
    # Hawala endpoints
    path('api/hawala/', include('hawala.urls')),
    
    # Messaging endpoints
    path('api/messages/', include('msg.urls')),
    
    # OTP endpoints
    path('api/email-otp/', include('email_otp.urls')),
    path('api/phone-otp/', include('phone_otp.urls')),
    path('api/wa-otp/', include('wa_otp.urls')),
    
    # Normal user account endpoints
    path('api/normal-user/', include('normal_user_account.urls')),
    
    # Saraf create accounts endpoints
    path('api/saraf-create-accounts/', include('saraf_create_accounts.urls')),
    
    # Exchange rate endpoints
    path('api/exchange/', include('exchange.urls')),
    
    # Saraf post endpoints
    path('api/saraf-posts/', include('saraf_post.urls')),

    # AI endpoints
    path('api/ai/', include('ai.urls')),

    # User feedback endpoints
    path('api/user-feedback/', include('user_feedback.urls')),

]

# Serve media files during development and production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, you should configure your web server (nginx/apache) to serve media files
    # This is a fallback for development/testing
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
