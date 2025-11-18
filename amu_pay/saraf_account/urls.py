from django.urls import path
from .views import (
    SarafAccountRegisterView,
    SarafAccountProtectedView,
    ChangePasswordView,
    ChangeEmployeePasswordView,
    DeleteAccountView,
    ForgotPasswordRequestView,
    ForgotPasswordOTPVerifyView,
    ResetPasswordConfirmView,
    SarafEmailOTPRequestView,
    SarafEmailOTPVerifyView,
    SarafLoginView,
    SarafLogoutView,
    SarafListView,
    SarafDetailView,
    GetEmployeesView,
    EmployeeManagementView,
    EmployeeMyPermissionsView,
    EmployeePermissionsView,
    BulkEmployeePermissionsView,
    PermissionTemplatesView,
    SarafOTPVerificationView,
    SarafResendOTPView,
    SarafPictureManagementView,
    SarafSinglePictureUpdateView,
)

urlpatterns = [
    path('register/', SarafAccountRegisterView.as_view(), name='saraf_register'),
    path('login/', SarafLoginView.as_view(), name='saraf_login'),
    path('logout/', SarafLogoutView.as_view(), name='saraf_logout'),
    path('list/', SarafListView.as_view(), name='saraf_list'),
    path('<int:saraf_id>/', SarafDetailView.as_view(), name='saraf_detail'),
    path('get-employees/', GetEmployeesView.as_view(), name='get_employees'),
    path('employees/', EmployeeManagementView.as_view(), name='employee_management'),
    
    # Employee Permissions Management
    path('my-permissions/', EmployeeMyPermissionsView.as_view(), name='employee_my_permissions'),
    path('permissions/', EmployeePermissionsView.as_view(), name='permission_defaults'),
    path('permissions/<int:employee_id>/', EmployeePermissionsView.as_view(), name='employee_permissions'),
    path('permissions/bulk/', BulkEmployeePermissionsView.as_view(), name='bulk_employee_permissions'),
    path('permissions/templates/', PermissionTemplatesView.as_view(), name='permission_templates'),
    
    path('protected/', SarafAccountProtectedView.as_view(), name='saraf_protected'),
    path('change-password/', ChangePasswordView.as_view(), name='saraf_change_password'),
    path('employees/<int:employee_id>/change-password/', ChangeEmployeePasswordView.as_view(), name='saraf_change_employee_password'),
    path('delete-account/', DeleteAccountView.as_view(), name='saraf_delete_account'),
    path('forgot-password/', ForgotPasswordRequestView.as_view(), name='saraf_forgot_password'),
    path('forgot-password/otp/verify/', ForgotPasswordOTPVerifyView.as_view(), name='saraf_forgot_password_otp_verify'),
    path('reset-password-confirm/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='saraf_reset_password_confirm'),
    path('email/otp/request/', SarafEmailOTPRequestView.as_view(), name='saraf_email_otp_request'),
    path('email/otp/verify/', SarafEmailOTPVerifyView.as_view(), name='saraf_email_otp_verify'),
    
    # OTP verification endpoints
    path('otp/verify/', SarafOTPVerificationView.as_view(), name='saraf_otp_verify'),
    path('otp/resend/', SarafResendOTPView.as_view(), name='saraf_otp_resend'),
    
    # Picture management endpoints
    path('pictures/', SarafPictureManagementView.as_view(), name='saraf_pictures'),
    path('pictures/<str:picture_field>/', SarafSinglePictureUpdateView.as_view(), name='saraf_single_picture'),
]
