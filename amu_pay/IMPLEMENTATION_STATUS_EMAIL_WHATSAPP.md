# 📊 Implementation Status: Email + WhatsApp Separation

## 🎯 **Goal**

Separate email and WhatsApp fields:
- **API field `email`**: Required, used for all OTP verification
- **API field `email_or_whatsapp`**: Required, WhatsApp number only (no OTP)
- **Login**: Still supports BOTH email OR whatsapp

---

## ✅ **COMPLETED - Normal User Account (100%)**

### **1. Model** ✅
- `email`: Required field, unique, used for OTP
- `whatsapp_number`: Required field, unique, no OTP
- Migration created: `0004_alter_normaluser_email_and_more.py`

### **2. Serializers** ✅
- **Registration**: Requires both `email` + `email_or_whatsapp` (whatsapp)
- **OTP Verification**: Uses `email` only
- **Login**: Accepts `email_or_whatsapp` (can be either)
- **Forgot Password**: Uses `email` only
- **Resend OTP**: Uses `email` only

### **3. Views** ✅
- **Registration**: Sends OTP to email only
- **OTP Verification**: Verifies email only
- **Forgot Password** (3 steps): All use email
- **Resend OTP**: Email only
- **Login**: Supports both email and WhatsApp

### **4. API Examples**

#### Registration
```json
POST /api/normal-user/register/
{
  "full_name": "Ahmad Khan",
  "email": "ahmad@example.com",
  "email_or_whatsapp": "+93790976268",
  "password": "Pass123!",
  "repeat_password": "Pass123!"
}
```

#### OTP Verification
```json
POST /api/normal-user/verify-otp/
{
  "email": "ahmad@example.com",
  "otp_code": "123456"
}
```

#### Login (Email)
```json
POST /api/normal-user/login/
{
  "email_or_whatsapp": "ahmad@example.com",
  "password": "Pass123!"
}
```

#### Login (WhatsApp)
```json
POST /api/normal-user/login/
{
  "email_or_whatsapp": "+93790976268",
  "password": "Pass123!"
}
```

#### Forgot Password (Step 1)
```json
POST /api/normal-user/forgot-password/
{
  "email": "ahmad@example.com"
}
```

---

## ⏳ **IN PROGRESS - Saraf Account (40%)**

### **1. Model** ✅ **COMPLETED**
- `email`: Required field, unique, used for OTP
- `email_or_whatsapp_number`: Required field, unique, WhatsApp only (no OTP)
- Migration created: `0004_remove_sarafaccount_whatsapp_number_and_more.py`

### **2. Serializers** ❌ **NOT STARTED**
Need to update:
- `SarafRegistrationSerializer` - Add separate email field
- `SarafOTPVerificationSerializer` - Use email only
- `SarafLoginSerializer` - Support both email and whatsapp
- `SarafForgotPasswordSerializer` - Use email only
- `SarafResendOTPSerializer` - Use email only

### **3. Views** ❌ **NOT STARTED**
Need to update:
- `SarafAccountRegisterView` - Handle both email + whatsapp
- `SarafOTPVerificationView` - Verify email only
- `ForgotPasswordRequestView` - Use email only
- `ForgotPasswordOTPVerifyView` - Use email only
- `ResetPasswordConfirmView` - No changes needed (token-based)
- `SarafResendOTPView` - Use email only

---

## 📦 **Migrations Created**

### Normal User
```
normal_user_account/migrations/0004_alter_normaluser_email_and_more.py
- Alter field email on normaluser (make required)
- Alter field whatsapp_number on normaluser (make required)
```

### Saraf Account
```
saraf_account/migrations/0004_remove_sarafaccount_whatsapp_number_and_more.py
- Remove field whatsapp_number from sarafaccount
- Alter field email on sarafaccount (make required)
- Alter field email_or_whatsapp_number on sarafaccount (make required, WhatsApp only)
```

---

## ⚠️ **BEFORE Running Migrations**

**IMPORTANT**: Existing users have either email OR whatsapp (not both). Migrations will fail!

### **Option 1: Delete Test Data** (Recommended for dev)
```bash
python manage.py shell
>>> from normal_user_account.models import NormalUser
>>> from saraf_account.models import SarafAccount
>>> NormalUser.objects.all().delete()
>>> SarafAccount.objects.all().delete()
>>> exit()
python manage.py migrate
```

### **Option 2: Add Missing Fields Manually**
Before running migrations, manually update existing records to have both email AND whatsapp.

---

## 🔄 **API Changes Summary**

| Endpoint | Old Field | New Fields | Notes |
|----------|-----------|------------|-------|
| Registration | `email_or_whatsapp` | `email` + `email_or_whatsapp` | Both required |
| OTP Verification | `email_or_whatsapp` | `email` | Email only |
| Login | `email_or_whatsapp` | `email_or_whatsapp` | No change |
| Forgot Password | `email_or_whatsapp` | `email` | Email only |
| Resend OTP | `email_or_whatsapp` | `email` + `otp_type` | Email only |

---

## 📝 **Next Steps**

### **For Normal Users** ✅ READY TO TEST
1. Delete existing test users (or add WhatsApp numbers)
2. Run migration: `python manage.py migrate normal_user_account`
3. Test registration with both email + whatsapp
4. Test OTP verification with email
5. Test login with email
6. Test login with WhatsApp
7. Test forgot password flow

### **For Saraf Accounts** ⏳ NEEDS MORE WORK
1. Update all Saraf serializers (10 serializers to update)
2. Update all Saraf views (8+ views to update)
3. Create/update migration
4. Delete existing test Saraf accounts
5. Run migrations
6. Test all endpoints

---

## 📂 **Files Modified**

### ✅ Normal User (Complete)
- `normal_user_account/models.py`
- `normal_user_account/serializers.py`
- `normal_user_account/views.py`
- `normal_user_account/migrations/0004_alter_normaluser_email_and_more.py`

### ⏳ Saraf Account (Partial)
- `saraf_account/models.py` ✅
- `saraf_account/serializers.py` ❌ TODO
- `saraf_account/views.py` ❌ TODO
- `saraf_account/migrations/0004_remove_sarafaccount_whatsapp_number_and_more.py` ✅

### 📖 Documentation
- `MIGRATION_GUIDE_EMAIL_WHATSAPP.md` ✅
- `IMPLEMENTATION_STATUS_EMAIL_WHATSAPP.md` ✅ (this file)

---

## 🎉 **Current Status: 70% Complete**

**✅ Fully Done:**
- Normal User model, serializers, views, migrations
- Saraf model and migrations
- Documentation

**⏳ Remaining Work:**
- Saraf serializers (est. 30 min)
- Saraf views (est. 45 min)
- Testing (est. 30 min)

**Total Remaining: ~1-2 hours**

---

## 💡 **Key Design Decisions**

1. **Field name `email_or_whatsapp` preserved** - No breaking changes to API field names
2. **Email required for ALL OTP** - WhatsApp is profile-only (Twilio disabled)
3. **Login supports BOTH** - Users can login with email OR WhatsApp
4. **WhatsApp no longer accepts emails** - Validation enforces phone numbers only
5. **Both fields are required** - Cannot register with only email or only WhatsApp

---

## 🔗 **Related Documentation**

- See `MIGRATION_GUIDE_EMAIL_WHATSAPP.md` for detailed migration steps
- See `normal_user_account/README.md` for updated API documentation
- See `saraf_account/README.md` for Saraf API documentation (needs update)

