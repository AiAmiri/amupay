# 🏦 **Saraf Account App**

A comprehensive business account management system for AMU Pay that enables Saraf (money exchange) businesses to register, manage employees, and operate with advanced permission controls and OTP-based verification.

## 🎯 **Overview**

The Saraf Account app provides a complete business management solution with:
- **Business Registration**: Saraf account registration with license validation
- **Employee Management**: Multi-employee system with granular permissions
- **OTP Verification**: Email and WhatsApp OTP verification via Twilio
- **Permission System**: 20+ granular permissions for employee access control
- **Document Management**: File uploads for business documents and logos
- **Security Features**: Strong password requirements and account verification

## 🏗️ **Architecture**

### **Models**

#### **SarafAccount**
- **Purpose**: Represents a Saraf (money exchange) business account
- **Contact Methods**: Email OR WhatsApp number (one required)
- **Business Info**: Exchange name, license number, address, province
- **Documents**: Logo, wallpaper, ID cards (front/back)
- **Security**: Password hashing, verification status tracking

#### **SarafEmployee**
- **Purpose**: Employee accounts under Saraf businesses
- **Permissions**: Granular permission system with 20+ permissions
- **Security**: Individual passwords and login tracking
- **Management**: Employee creation, permission management, status control

#### **SarafOTP**
- **Purpose**: OTP verification codes for Saraf accounts
- **Types**: `email`, `whatsapp`, `password_reset`
- **Features**: Expiration tracking, usage validation, secure generation

#### **RegistrationCode**
- **Purpose**: Pre-generated codes for Saraf account registration
- **Security**: One-time use codes with validation
- **Management**: Admin-controlled code generation and usage tracking

#### **ActionLog**
- **Purpose**: Audit trail for all Saraf account activities
- **Tracking**: User actions, IP addresses, timestamps
- **Security**: Complete activity logging for compliance

### **Key Features**

#### **🔐 Authentication & Security**
- **Password Requirements**: Minimum 6 characters with uppercase, lowercase, digit, and special character
- **OTP Verification**: 6-digit codes with 10-minute expiration
- **JWT Tokens**: Custom token generation with Saraf-specific claims
- **Account Security**: Password hashing, verification status tracking
- **Registration Codes**: Pre-approved registration system

#### **👥 Employee Management**
- **Multi-Employee Support**: Unlimited employees per Saraf account
- **Granular Permissions**: 20+ specific permissions for fine-grained control
- **Permission Templates**: Default permission sets for different roles
- **Bulk Management**: Bulk permission updates and employee management
- **Individual Logins**: Separate login credentials for each employee

#### **📱 Contact Management**
- **Email Support**: Full email validation and verification
- **WhatsApp Support**: Iranian phone number validation (0XXXXXXXXX)
- **Flexible Registration**: Either email OR WhatsApp (not both required)
- **Contact Normalization**: Automatic phone number formatting

#### **🔄 OTP System**
- **Email OTP**: Professional email templates with OTP codes
- **WhatsApp OTP**: Twilio integration for WhatsApp delivery
- **Password Reset OTP**: Secure password reset flow
- **Resend Functionality**: OTP resending with expiration handling

#### **📄 Document Management**
- **Business Documents**: Logo, wallpaper, ID cards
- **File Uploads**: Secure file storage with validation
- **Image Processing**: Automatic image handling and storage
- **Document Verification**: Admin review of uploaded documents

#### **🔒 Permission System**
- **20+ Permissions**: Comprehensive permission system including:
  - `edit_profile`: Edit Saraf profile
  - `chat`: Access messaging system
  - `send_transfer`: Send money transfers
  - `receive_transfer`: Receive money transfers
  - `take_money`: Take money from customers
  - `give_money`: Give money to customers
  - `loans`: Manage loan operations
  - `add_employee`: Add new employees
  - `change_password`: Change passwords
  - `see_how_did_works`: View operation history
  - `create_exchange`: Create exchange operations
  - `view_history`: View transaction history
  - `create_accounts`: Create customer accounts
  - `delete_accounts`: Delete customer accounts
  - `add_posts`: Add posts/announcements
  - `deliver_amount`: Deliver money amounts
  - `withdraw_to_customer`: Withdraw to customer accounts
  - `deposit_to_customer`: Deposit to customer accounts
  - `withdraw_from_account`: Withdraw from business account
  - `deposit_to_account`: Deposit to business account
  - `add_currency`: Add new currencies

