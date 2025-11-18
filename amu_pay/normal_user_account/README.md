# 👤 **Normal User Account App**

A comprehensive user management system for AMU Pay that enables normal customers to register, authenticate, and manage their accounts with OTP-based verification through email.

## 🎯 **Overview**

The Normal User Account app provides a complete customer authentication solution with:
- **Email Registration**: Email-based registration and verification
- **OTP Verification**: Email OTP verification
- **Secure Authentication**: JWT token-based authentication
- **Password Management**: Secure password reset with OTP verification
- **Account Management**: Profile management and verification status tracking

> **⚠️ Note**: WhatsApp OTP functionality is currently disabled (Twilio account deleted). Only email registration and verification is available. Users should register using their email address.

## 🏗️ **Architecture**

### **Models**

#### **NormalUser**
- **Purpose**: Represents a normal customer account
- **Contact Methods**: Email OR WhatsApp number (one required)
- **Security**: Password hashing, verification status tracking
- **Features**: Account activation, last login tracking

#### **NormalUserOTP**
- **Purpose**: Manages OTP verification codes
- **Types**: `email`, `whatsapp`, `password_reset`
- **Features**: Expiration tracking, usage validation, secure generation

### **Key Features**

#### **🔐 Authentication & Security**
- **Password Requirements**: Minimum 6 characters with uppercase, lowercase, digit, and special character
- **OTP Verification**: 6-digit codes with 10-minute expiration
- **JWT Tokens**: Custom token generation with user-specific claims
- **Account Security**: Password hashing, verification status tracking
- **JWT Session Management**: Secure login and logout with client-side token management

#### **📱 Contact Management**
- **Email Support**: Full email validation and verification
- **Email-Only Registration**: Currently only email registration is supported
- ~~**WhatsApp Support**: International phone number validation~~ (Disabled - Twilio account deleted)
- ~~**Flexible Registration**: Either email OR WhatsApp~~ (Only email is active)

#### **🔄 OTP System**
- **Email OTP**: HTML-formatted emails with OTP codes
- ~~**WhatsApp OTP**: Twilio integration for WhatsApp delivery~~ (Disabled - Twilio account deleted)
- **Password Reset OTP**: Secure password reset flow (email only)
- **Resend Functionality**: OTP resending with expiration handling (email only)

#### **👤 User Management**
- **Profile Management**: User information and verification status
- **Account Status**: Active/inactive account management
- **Login Tracking**: Last login timestamp tracking
- **Verification Status**: Email and WhatsApp verification tracking

## 🚀 **API Endpoints**

### **Registration & Verification**
```http
POST   /api/normal-user/register/              # Register new user
POST   /api/normal-user/verify-otp/           # Verify OTP code
POST   /api/normal-user/resend-otp/           # Resend OTP code
```

### **Authentication**
```http
POST   /api/normal-user/login/                # User login
POST   /api/normal-user/logout/               # User logout
```

### **Password Management (3-Step Process)**
```http
POST   /api/normal-user/forgot-password/              # Step 1: Request password reset OTP
POST   /api/normal-user/forgot-password/otp/verify/   # Step 2: Verify OTP, get reset token
POST   /api/normal-user/reset-password-confirm/<uidb64>/<token>/  # Step 3: Reset password with token
```

### **Profile Management**
```http
GET    /api/normal-user/profile/              # Get user profile
```

## 📋 **Usage Examples**

### **1. Register New User**

```bash
curl -X POST "http://localhost:8000/api/normal-user/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email_or_whatsapp": "john@example.com",
    "password": "SecurePass123!",
    "repeat_password": "SecurePass123!"
  }'
```

**Response:**
```json
{
    "message": "Registration successful. Please check your email for OTP verification.",
    "user_id": 1,
    "email": "john@example.com",
    "requires_verification": true
}
```

### **2. Register with WhatsApp**

```bash
curl -X POST "http://localhost:8000/api/normal-user/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Smith",
    "email_or_whatsapp": "+1234567890",
    "password": "SecurePass123!",
    "repeat_password": "SecurePass123!"
  }'
```

**Response:**
```json
{
    "message": "Registration successful. Please check your WhatsApp for OTP verification.",
    "user_id": 2,
    "whatsapp_number": "+1234567890",
    "requires_verification": true
}
```

