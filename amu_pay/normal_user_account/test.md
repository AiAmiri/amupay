# 👤 **Normal User Account Test Cases for Postman**

This document provides comprehensive test cases for all Normal User Account API endpoints using Postman.

## Prerequisites

1. **Test Environment**: Ensure the Django server is running
2. **Email Configuration**: Configure SMTP settings for email OTP testing
3. **WhatsApp Configuration**: Configure Twilio settings for WhatsApp OTP testing
4. **Test Data**: Prepare test email addresses and phone numbers

## Environment Variables Setup

Create these variables in Postman:

```
NORMAL_USER_BASE_URL: http://localhost:8000/api/normal-user
TEST_EMAIL: test@example.com
TEST_WHATSAPP: +1234567890
TEST_PASSWORD: SecurePass123!
ACCESS_TOKEN: your_access_token_here
REFRESH_TOKEN: your_refresh_token_here
USER_ID: 1
```

## Test Cases

### 1. Register User with Email

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/register/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "full_name": "John Doe",
    "email_or_whatsapp": "{{TEST_EMAIL}}",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "{{TEST_PASSWORD}}"
}
```

**Expected Response** (201 Created):
```json
{
    "message": "Registration successful. Please check your email for OTP verification.",
    "user_id": 1,
    "email": "test@example.com",
    "requires_verification": true
}
```

---

### 2. Register User with WhatsApp

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/register/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "full_name": "Jane Smith",
    "email_or_whatsapp": "{{TEST_WHATSAPP}}",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "{{TEST_PASSWORD}}"
}
```

**Expected Response** (201 Created):
```json
{
    "message": "Registration successful. Please check your WhatsApp for OTP verification.",
    "user_id": 2,
    "whatsapp_number": "+1234567890",
    "requires_verification": true
}
```

---

### 3. Verify Email OTP

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/verify-otp/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_EMAIL}}",
    "otp_code": "123456"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Verification successful! Your account is now active.",
    "user_id": 1,
    "is_verified": true
}
```

---

### 4. Verify WhatsApp OTP

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/verify-otp/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_WHATSAPP}}",
    "otp_code": "654321"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Verification successful! Your account is now active.",
    "user_id": 2,
    "is_verified": true
}
```

---

### 5. Login with Email

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/login/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_EMAIL}}",
    "password": "{{TEST_PASSWORD}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "user_id": 1,
        "full_name": "John Doe",
        "email": "test@example.com",
        "whatsapp_number": null,
        "is_email_verified": true,
        "is_whatsapp_verified": false,
        "is_verified": true
    }
}
```

---

### 6. Login with WhatsApp

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/login/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_WHATSAPP}}",
    "password": "{{TEST_PASSWORD}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Login successful",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "user_id": 2,
        "full_name": "Jane Smith",
        "email": null,
        "whatsapp_number": "+1234567890",
        "is_email_verified": false,
        "is_whatsapp_verified": true,
        "is_verified": true
    }
}
```

---

### 7. Forgot Password (Email)

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/forgot-password/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_EMAIL}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Password reset OTP sent to your email."
}
```

---

### 8. Forgot Password (WhatsApp)

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/forgot-password/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_WHATSAPP}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Password reset OTP sent to your WhatsApp."
}
```

---

### 9. Reset Password

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/reset-password/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_EMAIL}}",
    "otp_code": "789012",
    "new_password": "NewSecurePass123!",
    "repeat_password": "NewSecurePass123!"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Password reset successful. You can now login with your new password."
}
```

---

### 10. Resend OTP (Email)

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/resend-otp/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_EMAIL}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "New OTP sent to your email. Please check your inbox."
}
```

---

### 11. Resend OTP (WhatsApp)

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/resend-otp/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_WHATSAPP}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "New OTP sent to your WhatsApp. Please check your messages."
}
```

---

### 12. Get User Profile

**Endpoint**: `GET {{NORMAL_USER_BASE_URL}}/profile/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "user_id": "{{USER_ID}}"
}
```

**Expected Response** (200 OK):
```json
{
    "user_id": 1,
    "full_name": "John Doe",
    "email": "test@example.com",
    "whatsapp_number": null,
    "is_email_verified": true,
    "is_whatsapp_verified": false,
    "is_active": true,
    "created_at": "2024-01-01T10:00:00Z",
    "last_login": "2024-01-01T10:30:00Z"
}
```

---

## Error Test Cases

### 1. Invalid Email Format

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/register/`

**Request Body**:
```json
{
    "full_name": "Test User",
    "email_or_whatsapp": "invalid-email",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "{{TEST_PASSWORD}}"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "email_or_whatsapp": ["Please enter a valid email address or WhatsApp number"]
}
```

---

### 2. Invalid WhatsApp Format

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/register/`

**Request Body**:
```json
{
    "full_name": "Test User",
    "email_or_whatsapp": "123",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "{{TEST_PASSWORD}}"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "email_or_whatsapp": ["Please enter a valid email address or WhatsApp number"]
}
```

---

### 3. Weak Password

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/register/`

