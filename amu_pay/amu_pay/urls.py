
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from saraf_account.views import CustomTokenRefreshView
from django.http import JsonResponse
import os

# Temporary debug view to inspect storage backend and env vars

def debug_s3(request):
    from django.core.files.storage import default_storage
    from django.utils.module_loading import import_string
    error = None
    try:
        cls_path = settings.DEFAULT_FILE_STORAGE
        cls = import_string(cls_path)
        _ = cls()  # instantiate to trigger any S3 errors
    except Exception as e:
        error = str(e)

    data = {
        "DEFAULT_FILE_STORAGE": settings.DEFAULT_FILE_STORAGE,
        "storage_class": str(default_storage.__class__),
        "USE_S3_env": os.getenv("USE_S3"),
        "AWS_STORAGE_BUCKET_NAME_env": os.getenv("AWS_STORAGE_BUCKET_NAME"),
        "media_storage_error": error,
    }
    return JsonResponse(data)


urlpatterns = [
    # Debug endpoint (remove in production)
    path('debug-s3/', debug_s3),
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

# Serve static and media files during development
if settings.DEBUG:
    # Serve static files (CSS, JS, images) in development
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    # Serve media files (user uploads) in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, static files are served by WhiteNoise or nginx
    # Media files should be served by nginx or S3
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