### **3. Verify OTP**

```bash
curl -X POST "http://localhost:8000/api/normal-user/verify-otp/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_whatsapp": "john@example.com",
    "otp_code": "123456"
  }'
```

**Response:**
```json
{
    "message": "Verification successful! Your account is now active.",
    "user_id": 1,
    "is_verified": true
}
```

### **4. Login**

```bash
curl -X POST "http://localhost:8000/api/normal-user/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_whatsapp": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "user_id": 1,
        "full_name": "John Doe",
        "email": "john@example.com",
        "whatsapp_number": null,
        "is_email_verified": true,
        "is_whatsapp_verified": false,
        "is_verified": true
    }
}
```

### **5. Logout**

```bash
curl -X POST "http://localhost:8000/api/normal-user/logout/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

**Note:** JWT logout works differently from session-based logout. The server cannot invalidate JWT tokens, so the client must discard the token after receiving the logout confirmation.

**Response:**
```json
{
    "message": "Successfully logged out. Please discard your token on the client side.",
    "user_id": 1,
    "logout_timestamp": "2025-10-25T18:08:18.401669+00:00"
}
```

### **6. Forgot Password (Step 1: Request OTP)**

```bash
curl -X POST "http://localhost:8000/api/normal-user/forgot-password/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_whatsapp": "john@example.com"
  }'
```

**Response:**
```json
{
    "message": "OTP sent to your email for password reset verification.",
    "contact_info": "john@example.com",
    "otp_type": "email"
}
```

### **7. Forgot Password (Step 2: Verify OTP)**

```bash
curl -X POST "http://localhost:8000/api/normal-user/forgot-password/otp/verify/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_whatsapp": "john@example.com",
    "otp_code": "654321"
  }'
```

**Response:**
```json
{
    "message": "OTP verified successfully. You can now reset your password.",
    "uidb64": "MQ",
    "token": "abcdef-123456-ghijkl",
    "reset_path": "reset-password-confirm/MQ/abcdef-123456-ghijkl/"
}
```

### **8. Reset Password (Step 3: Confirm with Token)**

```bash
curl -X POST "http://localhost:8000/api/normal-user/reset-password-confirm/MQ/abcdef-123456-ghijkl/" \
  -H "Content-Type: application/json" \
  -d '{
    "new_password": "NewSecurePass123!"
  }'
```

**Response:**
```json
{
    "message": "Password has been reset successfully. You can now login with your new password."
}
```

### **9. Resend OTP**

```bash
curl -X POST "http://localhost:8000/api/normal-user/resend-otp/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_whatsapp": "john@example.com"
  }'
```

**Response:**
```json
{
    "message": "New OTP sent to your email. Please check your inbox."
}
```

### **10. Get User Profile**

```bash
curl -X GET "http://localhost:8000/api/normal-user/profile/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1
  }'