**Request Body**:
```json
{
    "full_name": "Test User",
    "email_or_whatsapp": "test@example.com",
    "password": "123",
    "repeat_password": "123"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "password": ["Password must be at least 6 characters long"]
}
```

---

### 4. Password Mismatch

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/register/`

**Request Body**:
```json
{
    "full_name": "Test User",
    "email_or_whatsapp": "test@example.com",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "DifferentPass123!"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "non_field_errors": ["Passwords do not match"]
}
```

---

### 5. Duplicate Email Registration

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/register/`

**Request Body**:
```json
{
    "full_name": "Another User",
    "email_or_whatsapp": "{{TEST_EMAIL}}",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "{{TEST_PASSWORD}}"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "email_or_whatsapp": ["An account with this email already exists"]
}
```

---

### 6. Invalid Login Credentials

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/login/`

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_EMAIL}}",
    "password": "WrongPassword123!"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "email_or_whatsapp": ["Invalid email/WhatsApp or password"]
}
```

---

### 7. Invalid OTP Code

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/verify-otp/`

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_EMAIL}}",
    "otp_code": "000000"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "otp_code": ["Invalid OTP code"]
}
```

---

### 8. Expired OTP Code

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/verify-otp/`

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_EMAIL}}",
    "otp_code": "123456"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "non_field_errors": ["OTP has expired"]
}
```

---

### 9. User Not Found

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/forgot-password/`

**Request Body**:
```json
{
    "email_or_whatsapp": "nonexistent@example.com"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "email_or_whatsapp": ["No account found with this email/WhatsApp number"]
}
```

---

### 10. Already Verified Email

**Endpoint**: `POST {{NORMAL_USER_BASE_URL}}/resend-otp/`

**Request Body**:
```json
{
    "email_or_whatsapp": "{{TEST_EMAIL}}"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "email_or_whatsapp": ["Email is already verified"]
}
```

---

## Test Execution Order

1. **Setup**: Configure environment variables and test data
2. **Registration**: Test email and WhatsApp registration
3. **OTP Verification**: Test OTP verification for both contact methods
4. **Login**: Test login with verified accounts
5. **Password Reset**: Test forgot password and reset password flow
6. **Resend OTP**: Test OTP resending functionality
7. **Profile**: Test user profile retrieval
8. **Error Cases**: Test validation errors and edge cases

## Postman Collection Setup

1. Create a new collection named "Normal User Account Tests"
2. Add all endpoints as requests
3. Set up environment variables
4. Add pre-request scripts for dynamic data generation
5. Add test scripts for response validation

## Dynamic Data Generation

Use these Postman pre-request scripts for dynamic data:

```javascript
// Generate random email
pm.environment.set("random_email", "test" + Math.floor(Math.random() * 10000) + "@example.com");

// Generate random WhatsApp number
pm.environment.set("random_whatsapp", "+1" + Math.floor(Math.random() * 1000000000));

// Generate random password
pm.environment.set("random_password", "TestPass" + Math.floor(Math.random() * 1000) + "!");

// Generate random OTP code
pm.environment.set("random_otp", Math.floor(Math.random() * 900000) + 100000);
```

## Response Validation Scripts

Add these test scripts to validate responses:

```javascript
// Check response status
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Check response structure
pm.test("Response has required fields", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('message');
});

// Check authentication
pm.test("Response is not unauthorized", function () {
    pm.expect(pm.response.code).to.not.equal(401);
});

// Check OTP response
pm.test("OTP response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('message');
    pm.expect(jsonData).to.have.property('user_id');
});

// Check login response
pm.test("Login response has tokens", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('access_token');
    pm.expect(jsonData).to.have.property('refresh_token');
    pm.expect(jsonData).to.have.property('user');
});
```

## Test Scenarios

### **Complete Registration Flow**
1. Register with email → Receive OTP → Verify OTP → Login
2. Register with WhatsApp → Receive OTP → Verify OTP → Login

### **Password Reset Flow**
1. Forgot password → Receive OTP → Reset password → Login with new password

### **OTP Management**
1. Generate OTP → Wait for expiration → Resend OTP → Verify with new OTP

### **Error Handling**
1. Invalid formats → Validation errors
2. Duplicate accounts → Conflict errors
3. Invalid credentials → Authentication errors
4. Expired OTPs → Expiration errors

## Performance Testing

### **Load Testing Scenarios**
1. **Concurrent Registrations**: Test multiple simultaneous registrations
2. **OTP Generation**: Test OTP generation under load
3. **Login Performance**: Test login response times
4. **Database Performance**: Test database query performance

### **Security Testing**
1. **Password Strength**: Test password validation
2. **OTP Security**: Test OTP generation and validation
3. **Token Security**: Test JWT token generation and validation
4. **Rate Limiting**: Test OTP rate limiting

This comprehensive test suite covers all Normal User Account endpoints with various scenarios including success cases, error cases, and edge cases for both email and WhatsApp authentication methods.
