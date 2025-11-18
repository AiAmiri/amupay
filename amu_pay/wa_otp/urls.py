from django.urls import path
from .views import WhatsAppOTPView, VerifyWhatsAppOTPView

urlpatterns = [
    path('wa-otp/', WhatsAppOTPView.as_view(), name='wa-otp'),
    path('verify-wa-otp/', VerifyWhatsAppOTPView.as_view(), name='verify-wa-otp'),
]