## 🚀 **API Endpoints**

### **Registration & Authentication**
```http
POST   /api/saraf/register/                    # Register new Saraf account
POST   /api/saraf/login/                      # Saraf account login
POST   /api/saraf/logout/                     # Logout
```

### **OTP Verification**
```http
POST   /api/saraf/otp/verify/                 # Verify OTP code
POST   /api/saraf/otp/resend/                 # Resend OTP code
```

### **Account Management**
```http
GET    /api/saraf/list/                       # List Saraf accounts
GET    /api/saraf/protected/                  # Get protected account info
POST   /api/saraf/change-password/            # Change password
DELETE /api/saraf/delete-account/              # Delete account
```

### **Password Management**
```http
POST   /api/saraf/forgot-password/            # Request password reset OTP
POST   /api/saraf/forgot-password/otp/verify/ # Verify password reset OTP
GET    /api/saraf/reset-password-confirm/<uidb64>/<token>/ # Reset password
```

### **Employee Management**
```http
GET    /api/saraf/get-employees/               # Get employees list
POST   /api/saraf/employees/                   # Create employee
PUT    /api/saraf/employees/<id>/              # Update employee
DELETE /api/saraf/employees/<id>/              # Delete employee
POST   /api/saraf/employees/<id>/change-password/ # Change employee password
```

### **Permission Management**
```http
GET    /api/saraf/permissions/                 # Get default permissions
GET    /api/saraf/permissions/<employee_id>/    # Get employee permissions
PUT    /api/saraf/permissions/<employee_id>/    # Update employee permissions
POST   /api/saraf/permissions/bulk/             # Bulk update permissions
GET    /api/saraf/permissions/templates/        # Get permission templates
```

### **Email OTP (Legacy)**
```http
POST   /api/saraf/email/otp/request/           # Request email OTP
POST   /api/saraf/email/otp/verify/            # Verify email OTP
```

## 📋 **Usage Examples**

### **1. Register Saraf Account**

```bash
curl -X POST "http://localhost:8000/api/saraf/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "ABC Exchange",
    "exchange_name": "ABC Money Exchange",
    "email_or_whatsapp_number": "abc@example.com",
    "license_no": "LIC123456",
    "amu_pay_code": "ABC123",
    "saraf_address": "123 Main Street",
    "province": "Kabul",
    "password": "SecurePass123!",
    "repeat_password": "SecurePass123!",
    "registration_code": "ABCD1234EFGH"
  }'
```

**Response:**
```json
{
    "message": "Account created successfully. Please check your email for OTP verification.",
    "saraf_id": 1,
    "contact_info": "abc@example.com",
    "otp_type": "email",
    "otp_sent": true,
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **2. Register with WhatsApp**

```bash
curl -X POST "http://localhost:8000/api/saraf/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "XYZ Exchange",
    "exchange_name": "XYZ Money Exchange",
    "email_or_whatsapp_number": "0791234567",
    "license_no": "LIC789012",
    "amu_pay_code": "XYZ456",
    "saraf_address": "456 Oak Street",
    "province": "Herat",
    "password": "SecurePass123!",
    "repeat_password": "SecurePass123!",
    "registration_code": "WXYZ5678IJKL"
  }'
