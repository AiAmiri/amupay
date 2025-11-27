# 🧪 Postman Testing Guide - Registration & OTP Verification

This guide provides detailed instructions for testing the registration and OTP verification flow in Postman.

## 📋 Table of Contents
1. [Normal User Registration](#normal-user-registration)
2. [Normal User OTP Verification](#normal-user-otp-verification)
3. [Normal User Resend OTP](#normal-user-resend-otp)
4. [Saraf Registration](#saraf-registration)
5. [Saraf OTP Verification](#saraf-otp-verification)
6. [Saraf Resend OTP](#saraf-resend-otp)
7. [Testing Scenarios](#testing-scenarios)

---

## Normal User Registration

### Endpoint
```
POST http://your-server-ip/api/normal-user/register/
```
or
```
POST http://localhost:8000/api/normal-user/register/
```

### Headers
```
Content-Type: application/json
```

### Request Body (JSON)
```json
{
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "email_or_whatsapp": "0790123456",
    "password": "SecurePass123!",
    "repeat_password": "SecurePass123!"
}
```

### Expected Response (Success - 200 OK)
```json
{
    "message": "Registration data received. Please check your email for OTP verification.",
    "email": "john.doe@example.com",
    "email_or_whatsapp": "0790123456",
    "requires_verification": true,
    "message_note": "Your account will be created after OTP verification."
}
```

### Expected Response (Error - 400 Bad Request)
```json
{
    "email": ["An account with this email already exists"]
}
```
or
```json
{
    "password": ["Password must contain at least one uppercase letter"]
}
```

### Important Notes
- ✅ **User is NOT saved to database yet**
- ✅ **Check your email for OTP code**
- ✅ **Registration data stored in cache for 15 minutes**
- ✅ **If OTP not verified, data expires and user can register again**

---

## Normal User OTP Verification

### Endpoint
```
POST http://your-server-ip/api/normal-user/verify-otp/
```
or
```
POST http://localhost:8000/api/normal-user/verify-otp/
```

### Headers
```
Content-Type: application/json
```

### Request Body (JSON)
```json
{
    "email": "john.doe@example.com",
    "otp_code": "123456"
}
```

### Expected Response (Success - 201 Created)
```json
{
    "message": "Email verification successful! Your account is now active.",
    "user_id": 1,
    "email": "john.doe@example.com",
    "email_or_whatsapp": "0790123456",
    "is_verified": true,
    "is_active": true
}
```

### Expected Response (Error - Invalid OTP)
```json
{
    "error": "Invalid OTP code"
}
```

### Expected Response (Error - Expired Session)
```json
{
    "error": "Registration session expired or not found. Please register again."
}
```

### Important Notes
- ✅ **User account is created in database ONLY after successful verification**
- ✅ **OTP expires after 10 minutes**
- ✅ **Registration session expires after 15 minutes**

---

## Normal User Resend OTP

### Endpoint
```
POST http://your-server-ip/api/normal-user/resend-otp/
```
or
```
POST http://localhost:8000/api/normal-user/resend-otp/
```

### Headers
```
Content-Type: application/json
```

### Request Body (JSON)
```json
{
    "email": "john.doe@example.com",
    "otp_type": "email"
}
```

### Expected Response (Success - 200 OK)
```json
{
    "message": "New OTP sent to your email. Please check your inbox.",
    "email": "john.doe@example.com"
}
```

### Expected Response (Error - No Pending Registration)
```json
{
    "error": "No pending registration or account found with this email. Please register first."
}
```

---

## Saraf Registration

### Endpoint
```
POST http://your-server-ip/api/saraf/register/
```
or
```
POST http://localhost:8000/api/saraf/register/
```

### Headers
```
Content-Type: multipart/form-data
```
**OR**
```
Content-Type: application/json
```

### Request Body (Form-Data)
```
full_name: Ahmad Saraf
exchange_name: Kabul Exchange
email: ahmad@example.com
email_or_whatsapp_number: 0790123456
license_no: LIC123456
amu_pay_code: AMU001
saraf_address: Street 123, Kabul
province: Kabul
password: SecurePass123!
saraf_logo: [FILE] (optional)
saraf_logo_wallpeper: [FILE] (optional)
front_id_card: [FILE] (optional)
back_id_card: [FILE] (optional)
```

### Request Body (JSON - without files)
```json
{
    "full_name": "Ahmad Saraf",
    "exchange_name": "Kabul Exchange",
    "email": "ahmad@example.com",
    "email_or_whatsapp_number": "0790123456",
    "license_no": "LIC123456",
    "amu_pay_code": "AMU001",
    "saraf_address": "Street 123, Kabul",
    "province": "Kabul",
    "password": "SecurePass123!"
}
```

### Expected Response (Success - 200 OK)
```json
{
    "message": "Registration data received. Please check your email for OTP verification.",
    "email": "ahmad@example.com",
    "otp_sent": true,
    "requires_verification": true,
    "message_note": "Your account will be created after OTP verification."
}
```

### Expected Response (Error - Duplicate Email)
```json
{
    "error": "Email already exists."
}
```

### Important Notes
- ✅ **Saraf account is NOT saved to database yet**
- ✅ **Files are saved temporarily**
- ✅ **Check your email for OTP code**
- ✅ **Registration data stored in cache for 15 minutes**

---

## Saraf OTP Verification

### Endpoint
```
POST http://your-server-ip/api/saraf/otp/verify/
```
or
```
POST http://localhost:8000/api/saraf/otp/verify/
```

### Headers
```
Content-Type: application/json
```

### Request Body (JSON)
```json
{
    "email": "ahmad@example.com",
    "otp_code": "123456"
}
```

### Expected Response (Success - 201 Created)
```json
{
    "message": "Email OTP verified successfully. Your account is now active.",
    "saraf_id": 1,
    "email": "ahmad@example.com",
    "whatsapp_number": "0790123456",
    "verified": true,
    "is_active": true,
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Expected Response (Error - Invalid OTP)
```json
{
    "error": "Invalid OTP code"
}
```

### Expected Response (Error - Expired Session)
```json
{
    "error": "Registration session expired or not found. Please register again."
}
```

### Important Notes
- ✅ **Saraf account is created in database ONLY after successful verification**
- ✅ **JWT tokens are returned for immediate login**
- ✅ **Files are moved from temp to permanent location**

---

## Saraf Resend OTP

### Endpoint
```
POST http://your-server-ip/api/saraf/otp/resend/
```
or
```
POST http://localhost:8000/api/saraf/otp/resend/
```

### Headers
```
Content-Type: application/json
```

### Request Body (JSON)
```json
{
    "email": "ahmad@example.com"
}
```

### Expected Response (Success - 200 OK)
```json
{
    "message": "New OTP sent to your email. Please check your inbox.",
    "email": "ahmad@example.com",
    "otp_type": "email"
}
```

---

## Testing Scenarios

### ✅ Scenario 1: Complete Registration Flow (Success)

1. **Register Normal User**
   - POST `/api/normal-user/register/`
   - Check email for OTP code
   - ✅ User NOT in database/admin panel

2. **Verify OTP**
   - POST `/api/normal-user/verify-otp/` with correct OTP
   - ✅ User created in database
   - ✅ Account is active

3. **Try to Register Again with Same Email**
   - POST `/api/normal-user/register/` with same email
   - ✅ Should get error: "An account with this email already exists"

### ✅ Scenario 2: Registration Without OTP Verification

1. **Register User**
   - POST `/api/normal-user/register/`
   - ✅ User NOT in database

2. **Wait 15+ minutes OR Don't verify OTP**
   - ✅ Registration session expires

3. **Try to Register Again with Same Email**
   - POST `/api/normal-user/register/` with same email
   - ✅ Should work (no duplicate error)
   - ✅ Can register again because previous data expired

### ✅ Scenario 3: Invalid OTP

1. **Register User**
   - POST `/api/normal-user/register/`
   - Get OTP from email (e.g., "123456")

2. **Verify with Wrong OTP**
   - POST `/api/normal-user/verify-otp/` with "000000"
   - ✅ Should get error: "Invalid OTP code"
   - ✅ User still NOT in database

3. **Resend OTP**
   - POST `/api/normal-user/resend-otp/`
   - ✅ New OTP sent

4. **Verify with Correct OTP**
   - POST `/api/normal-user/verify-otp/` with new OTP
   - ✅ User created successfully

### ✅ Scenario 4: Expired OTP

1. **Register User**
   - POST `/api/normal-user/register/`
   - Get OTP from email

2. **Wait 10+ minutes** (OTP expires)

3. **Try to Verify OTP**
   - POST `/api/normal-user/verify-otp/` with expired OTP
   - ✅ Should get error: "OTP expired. Please register again."

4. **Register Again**
   - POST `/api/normal-user/register/` with same email
   - ✅ Should work (previous session expired)

### ✅ Scenario 5: Resend OTP During Registration

1. **Register User**
   - POST `/api/normal-user/register/`
   - Get first OTP

2. **Resend OTP**
   - POST `/api/normal-user/resend-otp/`
   - ✅ New OTP sent (old one invalidated)

3. **Verify with New OTP**
   - POST `/api/normal-user/verify-otp/` with new OTP
   - ✅ User created successfully

### ✅ Scenario 6: Saraf Registration with Files

1. **Register Saraf with Files**
   - POST `/api/saraf/register/` (multipart/form-data)
   - Include: saraf_logo, front_id_card, back_id_card
   - ✅ Files saved temporarily

2. **Verify OTP**
   - POST `/api/saraf/otp/verify/` with correct OTP
   - ✅ Saraf account created
   - ✅ Files moved to permanent location
   - ✅ JWT tokens returned

---

## Postman Collection Setup

### Step 1: Create Environment Variables

Create a Postman environment with these variables:

```
base_url: http://localhost:8000
# OR
base_url: http://your-aws-server-ip

test_email: test@example.com
test_otp: (will be filled from email)
```

### Step 2: Create Collection Structure

```
📁 Registration Testing
  📁 Normal User
    📄 Register
    📄 Verify OTP
    📄 Resend OTP
  📁 Saraf
    📄 Register
    📄 Verify OTP
    📄 Resend OTP
```

### Step 3: Use Variables in Requests

In your requests, use:
```
{{base_url}}/api/normal-user/register/
```

### Step 4: Extract OTP from Response (Optional)

You can create a test script to extract OTP if you're using a test email service:

```javascript
// In Register request's Tests tab
pm.test("OTP sent", function () {
    var jsonData = pm.response.json();
    pm.environment.set("test_otp", "123456"); // Replace with actual OTP from email
});
```

---

## Common Issues & Solutions

### Issue 1: "Registration session expired"
**Solution:** Register again - the previous session expired after 15 minutes

### Issue 2: "Email already exists"
**Solution:** 
- Check if account was already created
- Or wait 15 minutes for cache to expire
- Or use a different email

### Issue 3: "Invalid OTP code"
**Solution:**
- Check email for correct OTP
- OTP expires after 10 minutes
- Resend OTP if needed

### Issue 4: Files not uploading (Saraf)
**Solution:**
- Use `multipart/form-data` content type
- In Postman, use "form-data" tab, not "raw"
- Select "File" type for file fields

---

## Quick Test Checklist

- [ ] Normal User Registration (without OTP) → User NOT in database
- [ ] Normal User OTP Verification → User created in database
- [ ] Try to register again with same email → Error (after verification)
- [ ] Register without verifying → Wait 15 min → Register again → Should work
- [ ] Invalid OTP → Error, user still NOT in database
- [ ] Resend OTP → New OTP sent
- [ ] Saraf Registration → Account NOT in database
- [ ] Saraf OTP Verification → Account created, JWT tokens returned
- [ ] Check Admin Panel → Only verified users should appear

---

## Database Verification

After testing, verify in Django admin or database:

```sql
-- Check Normal Users
SELECT * FROM normal_user_account_normaluser WHERE email = 'test@example.com';

-- Check Saraf Accounts
SELECT * FROM saraf_account_sarafaccount WHERE email = 'test@example.com';
```

**Expected:**
- ✅ Users should only exist AFTER OTP verification
- ✅ Users registered but not verified should NOT exist

---

## Email Testing

If you're testing locally, check your email console output or mail logs:

```python
# Django settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will print emails to console instead of sending them.

---

## Tips

1. **Use different emails** for each test to avoid conflicts
2. **Check email immediately** after registration (OTP expires in 10 min)
3. **Use Postman's Collection Runner** to automate testing
4. **Save responses** to variables for chained requests
5. **Use environment variables** for base URL to switch between local/AWS

---

## Example Postman Collection JSON

You can import this into Postman:

```json
{
    "info": {
        "name": "AMU Pay Registration Testing",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Normal User Register",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"full_name\": \"Test User\",\n    \"email\": \"test@example.com\",\n    \"email_or_whatsapp\": \"0790123456\",\n    \"password\": \"TestPass123!\",\n    \"repeat_password\": \"TestPass123!\"\n}"
                },
                "url": {
                    "raw": "{{base_url}}/api/normal-user/register/",
                    "host": ["{{base_url}}"],
                    "path": ["api", "normal-user", "register", ""]
                }
            }
        },
        {
            "name": "Normal User Verify OTP",
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": "{\n    \"email\": \"test@example.com\",\n    \"otp_code\": \"{{test_otp}}\"\n}"
                },
                "url": {
                    "raw": "{{base_url}}/api/normal-user/verify-otp/",
                    "host": ["{{base_url}}"],
                    "path": ["api", "normal-user", "verify-otp", ""]
                }
            }
        }
    ]
}
```

---

Happy Testing! 🚀