```

**Response:**
```json
{
    "user_id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "whatsapp_number": null,
    "is_email_verified": true,
    "is_whatsapp_verified": false,
    "is_active": true,
    "created_at": "2024-01-01T10:00:00Z",
    "last_login": "2024-01-01T10:30:00Z"
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
- **WhatsApp**: International phone number format (+1234567890)
- **Normalization**: Automatic phone number formatting
- **Uniqueness**: Each contact method must be unique across all users

### **JWT Token Configuration**
- **Token Type**: Custom JWT tokens with user-specific claims
- **Claims**: `user_id`, `user_type`, `full_name`, `email`, `whatsapp_number`
- **Refresh Token**: Long-lived refresh token for token renewal
- **Access Token**: Short-lived access token for API requests

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

### **Data Privacy**
- **Password Storage**: Never stored in plain text
- **Contact Information**: Secure storage with proper validation
- **OTP Storage**: Temporary storage with automatic expiration
- **Token Security**: Secure JWT token generation and validation

## 📊 **Database Schema**

### **NormalUser Table**
```sql
CREATE TABLE normal_user_account_normaluser (
    user_id BIGINT PRIMARY KEY,
    full_name VARCHAR(128) NOT NULL,
    email VARCHAR(128) UNIQUE NULL,
    whatsapp_number VARCHAR(15) UNIQUE NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_email_verified BOOLEAN DEFAULT FALSE,
    is_whatsapp_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);
```

### **NormalUserOTP Table**
```sql
CREATE TABLE normal_user_account_normaluserotp (
    otp_id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES normal_user_account_normaluser(user_id),
    otp_type VARCHAR(20) NOT NULL,
    contact_info VARCHAR(128) NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP NULL
);
```

## 🚨 **Error Handling**

### **Common Error Responses**

#### **Validation Errors**
```json
{
    "email_or_whatsapp": ["Please enter a valid email address or WhatsApp number"],
    "password": ["Password must contain at least one uppercase letter"],
    "repeat_password": ["Passwords do not match"]
}
```

#### **Authentication Errors**
```json
{
    "email_or_whatsapp": ["Invalid email/WhatsApp or password"]
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
    "email_or_whatsapp": ["An account with this email already exists"],
    "non_field_errors": ["Account is deactivated"]
}
```

#### **Not Found Errors**
```json
{
    "email_or_whatsapp": ["No account found with this email/WhatsApp number"]
}
```

## 🔄 **Integration Points**

### **Email Integration**
- **Django Email Backend**: Uses Django's built-in email system
- **HTML Templates**: Rich HTML email templates for OTP delivery
- **SMTP Configuration**: Configurable SMTP settings for production

### **WhatsApp Integration**
- **Twilio API**: Twilio WhatsApp Business API integration
- **Content Templates**: Pre-approved WhatsApp message templates
- **International Support**: Global WhatsApp number support

### **JWT Integration**
- **Custom Token Generation**: Manual JWT token creation with user claims
- **Token Validation**: Custom token validation for API requests
- **Refresh Token Support**: Long-lived refresh tokens for session management

### **Django Integration**
- **Model Integration**: Standard Django model patterns
- **Serializer Validation**: DRF serializer-based validation
- **View Integration**: APIView-based endpoint implementation

## 📈 **Performance Considerations**

### **Database Indexes**
- Email and WhatsApp number indexes for fast lookups
- OTP expiration time indexes for cleanup operations
- User status indexes for filtering

### **OTP Management**
- Automatic cleanup of expired OTPs
- Efficient OTP generation and validation
- Single-use OTP enforcement

### **Caching Strategy**
- User profile caching for frequently accessed data
- OTP rate limiting to prevent abuse
- Token caching for authentication performance

## 🧪 **Testing**

### **Test Coverage**
- Model validation and methods
- Serializer validation and data processing
- View authentication and authorization
- OTP generation and verification
- Password validation and hashing
- Email and WhatsApp integration

### **Test Scenarios**
1. **Registration Flow**: Test email and WhatsApp registration
2. **OTP Verification**: Test OTP generation, verification, and expiration
3. **Login Flow**: Test authentication with different contact methods
4. **Password Reset**: Test forgot password and reset password flow
5. **Profile Management**: Test user profile retrieval and updates
6. **Error Handling**: Test validation errors and edge cases
7. **Security**: Test password requirements and OTP security

## 🔐 **Password Reset Flow**

The password reset feature now uses a secure **3-step token-based process** (same as Saraf accounts):

### **Step 1: Request OTP**
- User provides `email_or_whatsapp`
- System generates 6-digit OTP valid for 10 minutes
- OTP sent via email or WhatsApp
- Session stores user info for verification

### **Step 2: Verify OTP**
- User provides `email_or_whatsapp` and `otp_code`
- System verifies OTP validity and expiration
- Generates secure reset token (uidb64 + token)
- Token is user-specific and invalidated after use

### **Step 3: Reset Password**
- User provides `new_password` with reset token in URL
- System validates token hasn't been used
- Password is updated using Django's secure hashing
- Token automatically invalidated after successful reset

### **Security Features**
- ✅ **Token-based**: Reset links expire and are single-use
- ✅ **Time-limited**: OTPs expire in 10 minutes
- ✅ **User-specific**: Tokens tied to user ID and password hash
- ✅ **Auto-invalidation**: Tokens invalidated after password change
- ✅ **No account enumeration**: Same response for valid/invalid accounts

### **Example Flow**
```bash
# Step 1: Request OTP
curl -X POST "http://localhost:8000/api/normal-user/forgot-password/" \
  -d '{"email_or_whatsapp": "user@example.com"}'

# Step 2: Verify OTP (returns uidb64 + token)
curl -X POST "http://localhost:8000/api/normal-user/forgot-password/otp/verify/" \
  -d '{"email_or_whatsapp": "user@example.com", "otp_code": "123456"}'

# Step 3: Reset password with token
curl -X POST "http://localhost:8000/api/normal-user/reset-password-confirm/MQ/abc123-token/" \
  -d '{"new_password": "NewSecurePass123!"}'
```

## 🚀 **Deployment Notes**

### **Environment Variables**
- **Email Settings**: `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_HOST`, `EMAIL_PORT` ✅ **REQUIRED**
- ~~**Twilio Settings**: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM_NUMBER`, `TWILIO_WHATSAPP_CONTENT_SID`~~ ❌ **DISABLED**
- **JWT Settings**: `SECRET_KEY` for token signing ✅ **REQUIRED**

### **Database Migrations**
- Run migrations to create required tables
- Set up database indexes for performance
- Configure foreign key constraints

### **Email Configuration** ✅ **ACTIVE**
- Configure SMTP settings for production
- Set up email templates and styling
- Configure email delivery monitoring

### ~~**WhatsApp Configuration**~~ ❌ **DISABLED - Twilio Account Deleted**
- ~~Set up Twilio WhatsApp Business API~~
- ~~Configure approved message templates~~
- ~~Set up webhook endpoints for delivery status~~
- **Note**: WhatsApp OTP functionality has been disabled. Only email-based registration and verification is currently available.

## 🔧 **Development Setup**

### **Required Dependencies**
```python
# Django and DRF
django>=4.0
djangorestframework>=3.14
djangorestframework-simplejwt>=5.0

# Email (REQUIRED)
# No additional dependencies needed - uses Django's built-in email backend

# WhatsApp (DISABLED - Not needed anymore)
# twilio>=8.0  # ❌ REMOVED - Twilio account deleted

# Password hashing
django[argon2]  # For Argon2 password hashing
```

### **Settings Configuration**
```python
# Email settings ✅ REQUIRED
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

# Twilio settings ❌ DISABLED - No longer needed
# TWILIO_ACCOUNT_SID = 'your-account-sid'
# TWILIO_AUTH_TOKEN = 'your-auth-token'
# TWILIO_WHATSAPP_FROM_NUMBER = 'whatsapp:+14155238886'
# TWILIO_WHATSAPP_CONTENT_SID = 'your-content-sid'

# JWT settings ✅ REQUIRED
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

## 📚 **API Documentation**

> **⚠️ Important**: WhatsApp registration is currently disabled. Use email addresses only for registration and verification. Attempting to register with a phone number will return a `503 Service Unavailable` error.

### **Registration Endpoint**
- **URL**: `/api/normal-user/register/`
- **Method**: `POST`
- **Description**: Register a new normal user account **(Email only)**
- **Required Fields**: `full_name`, `email_or_whatsapp` (use email), `password`, `repeat_password`
- **Response**: User ID and verification requirement status
- **Note**: The `email_or_whatsapp` field should contain an email address. WhatsApp numbers are no longer supported.

### **OTP Verification Endpoint**
- **URL**: `/api/normal-user/verify-otp/`
- **Method**: `POST`
- **Description**: Verify OTP code for account activation
- **Required Fields**: `email_or_whatsapp`, `otp_code`
- **Response**: Verification success status

### **Login Endpoint**
- **URL**: `/api/normal-user/login/`
- **Method**: `POST`
- **Description**: Authenticate user and return JWT tokens
- **Required Fields**: `email_or_whatsapp`, `password`
- **Response**: Access token, refresh token, and user information

### **Password Reset Endpoints**
- **Forgot Password**: `/api/normal-user/forgot-password/`
- **Reset Password**: `/api/normal-user/reset-password/`
- **Description**: Secure password reset using OTP verification
- **Flow**: Request OTP → Verify OTP → Reset password

### **Profile Endpoint**
- **URL**: `/api/normal-user/profile/`
- **Method**: `GET`
- **Description**: Retrieve user profile information
- **Required Fields**: `user_id`
- **Response**: Complete user profile data

This comprehensive normal user account system provides a secure, user-friendly authentication solution with flexible contact methods, robust OTP verification, and complete password management capabilities.