```

**Response:**
```json
{
    "message": "Account created successfully. Please check your WhatsApp for OTP verification.",
    "saraf_id": 2,
    "contact_info": "0791234567",
    "otp_type": "whatsapp",
    "otp_sent": true,
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **3. Verify OTP**

```bash
curl -X POST "http://localhost:8000/api/saraf/otp/verify/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_whatsapp_number": "abc@example.com",
    "otp_code": "123456"
  }'
```

**Response:**
```json
{
    "message": "OTP verified successfully",
    "saraf_id": 1,
    "verified": true
}
```

### **4. Login**

```bash
curl -X POST "http://localhost:8000/api/saraf/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_whatsapp_number": "abc@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
    "message": "Login successful",
    "user_type": "saraf",
    "user_id": 1,
    "full_name": "ABC Exchange",
    "exchange_name": "ABC Money Exchange",
    "email_or_whatsapp_number": "abc@example.com",
    "is_verified": true,
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **5. Create Employee**

```bash
curl -X POST "http://localhost:8000/api/saraf/employees/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "full_name": "John Doe",
    "password": "EmployeePass123!",
    "repeat_password": "EmployeePass123!"
  }'
```

**Response:**
```json
{
    "message": "Employee created successfully",
    "employee_id": 1,
    "username": "john_doe",
    "full_name": "John Doe",
    "permissions": {
        "edit_profile": false,
        "chat": true,
        "send_transfer": true,
        "receive_transfer": true,
        "take_money": false,
        "give_money": false,
        "loans": false,
        "add_employee": false,
        "change_password": false,
        "see_how_did_works": true,
        "create_exchange": false,
        "view_history": true,
        "create_accounts": false,
        "delete_accounts": false,
        "add_posts": false,
        "deliver_amount": true,
        "withdraw_to_customer": true,
        "deposit_to_customer": true,
        "withdraw_from_account": false,
        "deposit_to_account": true,
        "add_currency": false
    }
}
```

### **6. Update Employee Permissions**

```bash
curl -X PUT "http://localhost:8000/api/saraf/permissions/1/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "permissions": {
        "take_money": true,
        "give_money": true,
        "loans": true,
        "add_employee": true
    }
  }'
```

**Response:**
```json
{
    "message": "Employee permissions updated successfully",
    "employee_id": 1,
    "updated_permissions": {
        "take_money": true,
        "give_money": true,
        "loans": true,
        "add_employee": true
    }
}
```

### **7. Bulk Update Permissions**

```bash
curl -X POST "http://localhost:8000/api/saraf/permissions/bulk/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_ids": [1, 2, 3],
    "permissions": {
        "send_transfer": true,
        "receive_transfer": true,
        "view_history": true
    }
  }'
```

**Response:**
```json
{
    "message": "Bulk permissions updated successfully",
    "updated_employees": 3,
    "permissions": {
        "send_transfer": true,
        "receive_transfer": true,
        "view_history": true
    }
}
```

### **8. Get Employee List**

```bash
curl -X GET "http://localhost:8000/api/saraf/get-employees/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
    "employees": [
        {
            "employee_id": 1,
            "username": "john_doe",
            "full_name": "John Doe",
            "is_active": true,
            "created_at": "2024-01-01T10:00:00Z",
            "last_login": "2024-01-01T10:30:00Z",
            "permissions": {...}
        }
    ],
    "total_count": 1
}
```

### **8.5. Change Employee Password**

```bash
curl -X POST "http://localhost:8000/api/saraf/employees/1/change-password/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "new_password": "NewSecurePass123!",
    "repeat_password": "NewSecurePass123!"
  }'
```

**Response:**
```json
{
    "message": "Employee password changed successfully.",
    "employee": {
        "employee_id": 1,
        "username": "john_doe",
        "full_name": "John Doe"
    }
}
```

**Note:** This endpoint allows Saraf owners to change employee passwords without requiring the current password. Only the Saraf owner can change passwords for their own employees.

### **9. Forgot Password**

```bash
curl -X POST "http://localhost:8000/api/saraf/forgot-password/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_whatsapp_number": "abc@example.com"
  }'
