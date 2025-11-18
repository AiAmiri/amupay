# 🏦 **Saraf Account Test Cases for Postman**

This document provides comprehensive test cases for all Saraf Account API endpoints using Postman.

## Prerequisites

1. **Test Environment**: Ensure the Django server is running
2. **Email Configuration**: Configure SMTP settings for email OTP testing
3. **WhatsApp Configuration**: Configure Twilio settings for WhatsApp OTP testing
4. **Registration Codes**: Generate valid registration codes for testing
5. **Test Data**: Prepare test email addresses and phone numbers

## Environment Variables Setup

Create these variables in Postman:

```
SARAF_BASE_URL: http://localhost:8000/api/saraf
TEST_EMAIL: saraf@example.com
TEST_WHATSAPP: 0791234567
TEST_PASSWORD: SecurePass123!
REGISTRATION_CODE: ABCD1234EFGH
ACCESS_TOKEN: your_access_token_here
REFRESH_TOKEN: your_refresh_token_here
SARAF_ID: 1
EMPLOYEE_ID: 1
```

## Test Cases

### 1. Register Saraf Account with Email

**Endpoint**: `POST {{SARAF_BASE_URL}}/register/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "full_name": "ABC Exchange",
    "exchange_name": "ABC Money Exchange",
    "email_or_whatsapp_number": "{{TEST_EMAIL}}",
    "license_no": "LIC123456",
    "amu_pay_code": "ABC123",
    "saraf_address": "123 Main Street",
    "province": "Kabul",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "{{TEST_PASSWORD}}",
    "registration_code": "{{REGISTRATION_CODE}}"
}
```

**Expected Response** (201 Created):
```json
{
    "message": "Account created successfully. Please check your email for OTP verification.",
    "saraf_id": 1,
    "contact_info": "saraf@example.com",
    "otp_type": "email",
    "otp_sent": true,
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 2. Register Saraf Account with WhatsApp

**Endpoint**: `POST {{SARAF_BASE_URL}}/register/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "full_name": "XYZ Exchange",
    "exchange_name": "XYZ Money Exchange",
    "email_or_whatsapp_number": "{{TEST_WHATSAPP}}",
    "license_no": "LIC789012",
    "amu_pay_code": "XYZ456",
    "saraf_address": "456 Oak Street",
    "province": "Herat",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "{{TEST_PASSWORD}}",
    "registration_code": "WXYZ5678IJKL"
}
```

**Expected Response** (201 Created):
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

---

### 3. Verify Email OTP

**Endpoint**: `POST {{SARAF_BASE_URL}}/otp/verify/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp_number": "{{TEST_EMAIL}}",
    "otp_code": "123456"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "OTP verified successfully",
    "saraf_id": 1,
    "verified": true
}
```

---

### 4. Verify WhatsApp OTP

**Endpoint**: `POST {{SARAF_BASE_URL}}/otp/verify/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp_number": "{{TEST_WHATSAPP}}",
    "otp_code": "654321"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "OTP verified successfully",
    "saraf_id": 2,
    "verified": true
}
```

---

### 5. Login with Email

**Endpoint**: `POST {{SARAF_BASE_URL}}/login/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp_number": "{{TEST_EMAIL}}",
    "password": "{{TEST_PASSWORD}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Login successful",
    "user_type": "saraf",
    "user_id": 1,
    "full_name": "ABC Exchange",
    "exchange_name": "ABC Money Exchange",
    "email_or_whatsapp_number": "saraf@example.com",
    "is_verified": true,
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 6. Login with WhatsApp

