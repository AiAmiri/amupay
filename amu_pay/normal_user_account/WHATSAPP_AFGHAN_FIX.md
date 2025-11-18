# WhatsApp OTP Fix for Afghanistan Numbers

## Problem

NormalUser registration with WhatsApp number `0790976268` was failing with error:
```json
{
    "error": "Failed to send verification WhatsApp. Please try again."
}
```

## Root Cause

The `send_otp_whatsapp()` function in `normal_user_account/views.py` was:
1. Not validating/formatting the phone number to E.164 format
2. Sending to Twilio without proper formatting
3. Missing detailed error logging

## Solution

### 1. Updated `send_otp_whatsapp()` Function

**Location**: `amu_pay/normal_user_account/views.py`

**Changes**:
- Added phone number validation and formatting using `validate_and_format_phone_number()`
- Added comprehensive logging at each step
- Added Twilio configuration validation
- Better error handling with detailed error messages

**Flow**:
1. Input: `0790976268` (local Afghan format)
2. Validated and formatted: `+93790976268` (E.164 format)
3. Sent to Twilio as: `whatsapp:+93790976268`

### 2. Updated Registration View

**Location**: `amu_pay/normal_user_account/views.py`

**Changes**:
- Changed to get `email_or_whatsapp` from `serializer.validated_data` instead of `request.data`
- Added logging to track the registration flow

### 3. Existing Validation (Already Working)

The serializer (`NormalUserRegistrationSerializer`) already has proper validation:
- Uses `validate_and_format_phone_number()` utility
- Converts `0790976268` → `+93790976268`
- Stores the formatted number in the database

## Test the Fix

### Test Case 1: NormalUser Registration with WhatsApp

```bash
POST /api/normal-user/register/
Content-Type: application/json

{
    "full_name": "Test User",
    "email_or_whatsapp": "0790976268",
    "password": "Test123!@#",
    "repeat_password": "Test123!@#"
}
```

**Expected Flow**:
1. Serializer validates and formats phone number to `+93790976268`
2. User is created with `whatsapp_number = '+93790976268'`
3. OTP is generated
4. `send_otp_whatsapp('+93790976268', '1234')` is called
5. Number is re-validated and sent to Twilio as `whatsapp:+93790976268`

### Test Case 2: Verify OTP

```bash
POST /api/normal-user/verify-otp/
Content-Type: application/json

{
    "email_or_whatsapp": "0790976268",
    "otp_code": "1234"
}
```

## Logging

The system now logs:
- Initial phone number received
- Formatted phone number
- Twilio configuration check
- Message sending attempt
- Success/failure with error details

Check logs for debugging:
```python
logger.info(f"Phone number formatted: {phone_number} -> {formatted_phone}")
logger.error(f"Failed to send WhatsApp OTP: {str(e)}", exc_info=True)
```

## Files Modified

1. **`amu_pay/normal_user_account/views.py`**
   - Updated `send_otp_whatsapp()` function
   - Added phone number validation
   - Added comprehensive logging
   - Updated registration view to use validated data

2. **`amu_pay/wa_otp/utils.py`** (NEW)
   - Utility function for WhatsApp OTP sending

3. **`amu_pay/wa_otp/views.py`** (Updated)
   - Updated to use utility function

## All WhatsApp OTP Endpoints Fixed

1. ✅ `/api/normal-user/register/` - NormalUser registration
2. ✅ `/api/normal-user/forgot-password/` - Password reset
3. ✅ `/api/normal-user/resend-otp/` - Resend OTP
4. ✅ `/api/wa-otp/generate/` - Direct WhatsApp OTP

All endpoints now properly handle Afghanistan phone numbers:
- Input: `0790976268`
- Internal: `+93790976268`
- Twilio: `whatsapp:+93790976268`

## Error Messages

Users will now get clear errors if:
- Invalid format: Validation error from serializer
- Twilio config missing: "Twilio settings not configured"
- Send failure: "Failed to send verification WhatsApp. Please try again." (with detailed logs)

## Production Checklist

- [x] Phone number validation works for Afghan format
- [x] E.164 formatting is correct
- [x] Twilio WhatsApp API properly configured
- [x] Error handling improved
- [x] Comprehensive logging added
- [x] All related OTP endpoints checked

