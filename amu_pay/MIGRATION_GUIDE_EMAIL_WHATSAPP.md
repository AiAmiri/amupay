# 📋 Email + WhatsApp Field Migration Guide

## 🎯 **Overview**

The Normal User and Saraf Account models have been updated to require BOTH email and WhatsApp fields:

### **Before (Old Structure)**
- User provides EITHER email OR WhatsApp number
- Field name in API: `email_or_whatsapp`
- Stored in: `email` OR `whatsapp_number` (one of them null)

### **After (New Structure)**  
- User provides BOTH email AND WhatsApp number
- Field names in API: `email` + `email_or_whatsapp` (for whatsapp)
- Stored in: `email` AND `whatsapp_number` (both required)
- **OTP**: Sent ONLY to email (WhatsApp OTP disabled - Twilio removed)

---

## 🔄 **Changes Made**

### **1. Normal User Account**

#### **Model Changes** (`normal_user_account/models.py`)
```python
# OLD
email = models.EmailField(max_length=128, unique=True, null=True, blank=True)
whatsapp_number = models.CharField(..., null=True, blank=True)

# NEW
email = models.EmailField(max_length=128, unique=True)  # Required for OTP
whatsapp_number = models.CharField(..., unique=True)    # Required but no OTP
```

#### **Serializer Changes** (`normal_user_account/serializers.py`)
```python
# Registration Serializer - NEW
class NormalUserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)  # NEW: Separate email field
    email_or_whatsapp = serializers.CharField(required=True)  # For WhatsApp only
    password = serializers.CharField(write_only=True)
    repeat_password = serializers.CharField(write_only=True)
```

#### **API Changes**
**Registration Endpoint**: `POST /api/normal-user/register/`
```json
{
  "full_name": "Ahmad Khan",
  "email": "ahmad@example.com",           // NEW: Required for OTP
  "email_or_whatsapp": "+93790976268",   // Required (WhatsApp only, no email)
  "password": "SecurePass123!",
  "repeat_password": "SecurePass123!"
}
```

**OTP Verification Endpoint**: `POST /api/normal-user/verify-otp/`
```json
{
  "email": "ahmad@example.com",  // Uses email (not email_or_whatsapp)
  "otp_code": "123456"
}
```

**Login Endpoint**: `POST /api/normal-user/login/` (NO CHANGE)
```json
{
  "email_or_whatsapp": "ahmad@example.com",  // Can use EITHER email OR whatsapp
  "password": "SecurePass123!"
}
```

**Forgot Password**: `POST /api/normal-user/forgot-password/`
```json
{
  "email": "ahmad@example.com"  // Email only (not email_or_whatsapp)
}
```

---

### **2. Saraf Account** (Similar Changes Needed)

The same pattern needs to be applied to Saraf accounts. Currently:
- `SarafAccount` has `email_or_whatsapp_number` field
- Needs to be split into `email` (required, for OTP) + keep `email_or_whatsapp_number` (required, for WhatsApp)

---

## ⚠️ **Migration Issues & Solutions**

### **Problem**: Existing users have EITHER email OR whatsapp (not both)

The migration will fail because existing records don't have both fields populated.

### **Solution Options**:

#### **Option 1: Delete Existing Test Data** (Easiest)
```bash
python manage.py shell
>>> from normal_user_account.models import NormalUser
>>> NormalUser.objects.all().delete()
>>> exit()
python manage.py migrate normal_user_account
```

#### **Option 2: Add Default WhatsApp Numbers** (For existing users)
Create a custom data migration:
```python
# migrations/0005_populate_missing_fields.py
def populate_whatsapp(apps, schema_editor):
    NormalUser = apps.get_model('normal_user_account', 'NormalUser')
    for user in NormalUser.objects.filter(whatsapp_number__isnull=True):
        # Add a placeholder WhatsApp number
        user.whatsapp_number = f'+93700000{user.user_id:04d}'
        user.save()
```

#### **Option 3: Make Fields Temporarily Optional**
1. Keep `null=True, blank=True` during migration
2. Manually update existing records
3. Create another migration to make them required

---

## 🧪 **Testing the New Structure**

### **Test Registration**
```bash
curl -X POST "http://localhost:8000/api/normal-user/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "email_or_whatsapp": "+93790976268",
    "password": "TestPass123!",
    "repeat_password": "TestPass123!"
  }'
```

### **Test OTP Verification**
```bash
curl -X POST "http://localhost:8000/api/normal-user/verify-otp/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "otp_code": "123456"
  }'
```

### **Test Login (with Email)**
```bash
curl -X POST "http://localhost:8000/api/normal-user/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_whatsapp": "test@example.com",
    "password": "TestPass123!"
  }'
```

### **Test Login (with WhatsApp)**
```bash
curl -X POST "http://localhost:8000/api/normal-user/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_whatsapp": "+93790976268",
    "password": "TestPass123!"
  }'
```

---

## 📝 **Next Steps**

1. **Decide on migration strategy** (delete test data, or add defaults)
2. **Run migrations**: `python manage.py migrate normal_user_account`
3. **Apply same changes to Saraf Account**
4. **Update documentation**
5. **Update frontend/mobile apps** to send both email + whatsapp
6. **Test all endpoints**

---

## 🔑 **Key Points**

✅ **API field name `email_or_whatsapp` is preserved** (no breaking change for field name)  
✅ **WhatsApp is required but NO OTP** (Twilio disabled)  
✅ **Email is required and receives ALL OTPs**  
✅ **Login supports BOTH email and WhatsApp**  
⚠️ **Existing users need data migration**  
⚠️ **Saraf accounts need same updates**  

---

## 📞 **Support**

If you encounter issues:
1. Check migration errors carefully
2. Backup database before running migrations
3. Test with new users first
4. Update frontend/mobile apps accordingly

