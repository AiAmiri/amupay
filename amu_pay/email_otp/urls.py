from django.urls import path
from . import views

urlpatterns = [
    path('generate-otp/', views.GenerateOTPView.as_view(), name='generate-otp'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('email-status/', views.EmailStatusView.as_view(), name='email-status'),
]
