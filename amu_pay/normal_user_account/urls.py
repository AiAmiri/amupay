from django.urls import path
from . import views

app_name = 'normal_user_account'

urlpatterns = [
    # Registration and verification
    path('register/', views.NormalUserRegistrationView.as_view(), name='register'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend_otp'),
    
    # Authentication
    path('login/', views.NormalUserLoginView.as_view(), name='login'),
    path('logout/', views.NormalUserLogoutView.as_view(), name='logout'),
    
    # Password management (3-step process like Saraf)
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('forgot-password/otp/verify/', views.ForgotPasswordOTPVerifyView.as_view(), name='forgot_password_otp_verify'),
    path('reset-password-confirm/<str:uidb64>/<str:token>/', views.ResetPasswordView.as_view(), name='reset_password'),
    
    # Profile
    path('profile/', views.NormalUserProfileView.as_view(), name='profile'),
]
