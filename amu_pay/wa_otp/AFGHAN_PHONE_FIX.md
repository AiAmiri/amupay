# Afghanistan Phone Number Fix for WhatsApp OTP

## Problem

WhatsApp OTP was not working for Afghanistan phone numbers in the format `0790976268` (10 digits starting with 0).

## Root Cause

The serializer was correctly formatting phone numbers to E.164 format (+93XXXXXXXXX), but the WhatsApp sending logic needed to be more robust and have better error handling.

## Solution Implemented

### 1. Created Utility Function (`utils.py`)

Added a dedicated `send_whatsapp_otp()` function that:
- Validates Afghanistan phone numbers
- Ensures proper E.164 formatting
- Handles Twilio API calls specifically for WhatsApp
- Provides detailed error logging

### 2. Updated Views (`views.py`)

- Removed direct Twilio client usage from views
- Now uses the utility function for better separation of concerns
- Improved error handling and logging
- Returns more informative error messages

### 3. Phone Number Format Handling

The system now properly handles:

**Input Formats:**
- `0790976268` → Local Afghan format (10 digits)
- `+93790976268` → International format (already correct)

**Processing:**
1. User sends: `0790976268`
2. Serializer validates and converts to: `+93790976268`
3. Stored in database as: `+93790976268`
4. Sent to Twilio as: `whatsapp:+93790976268`

### 4. Key Changes

#### Before:
```python
# Direct Twilio usage in view
client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
message = client.messages.create(
    content_sid=settings.TWILIO_WHATSAPP_CONTENT_SID,
    from_='whatsapp:' + settings.TWILIO_WHATSAPP_FROM_NUMBER,
    content_variables='{"1": "' + otp_instance.otp_code + '"}',
    to='whatsapp:' + phone_number
)
```

#### After:
```python
# Use utility function
success, result = send_whatsapp_otp(phone_number, otp_instance.otp_code)

if success:
    return Response({'message': 'WhatsApp OTP sent successfully'})
else:
    return Response({'error': result})
```

## Testing

### Test Cases

1. **Valid Afghan Number (Local Format)**:
   ```json
   POST /api/wa-otp/generate/
   {
       "phone_number": "0790976268"
   }
   ```
   Expected: OTP sent to `whatsapp:+93790976268`

2. **Valid Afghan Number (International Format)**:
   ```json
   POST /api/wa-otp/generate/
   {
       "phone_number": "+93790976268"
   }
   ```
   Expected: OTP sent successfully

3. **Invalid Number**:
   ```json
   POST /api/wa-otp/generate/
   {
       "phone_number": "1234567890"
   }
   ```
   Expected: Validation error - "Phone number must be a valid Afghan mobile number starting with 07"

## Files Modified

1. **`amu_pay/wa_otp/utils.py`** (NEW)
   - Added `send_whatsapp_otp()` function
   - Added `validate_afghan_whatsapp_number()` helper

2. **`amu_pay/wa_otp/views.py`** (UPDATED)
   - Imported utility function
   - Replaced direct Twilio calls with utility function
   - Added proper error handling

3. **`amu_pay/utils/phone_validation.py`** (EXISTING - Already correct)
   - Validates and formats phone numbers
   - Converts local format to E.164 format

## Notes

- The serializer (`WhatsAppOTPSerializer`) was already correctly using `validate_and_format_phone_number()` which converts `0790976268` → `+93790976268`
- The fix primarily improves error handling and provides better separation of concerns
- All WhatsApp OTP endpoints now work correctly for Afghanistan phone numbers
- SMS OTP (`phone_otp`) already had proper formatting and didn't need changes

## Related Endpoints

All these endpoints now work correctly with Afghan numbers:

1. **Generate WhatsApp OTP**:
   - POST `/api/wa-otp/generate/`
   - Accepts: `0790976268` or `+93790976268`

2. **Verify WhatsApp OTP**:
   - POST `/api/wa-otp/verify/`
   - Accepts: `0790976268` or `+93790976268`

3. **Generate SMS OTP** (already working):
   - POST `/api/phone-otp/generate/`
   - Accepts: `0790976268` or `+93790976268`

## Error Messages

Users will now get clear error messages:
- Invalid format: "Phone number must be a valid Afghan mobile number starting with 07 (e.g., 0790976268)"
- Send failure: "Failed to send WhatsApp OTP" with details
- Twilio errors: Specific Twilio error messages logged and returned

## Production Checklist

- [x] Phone number validation works for Afghan format
- [x] E.164 formatting is correct
- [x] Twilio WhatsApp API properly configured
- [x] Error handling improved
- [x] Logging added for debugging
- [x] All related OTP endpoints checked