```

**Response:**
```json
{
    "message": "Password reset OTP sent to your email."
}
```

### **10. Reset Password**

```bash
curl -X POST "http://localhost:8000/api/saraf/reset-password-confirm/uidb64/token/" \
  -H "Content-Type: application/json" \
  -d '{
    "new_password": "NewSecurePass123!",
    "repeat_password": "NewSecurePass123!"
  }'
```

**Response:**
```json
{
    "message": "Password reset successful. You can now login with your new password."
}
```

### **11. Resend OTP**

```bash
curl -X POST "http://localhost:8000/api/saraf/otp/resend/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_whatsapp_number": "abc@example.com"
  }'
```

**Response:**
```json
{
    "message": "OTP resent successfully",
    "contact_info": "abc@example.com",
    "otp_type": "email"
}
```

### **12. Get Saraf List**

```bash
curl -X GET "http://localhost:8000/api/saraf/list/"
```

**Response:**
```json
{
    "saraf_accounts": [
        {
            "saraf_id": 1,
            "exchange_name": "ABC Money Exchange",
            "province": "Kabul",
            "saraf_logo": "http://localhost:8000/media/saraf_photos/logo1.jpg"
        }
    ],
    "total_count": 1
}
```

## 🔧 **Configuration**

### **Password Requirements**
- **Minimum Length**: 6 characters
- **Uppercase Letter**: At least one (A-Z)
- **Lowercase Letter**: At least one (a-z)
- **Digit**: At least one (0-9)
- **Special Character**: At least one (!@#$%^&*(),.?":{}|<>)

### **OTP Settings**
- **Code Length**: 6 digits
- **Expiration Time**: 10 minutes
- **Generation**: Cryptographically secure random generation
- **Usage**: Single-use codes (marked as used after verification)

### **Contact Validation**
- **Email**: Standard email format validation
- **WhatsApp**: Iranian phone number format (0XXXXXXXXX)
- **Normalization**: Automatic phone number formatting
- **Uniqueness**: Each contact method must be unique across all Saraf accounts

### **Permission System**
- **Default Permissions**: 20+ permissions with default values
- **Permission Templates**: Pre-defined permission sets for different roles
- **Bulk Operations**: Bulk permission updates for multiple employees
- **Individual Control**: Fine-grained permission control per employee

### **Registration Codes**
- **Pre-generated Codes**: Admin-controlled registration codes
- **One-time Use**: Each code can only be used once
- **Validation**: Code validation during registration
- **Usage Tracking**: Complete tracking of code usage

## 🔐 **Security Features**

### **Password Security**
- **Hashing**: Django's built-in password hashing
- **Validation**: Strong password requirements
- **Reset Security**: OTP-based password reset (no email links)

### **OTP Security**
- **Secure Generation**: Cryptographically secure random codes
- **Expiration**: Time-limited codes (10 minutes)
- **Single Use**: Codes marked as used after verification
- **Rate Limiting**: Previous OTPs invalidated when new ones are generated

### **Account Security**
- **Verification Required**: Account activation through OTP verification
- **Contact Validation**: Email and phone number format validation
- **Account Status**: Active/inactive account management
- **Login Tracking**: Last login timestamp for security monitoring

### **Permission Security**
- **Granular Control**: 20+ specific permissions
- **Default Values**: Secure default permission settings
- **Bulk Management**: Efficient permission management
- **Audit Trail**: Complete permission change logging

### **Data Privacy**
- **Password Storage**: Never stored in plain text
- **Contact Information**: Secure storage with proper validation
- **OTP Storage**: Temporary storage with automatic expiration
- **Token Security**: Secure JWT token generation and validation
- **Action Logging**: Complete audit trail for all activities

## 📊 **Database Schema**

### **SarafAccount Table**
```sql
CREATE TABLE saraf_account_sarafaccount (
    saraf_id BIGINT PRIMARY KEY,
    full_name VARCHAR(128) NOT NULL,
    exchange_name VARCHAR(128) NULL,
    email_or_whatsapp_number VARCHAR(128) UNIQUE NULL,
    license_no VARCHAR(64) UNIQUE NOT NULL,
    amu_pay_code VARCHAR(32) NOT NULL,
    saraf_address VARCHAR(255) DEFAULT '',
    province VARCHAR(64) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_email_verified BOOLEAN DEFAULT FALSE,
    is_whatsapp_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    saraf_logo VARCHAR(100) NULL,
    saraf_logo_wallpeper VARCHAR(100) NULL,
    front_id_card VARCHAR(100) NULL,
    back_id_card VARCHAR(100) NULL
);
```

### **SarafEmployee Table**
```sql
CREATE TABLE saraf_account_sarafemployee (
    employee_id BIGINT PRIMARY KEY,
    saraf_account_id BIGINT REFERENCES saraf_account_sarafaccount(saraf_id),
    username VARCHAR(64) NOT NULL,
    full_name VARCHAR(128) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    permissions JSON NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    UNIQUE(saraf_account_id, username)
);
```

### **SarafOTP Table**
```sql
CREATE TABLE saraf_account_sarafotp (
    otp_id BIGINT PRIMARY KEY,
    saraf_account_id BIGINT REFERENCES saraf_account_sarafaccount(saraf_id),
    otp_type VARCHAR(20) NOT NULL,
    contact_info VARCHAR(128) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP NULL
);
```

### **RegistrationCode Table**
```sql
CREATE TABLE saraf_account_registrationcode (
    code_id BIGINT PRIMARY KEY,
    code VARCHAR(32) UNIQUE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    used_by_saraf_id BIGINT REFERENCES saraf_account_sarafaccount(saraf_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP NULL
);
```

### **ActionLog Table**
```sql
CREATE TABLE saraf_account_actionlog (
    log_id BIGINT PRIMARY KEY,
    saraf_id BIGINT REFERENCES saraf_account_sarafaccount(saraf_id),
    user_type VARCHAR(20) NOT NULL,
    user_id BIGINT NOT NULL,
    user_name VARCHAR(128) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT NOT NULL,
    metadata JSON NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚨 **Error Handling**

### **Common Error Responses**

#### **Validation Errors**
```json
{
    "email_or_whatsapp_number": ["Email or WhatsApp number is required"],
    "password": ["Password must contain at least one uppercase letter"],
    "repeat_password": ["Passwords do not match"],
    "registration_code": ["Invalid or already used registration code"]
}
```

#### **Authentication Errors**
```json
{
    "email_or_whatsapp_number": ["Invalid email/WhatsApp or password"]
}
```

#### **OTP Errors**
```json
{
    "otp_code": ["Invalid OTP code"],
    "non_field_errors": ["OTP has expired"]
}
```

#### **Account Errors**
```json
{
    "email_or_whatsapp_number": ["An account with this email already exists"],
    "license_no": ["License number already exists"],
    "non_field_errors": ["Account is deactivated"]
}
```

#### **Permission Errors**
```json
{
    "permissions": ["Invalid permission: invalid_permission_name"],
    "non_field_errors": ["You do not have permission to perform this action"]
}
```

#### **Employee Password Change Errors**
```json
{
    "error": "new_password and repeat_password are required."
}
```
```json
{
    "error": "Passwords do not match."
}
```
```json
{
    "error": "Only Saraf owners can change employee passwords."
}
```
```json
{
    "error": "You can only change passwords for your own employees."
}
```
```json
{
    "error": "Password must contain at least one uppercase letter."
}
```
```json
{
    "error": "Employee not found."
}
```

#### **Not Found Errors**
```json
{
    "email_or_whatsapp_number": ["No account found with this email/WhatsApp number"]
}
```

## 🔄 **Integration Points**

### **Email Integration**
- **Django Email Backend**: Uses Django's built-in email system
- **Professional Templates**: Business-focused email templates for OTP delivery
- **SMTP Configuration**: Configurable SMTP settings for production

### **WhatsApp Integration**
- **Twilio API**: Twilio WhatsApp Business API integration
- **Iranian Numbers**: Specialized support for Iranian phone number format
- **Content Templates**: Pre-approved WhatsApp message templates

### **JWT Integration**
- **Custom Token Generation**: Manual JWT token creation with Saraf-specific claims
- **Token Validation**: Custom token validation for API requests
- **Refresh Token Support**: Long-lived refresh tokens for session management

### **File Storage Integration**
- **Document Uploads**: Secure file storage for business documents
- **Image Processing**: Automatic image handling and storage
- **Media URL Serving**: Configurable media URL serving

### **Django Integration**
- **Model Integration**: Standard Django model patterns
- **Serializer Validation**: DRF serializer-based validation
- **View Integration**: APIView-based endpoint implementation
- **Admin Interface**: Complete admin interface for management

## 📈 **Performance Considerations**

### **Database Indexes**
- Email and WhatsApp number indexes for fast lookups
- OTP expiration time indexes for cleanup operations
- Employee username and status indexes for filtering
- Action log indexes for audit trail queries

### **OTP Management**
- Automatic cleanup of expired OTPs
- Efficient OTP generation and validation
- Single-use OTP enforcement

### **Permission System**
- Efficient permission checking with JSON field indexing
- Bulk permission updates for performance
- Permission template caching

### **Caching Strategy**
- Saraf profile caching for frequently accessed data
- Permission template caching
- OTP rate limiting to prevent abuse
- Token caching for authentication performance

## 🧪 **Testing**

### **Test Coverage**
- Model validation and methods
- Serializer validation and data processing
- View authentication and authorization
- OTP generation and verification
- Password validation and hashing
- Employee management and permissions
- Email and WhatsApp integration

### **Test Scenarios**
1. **Registration Flow**: Test email and WhatsApp registration with registration codes
2. **OTP Verification**: Test OTP generation, verification, and expiration
3. **Login Flow**: Test authentication with different contact methods
4. **Employee Management**: Test employee creation, permission management, and status control
5. **Permission System**: Test granular permissions and bulk operations
6. **Password Reset**: Test forgot password and reset password flow
7. **Error Handling**: Test validation errors and edge cases
8. **Security**: Test password requirements and OTP security

## 🚀 **Deployment Notes**

### **Environment Variables**
- **Email Settings**: `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_HOST`, `EMAIL_PORT`
- **Twilio Settings**: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM_NUMBER`
- **JWT Settings**: `SECRET_KEY` for token signing
- **Media Settings**: `MEDIA_URL`, `MEDIA_ROOT` for file storage

### **Database Migrations**
- Run migrations to create required tables
- Set up database indexes for performance
- Configure foreign key constraints

### **Email Configuration**
- Configure SMTP settings for production
- Set up email templates and styling
- Configure email delivery monitoring

### **WhatsApp Configuration**
- Set up Twilio WhatsApp Business API
- Configure approved message templates
- Set up webhook endpoints for delivery status

### **File Storage Configuration**
- Configure media file storage backend
- Set up file upload limits and validation
- Configure CDN for media file serving

## 🔧 **Development Setup**

### **Required Dependencies**
```python
# Django and DRF
django>=4.0
djangorestframework>=3.14
djangorestframework-simplejwt>=5.0

# Email and WhatsApp
twilio>=8.0

# Password hashing
django[argon2]  # For Argon2 password hashing

# File handling
Pillow>=9.0  # For image processing
```

### **Settings Configuration**
```python
# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

# Twilio settings
TWILIO_ACCOUNT_SID = 'your-account-sid'
TWILIO_AUTH_TOKEN = 'your-auth-token'
TWILIO_WHATSAPP_FROM_NUMBER = 'whatsapp:+14155238886'

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# Media settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 📚 **API Documentation**

### **Registration Endpoint**
- **URL**: `/api/saraf/register/`
- **Method**: `POST`
- **Description**: Register a new Saraf business account
- **Required Fields**: `full_name`, `email_or_whatsapp_number`, `license_no`, `amu_pay_code`, `province`, `password`, `repeat_password`, `registration_code`
- **Response**: Saraf ID, contact info, OTP type, and JWT tokens

### **OTP Verification Endpoint**
- **URL**: `/api/saraf/otp/verify/`
- **Method**: `POST`
- **Description**: Verify OTP code for account activation
- **Required Fields**: `email_or_whatsapp_number`, `otp_code`
- **Response**: Verification success status

### **Login Endpoint**
- **URL**: `/api/saraf/login/`
- **Method**: `POST`
- **Description**: Authenticate Saraf account and return JWT tokens
- **Required Fields**: `email_or_whatsapp_number`, `password`
- **Response**: Access token, refresh token, and Saraf information

### **List All Saraf Accounts Endpoint**
- **URL**: `/api/saraf/list/`
- **Method**: `GET`
- **Description**: Get a list of all active Saraf accounts
- **Authentication**: Not required (Public)
- **Response**: Array of Saraf accounts with basic information (saraf_id, exchange_name, province, saraf_logo, email_or_whatsapp_number)

### **Get Specific Saraf Profile Endpoint**
- **URL**: `/api/saraf/<saraf_id>/`
- **Method**: `GET`
- **Description**: Get detailed information about a specific Saraf account by ID
- **Authentication**: Not required (Public)
- **URL Parameters**: `saraf_id` (integer) - The ID of the Saraf account
- **Response**: Complete Saraf profile including:
  - Basic info: saraf_id, full_name, exchange_name, email_or_whatsapp_number
  - Business details: license_no, amu_pay_code, saraf_address, saraf_location_google_map, province
  - Verification status: is_email_verified, is_whatsapp_verified, is_active
  - Images: saraf_logo, saraf_logo_wallpeper, front_id_card, back_id_card (full URLs)
  - Statistics: employee_count, created_at, updated_at
- **Example**: `/api/saraf/1/` - Get details for Saraf with ID 1
- **Error Response**: 404 if Saraf not found or inactive

### **Change Employee Password Endpoint**
- **URL**: `/api/saraf/employees/<employee_id>/change-password/`
- **Method**: `POST`
- **Description**: Allow Saraf owners to change employee passwords without requiring current password
- **Authentication**: Required (Saraf JWT token)
- **Required Fields**: `new_password`, `repeat_password`
- **Password Requirements**: 
  - Minimum 6 characters
  - At least one uppercase letter (A-Z)
  - At least one lowercase letter (a-z)
  - At least one digit (0-9)
  - At least one special character (!@#$%^&*(),.?":{}|<>)
- **Security**: Only Saraf owners can change passwords for their own employees
- **Response**: Success message with employee information

### **Employee Management Endpoints**
- **Create Employee**: `/api/saraf/employees/`
- **Update Employee**: `/api/saraf/employees/<id>/`
- **Delete Employee**: `/api/saraf/employees/<id>/`
- **Get Employees**: `/api/saraf/get-employees/`
- **Change Employee Password**: `/api/saraf/employees/<id>/change-password/`
- **Description**: Complete employee management system

### **Permission Management Endpoints**
- **Get Permissions**: `/api/saraf/permissions/`
- **Update Permissions**: `/api/saraf/permissions/<employee_id>/`
- **Bulk Update**: `/api/saraf/permissions/bulk/`
- **Permission Templates**: `/api/saraf/permissions/templates/`
- **Description**: Granular permission control system

### **Password Reset Endpoints**
- **Forgot Password**: `/api/saraf/forgot-password/`
- **Reset Password**: `/api/saraf/reset-password-confirm/<uidb64>/<token>/`
- **Description**: Secure password reset using OTP verification
- **Flow**: Request OTP → Verify OTP → Reset password

This comprehensive Saraf account system provides a secure, scalable business management solution with advanced employee management, granular permissions, and complete audit trails for money exchange businesses.