**Endpoint**: `POST {{SARAF_BASE_URL}}/login/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp_number": "{{TEST_WHATSAPP}}",
    "password": "{{TEST_PASSWORD}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Login successful",
    "user_type": "saraf",
    "user_id": 2,
    "full_name": "XYZ Exchange",
    "exchange_name": "XYZ Money Exchange",
    "email_or_whatsapp_number": "0791234567",
    "is_verified": true,
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 7. Create Employee

**Endpoint**: `POST {{SARAF_BASE_URL}}/employees/`

**Headers**:
```
Authorization: Bearer {{ACCESS_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "username": "john_doe",
    "full_name": "John Doe",
    "password": "EmployeePass123!",
    "repeat_password": "EmployeePass123!"
}
```

**Expected Response** (201 Created):
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

---

### 8. Get Employee List

**Endpoint**: `GET {{SARAF_BASE_URL}}/get-employees/?whatsapp_number={{saraf WA numer}}`

**Headers**:
```
Authorization: Public
body: None
```

**Expected Response** (200 OK):
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

---

### 9. Update Employee Permissions

**Endpoint**: `PUT {{SARAF_BASE_URL}}/permissions/{{EMPLOYEE_ID}}/`

**Headers**:
```
Authorization: Bearer {{ACCESS_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "permissions": {
        "take_money": true,
        "give_money": true,
        "loans": true,
        "add_employee": true
    }
}
```

**Expected Response** (200 OK):
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

---

### 10. Bulk Update Permissions

**Endpoint**: `POST {{SARAF_BASE_URL}}/permissions/bulk/`

**Headers**:
```
Authorization: Bearer {{ACCESS_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "employee_ids": [1, 2, 3],
    "permissions": {
        "send_transfer": true,
        "receive_transfer": true,
        "view_history": true
    }
}
```

**Expected Response** (200 OK):
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

---

### 11. Get Permission Templates

**Endpoint**: `GET {{SARAF_BASE_URL}}/permissions/templates/`

**Headers**:
```
Authorization: Bearer {{ACCESS_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "templates": {
        "manager": {
            "description": "Full access manager permissions",
            "permissions": {
                "edit_profile": true,
                "chat": true,
                "send_transfer": true,
                "receive_transfer": true,
                "take_money": true,
                "give_money": true,
                "loans": true,
                "add_employee": true,
                "change_password": true,
                "see_how_did_works": true,
                "create_exchange": true,
                "view_history": true,
                "create_accounts": true,
                "delete_accounts": true,
                "add_posts": true,
                "deliver_amount": true,
                "withdraw_to_customer": true,
                "deposit_to_customer": true,
                "withdraw_from_account": true,
                "deposit_to_account": true,
                "add_currency": true
            }
        },
        "cashier": {
            "description": "Cashier with limited permissions",
            "permissions": {
                "chat": true,
                "send_transfer": true,
                "receive_transfer": true,
                "take_money": true,
                "give_money": true,
                "deliver_amount": true,
                "withdraw_to_customer": true,
                "deposit_to_customer": true,
                "view_history": true
            }
        }
    }
}
```

---

### 12. Forgot Password

**Endpoint**: `POST {{SARAF_BASE_URL}}/forgot-password/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp_number": "{{TEST_EMAIL}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Password reset OTP sent to your email."
}
```

---

### 13. Reset Password

**Endpoint**: `POST {{SARAF_BASE_URL}}/reset-password-confirm/uidb64/token/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
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

### 14. Resend OTP

**Endpoint**: `POST {{SARAF_BASE_URL}}/otp/resend/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "email_or_whatsapp_number": "{{TEST_EMAIL}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "OTP resent successfully",
    "contact_info": "saraf@example.com",
    "otp_type": "email"
}
```

---

### 15. Get Saraf List

**Endpoint**: `GET {{SARAF_BASE_URL}}/list/`

**Headers**:
```
Content-Type: application/json
```

**Expected Response** (200 OK):
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

---

### 16. Change Password

**Endpoint**: `POST {{SARAF_BASE_URL}}/change-password/`

**Headers**:
```
Authorization: Bearer {{ACCESS_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "old_password": "{{TEST_PASSWORD}}",
    "new_password": "NewSecurePass123!",
    "repeat_password": "NewSecurePass123!"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Password changed successfully"
}
```

---

### 17. Get Protected Account Info

**Endpoint**: `GET {{SARAF_BASE_URL}}/protected/`

**Headers**:
```
Authorization: Bearer {{ACCESS_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "saraf_id": 1,
    "full_name": "ABC Exchange",
    "exchange_name": "ABC Money Exchange",
    "email_or_whatsapp_number": "saraf@example.com",
    "license_no": "LIC123456",
    "saraf_address": "123 Main Street",
    "province": "Kabul",
    "is_email_verified": true,
    "is_whatsapp_verified": false,
    "is_active": true,
    "created_at": "2024-01-01T10:00:00Z"
}
```

---

### 18. Delete Account

**Endpoint**: `DELETE {{SARAF_BASE_URL}}/delete-account/`

**Headers**:
```
Authorization: Bearer {{ACCESS_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "password": "{{TEST_PASSWORD}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Account deleted successfully"
}
```

---

## Error Test Cases

### 1. Invalid Email Format

**Endpoint**: `POST {{SARAF_BASE_URL}}/register/`

**Request Body**:
```json
{
    "full_name": "Test Exchange",
    "exchange_name": "Test Money Exchange",
    "email_or_whatsapp_number": "invalid-email",
    "license_no": "LIC123456",
    "amu_pay_code": "TEST123",
    "saraf_address": "123 Test Street",
    "province": "Kabul",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "{{TEST_PASSWORD}}",
    "registration_code": "{{REGISTRATION_CODE}}"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "email_or_whatsapp_number": ["Invalid email format"]
}
```

---

### 2. Invalid WhatsApp Format

**Endpoint**: `POST {{SARAF_BASE_URL}}/register/`

**Request Body**:
```json
{
    "full_name": "Test Exchange",
    "exchange_name": "Test Money Exchange",
    "email_or_whatsapp_number": "123",
    "license_no": "LIC123456",
    "amu_pay_code": "TEST123",
    "saraf_address": "123 Test Street",
    "province": "Kabul",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "{{TEST_PASSWORD}}",
    "registration_code": "{{REGISTRATION_CODE}}"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "email_or_whatsapp_number": ["Phone must be 10 digits and start with 0"]
}
```

---

### 3. Weak Password

**Endpoint**: `POST {{SARAF_BASE_URL}}/register/`

**Request Body**:
```json
{
    "full_name": "Test Exchange",
    "exchange_name": "Test Money Exchange",
    "email_or_whatsapp_number": "{{TEST_EMAIL}}",
    "license_no": "LIC123456",
    "amu_pay_code": "TEST123",
    "saraf_address": "123 Test Street",
    "province": "Kabul",
    "password": "123",
    "repeat_password": "123",
    "registration_code": "{{REGISTRATION_CODE}}"
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

**Endpoint**: `POST {{SARAF_BASE_URL}}/register/`

**Request Body**:
```json
{
    "full_name": "Test Exchange",
    "exchange_name": "Test Money Exchange",
    "email_or_whatsapp_number": "{{TEST_EMAIL}}",
    "license_no": "LIC123456",
    "amu_pay_code": "TEST123",
    "saraf_address": "123 Test Street",
    "province": "Kabul",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "DifferentPass123!",
    "registration_code": "{{REGISTRATION_CODE}}"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "non_field_errors": ["Passwords do not match"]
}
```

---

### 5. Invalid Registration Code

**Endpoint**: `POST {{SARAF_BASE_URL}}/register/`

**Request Body**:
```json
{
    "full_name": "Test Exchange",
    "exchange_name": "Test Money Exchange",
    "email_or_whatsapp_number": "{{TEST_EMAIL}}",
    "license_no": "LIC123456",
    "amu_pay_code": "TEST123",
    "saraf_address": "123 Test Street",
    "province": "Kabul",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "{{TEST_PASSWORD}}",
    "registration_code": "INVALID123"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "registration_code": ["Invalid or already used registration code"]
}
```

---

### 6. Duplicate Email Registration

**Endpoint**: `POST {{SARAF_BASE_URL}}/register/`

**Request Body**:
```json
{
    "full_name": "Another Exchange",
    "exchange_name": "Another Money Exchange",
    "email_or_whatsapp_number": "{{TEST_EMAIL}}",
    "license_no": "LIC789012",
    "amu_pay_code": "ANOTHER123",
    "saraf_address": "456 Another Street",
    "province": "Herat",
    "password": "{{TEST_PASSWORD}}",
    "repeat_password": "{{TEST_PASSWORD}}",
    "registration_code": "ANOTHER5678"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "email_or_whatsapp_number": ["An account with this email already exists"]
}
```

---

### 7. Invalid Login Credentials

**Endpoint**: `POST {{SARAF_BASE_URL}}/login/`

**Request Body**:
```json
{
    "email_or_whatsapp_number": "{{TEST_EMAIL}}",
    "password": "WrongPassword123!"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "email_or_whatsapp_number": ["Invalid email/WhatsApp or password"]
}
```

---

### 8. Invalid OTP Code

**Endpoint**: `POST {{SARAF_BASE_URL}}/otp/verify/`

**Request Body**:
```json
{
    "email_or_whatsapp_number": "{{TEST_EMAIL}}",
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

### 9. Expired OTP Code

**Endpoint**: `POST {{SARAF_BASE_URL}}/otp/verify/`

**Request Body**:
```json
{
    "email_or_whatsapp_number": "{{TEST_EMAIL}}",
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

### 10. User Not Found

**Endpoint**: `POST {{SARAF_BASE_URL}}/forgot-password/`

**Request Body**:
```json
{
    "email_or_whatsapp_number": "nonexistent@example.com"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "email_or_whatsapp_number": ["No account found with this email/WhatsApp number"]
}
```

---

### 11. Invalid Permission

**Endpoint**: `PUT {{SARAF_BASE_URL}}/permissions/{{EMPLOYEE_ID}}/`

**Request Body**:
```json
{
    "permissions": {
        "invalid_permission": true
    }
}
```

**Expected Response** (400 Bad Request):
```json
{
    "permissions": ["Invalid permission: invalid_permission"]
}
```

---

### 12. Unauthorized Access

**Endpoint**: `GET {{SARAF_BASE_URL}}/protected/`

**Headers**:
```
Authorization: Bearer invalid_token
Content-Type: application/json
```

**Expected Response** (401 Unauthorized):
```json
{
    "detail": "Authentication credentials were not provided."
}
```

---

## Test Execution Order

1. **Setup**: Configure environment variables and test data
2. **Registration**: Test email and WhatsApp registration with registration codes
3. **OTP Verification**: Test OTP verification for both contact methods
4. **Login**: Test login with verified accounts
5. **Employee Management**: Test employee creation, updates, and deletion
6. **Permission Management**: Test permission updates and bulk operations
7. **Password Reset**: Test forgot password and reset password flow
8. **Account Management**: Test account info retrieval and password changes
9. **Error Cases**: Test validation errors and edge cases

## Postman Collection Setup

1. Create a new collection named "Saraf Account Tests"
2. Add all endpoints as requests
3. Set up environment variables
4. Add pre-request scripts for dynamic data generation
5. Add test scripts for response validation

## Dynamic Data Generation

Use these Postman pre-request scripts for dynamic data:

```javascript
// Generate random email
pm.environment.set("random_email", "saraf" + Math.floor(Math.random() * 10000) + "@example.com");

// Generate random WhatsApp number
pm.environment.set("random_whatsapp", "0" + Math.floor(Math.random() * 1000000000));

// Generate random password
pm.environment.set("random_password", "SarafPass" + Math.floor(Math.random() * 1000) + "!");

// Generate random OTP code
pm.environment.set("random_otp", Math.floor(Math.random() * 900000) + 100000);

// Generate random license number
pm.environment.set("random_license", "LIC" + Math.floor(Math.random() * 1000000));

// Generate random AMU Pay code
pm.environment.set("random_amu_pay", "AMU" + Math.floor(Math.random() * 1000));
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
    pm.expect(jsonData).to.have.property('saraf_id');
});

// Check login response
pm.test("Login response has tokens", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('access');
    pm.expect(jsonData).to.have.property('refresh');
    pm.expect(jsonData).to.have.property('user_type');
});

// Check employee response
pm.test("Employee response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('employee_id');
    pm.expect(jsonData).to.have.property('username');
    pm.expect(jsonData).to.have.property('permissions');
});

// Check permission response
pm.test("Permission response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('permissions');
    pm.expect(jsonData.permissions).to.be.an('object');
});
```

## Test Scenarios

### **Complete Registration Flow**
1. Register with email → Receive OTP → Verify OTP → Login
2. Register with WhatsApp → Receive OTP → Verify OTP → Login

### **Employee Management Flow**
1. Create employee → Set permissions → Update permissions → Delete employee

### **Permission Management Flow**
1. Get default permissions → Update individual permissions → Bulk update permissions

### **Password Reset Flow**
1. Forgot password → Receive OTP → Reset password → Login with new password

### **Error Handling**
1. Invalid formats → Validation errors
2. Duplicate accounts → Conflict errors
3. Invalid credentials → Authentication errors
4. Expired OTPs → Expiration errors
5. Invalid permissions → Permission errors

## Performance Testing

### **Load Testing Scenarios**
1. **Concurrent Registrations**: Test multiple simultaneous registrations
2. **OTP Generation**: Test OTP generation under load
3. **Login Performance**: Test login response times
4. **Employee Management**: Test employee operations under load
5. **Permission Updates**: Test permission management performance

### **Security Testing**
1. **Password Strength**: Test password validation
2. **OTP Security**: Test OTP generation and validation
3. **Token Security**: Test JWT token generation and validation
4. **Permission Security**: Test permission validation and enforcement
5. **Rate Limiting**: Test OTP rate limiting

## Business Logic Testing

### **Registration Code Validation**
1. Test valid registration codes
2. Test invalid registration codes
3. Test already used registration codes
4. Test registration code expiration

### **Permission System Testing**
1. Test default permission assignment
2. Test individual permission updates
3. Test bulk permission updates
4. Test permission inheritance
5. Test permission validation

### **Employee Management Testing**
1. Test employee creation with default permissions
2. Test employee username uniqueness
3. Test employee status management
4. Test employee deletion and cleanup

This comprehensive test suite covers all Saraf Account endpoints with various scenarios including success cases, error cases, and edge cases for both email and WhatsApp authentication methods, employee management, and permission systems.
