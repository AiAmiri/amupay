from django.urls import path
from .views import GeneratePhoneOTPView, VerifyPhoneOTPView, PhoneStatusView
from .integrated_views import CombinedOTPGenerateView, CombinedOTPVerifyView, CombinedStatusView

urlpatterns = [
    path('generate-otp/', GeneratePhoneOTPView.as_view(), name='generate_phone_otp'),
    path('verify-otp/', VerifyPhoneOTPView.as_view(), name='verify_phone_otp'),
    path('phone-status/', PhoneStatusView.as_view(), name='phone_status'),
    
    # Integrated OTP endpoints (combines email and phone)
    path('combined/generate-otp/', CombinedOTPGenerateView.as_view(), name='combined_generate_otp'),
    path('combined/verify-otp/', CombinedOTPVerifyView.as_view(), name='combined_verify_otp'),
    path('combined/status/', CombinedStatusView.as_view(), name='combined_status'),
]
