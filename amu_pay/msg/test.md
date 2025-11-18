# Messaging App API Testing Guide

## Overview
Complete testing guide for the messaging app APIs. This guide covers all endpoints with detailed examples and expected responses.

## Prerequisites
1. **Django Server Running**: Make sure your Django server is running on `http://localhost:8000`
2. **Postman Installed**: Download and install Postman
3. **Database Migrated**: Ensure all migrations are applied (`python manage.py migrate`)

## Quick Setup Summary

1. **Create Saraf Accounts**: Use `POST /api/saraf/register/` to create test accounts
2. **Create Employees** (Optional): Use `POST /api/saraf/employees/` for employee testing
3. **Get JWT Token**: Use `POST /api/saraf/login/` to authenticate
4. **Start Testing**: Use the messaging endpoints with your JWT token

## Setup Steps

### 1. Create Test Saraf Accounts

**Endpoint:** `POST http://localhost:8000/api/saraf/register/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON) - Account 1:**
```json
{
    "full_name": "Test Saraf 11",
    "exchange_name": "Test Exchange 11",
    "email": "test1@example.com1",
    "license_no": "LIC0011",
    "amu_pay_code": "TEST0011",
    "province": "Test Province1",
    "password": "TestPass123!1"
}
```

**Body (JSON) - Account 2:**
```json
{
    "full_name": "Test Saraf 2",
    "exchange_name": "Test Exchange 2",
    "email": "test2@example.com",
    "license_no": "LIC002",
    "amu_pay_code": "TEST002",
    "province": "Test Province",
    "password": "TestPass123!"
}
```

**Expected Response:**
```json
{
    "message": "Saraf account created successfully",
    "saraf_id": 1,
    "full_name": "Test Saraf 1",
    "email": "test1@example.com",
    "exchange_name": "Test Exchange 1"
}
```

### 2. Create Test Employees (Optional)

**Endpoint:** `POST http://localhost:8000/api/saraf/employees/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON) - Employee 1:**
```json
{
    "email_or_phone": "test1@example.com",
    "full_name": "Test Employee 1",
    "password": "TestPass123!"
}
```

**Body (JSON) - Employee 2:**
```json
{
    "email_or_phone": "test1@example.com",
    "full_name": "Test Employee 2",
    "password": "TestPass123!"
}
```

**Expected Response:**
```json
{
    "message": "Employee created successfully.",
    "employee": {
        "employee_id": 1,
        "username": "test_employee_1",
        "full_name": "Test Employee 1",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

**Note:** The system automatically generates a unique username based on the employee's full name. If multiple employees have the same name, numbers are added (e.g., "test_employee_1", "test_employee_1_1").

### 3. Get JWT Authentication Token

**Endpoint:** `POST http://localhost:8000/api/saraf/login/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "email_or_phone": "test1@example.com",
    "password": "TestPass123!"
}
```

**Expected Response:**
```json
{
    "message": "Login successful",
    "user_type": "saraf",
    "user_id": 1,
    "full_name": "Test Saraf 1",
    "email": "test1@example.com",
    "phone": null,
    "exchange_name": "Test Exchange 1",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Save the `access` token for all subsequent requests!**

#### Alternative: Employee Login (if you created employees)

**Endpoint:** `POST http://localhost:8000/api/saraf/login/`

**Body (JSON):**
```json
{
    "email_or_phone": "test1@example.com",
    "username": "employee1",
    "password": "TestPass123!"
}
```

---

## API Testing Endpoints

### 1. List Conversations

**Endpoint:** `GET http://localhost:8000/api/messages/conversations/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Query Parameters (Optional):**
- `page`: 1
- `page_size`: 20

**Expected Response:**
```json
{
    "conversations": [
        {
            "conversation_id": 1,
            "conversation_type": "direct",
            "title": "Test Saraf 1 - Test Saraf 2",
            "participants": ["Test Saraf 1", "Test Saraf 2"],
            "participant_names": "Test Saraf 1, Test Saraf 2",
            "last_message": {
                "message_id": 1,
                "content": "Hello!",
                "message_type": "text",
                "sender_display_name": "Test Saraf 1",
                "created_at": "2024-01-15T10:30:00Z"
            },
            "unread_count": 0,
            "is_active": true,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    ],
    "pagination": {
        "current_page": 1,
        "total_pages": 1,
        "total_count": 1,
        "has_next": false,
        "has_previous": false
    }
}
```

---

### 2. Create Conversation

**Endpoint:** `POST http://localhost:8000/api/messages/conversations/create/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "title": "My Conversation",
    "participant_ids": [2]
}
```

**Note:** You only need to specify the **other participant's ID**. The system automatically adds the current user (you) to the conversation, making it a direct conversation between 2 participants.

**How it works:**
1. You provide `participant_ids: [2]` (the other person's ID)
2. System adds your ID automatically (e.g., if you're saraf_id=1, it becomes `[2, 1]`)
3. Creates a direct conversation between you and the other participant
4. Both participants can now send messages to each other

**Expected Response:**
```json
{
    "conversation_id": 1,
    "conversation_type": "direct",
    "title": "My Conversation",
    "participants": ["Test Saraf 1", "Test Saraf 2"],
    "participant_names": "Test Saraf 1, Test Saraf 2",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### 3. Get Conversation Details

**Endpoint:** `GET http://localhost:8000/api/messages/conversations/{conversation_id}/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Query Parameters (Optional):**
- `page`: 1
- `page_size`: 20

**Example:** `GET http://localhost:8000/api/messages/conversations/1/`

**Expected Response:**
```json
{
    "conversation": {
        "conversation_id": 1,
        "conversation_type": "direct",
        "title": "My Conversation",
        "participants": ["Test Saraf 1", "Test Saraf 2"],
        "participant_names": "Test Saraf 1, Test Saraf 2",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    },
    "messages": [
        {
            "message_id": 1,
            "content": "Hello!",
            "message_type": "text",
            "attachment": null,
            "sender_display_name": "Test Saraf 1",
            "sender_employee_name": null,
            "file_size": null,
            "created_at": "2024-01-15T10:30:00Z",
            "deliveries": [
                {
                    "delivery_id": 1,
                    "recipient_name": "Test Saraf 2",
                    "delivery_status": "sent",
                    "sent_at": "2024-01-15T10:30:00Z",
                    "delivered_at": null,
                    "read_at": null
                }
            ]
        }
    ],
    "pagination": {
        "current_page": 1,
        "total_pages": 1,
        "total_count": 1,
        "has_next": false,
        "has_previous": false
    }
}
```

---

### 4. Send Text Message

**Endpoint:** `POST http://localhost:8000/api/messages/messages/send/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "conversation_id": 1,
    "content": "Hello! This is a test message.",
    "message_type": "text"
}
```

**Expected Response:**
```json
{
    "message_id": 1,
    "content": "Hello! This is a test message.",
    "message_type": "text",
    "attachment": null,
    "sender_display_name": "Test Saraf 1",
    "sender_employee_name": null,
    "file_size": null,
    "created_at": "2024-01-15T10:35:00Z",
    "deliveries": [
        {
            "delivery_id": 1,
            "recipient_name": "Test Saraf 2",
            "delivery_status": "sent",
            "sent_at": "2024-01-15T10:35:00Z",
            "delivered_at": null,
            "read_at": null
        }
    ]
}
```

---

### 5. Send Image Message

**Endpoint:** `POST http://localhost:8000/api/messages/messages/send/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: multipart/form-data
```

**Body (Form Data):**
- `conversation_id`: `1` (Text)
- `content`: `Check out this image!` (Text)
- `message_type`: `image` (Text)
- `attachment`: [Select your image file] (File)

**Note:** When using `multipart/form-data`, ensure all text fields are properly formatted as strings. The `content` field should be a plain text string, not a file or binary data.

**Important:** Some clients may send form data fields as arrays. The system automatically handles this by taking the first element of any array values.

**Debug Information:** If you're still getting validation errors, check the Django server console for debug output that shows exactly what data is being received and processed.

**Expected Response:**
```json
{
    "message_id": 2,
    "content": "Check out this image!",
    "message_type": "image",
    "attachment": "/media/message_files/1/image.jpg",
    "sender_display_name": "Test Saraf 1",
    "sender_employee_name": null,
    "file_size": "2.5 MB",
    "created_at": "2024-01-15T10:40:00Z",
    "deliveries": [
        {
            "delivery_id": 2,
            "recipient_name": "Test Saraf 2",
            "delivery_status": "sent",
            "sent_at": "2024-01-15T10:40:00Z",
            "delivered_at": null,
            "read_at": null
        }
    ]
}
```

---

### 6. Send Audio Message

**Endpoint:** `POST http://localhost:8000/api/messages/messages/send/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: multipart/form-data
```

**Body (Form Data):**
- `conversation_id`: `1` (Text)
- `content`: `Voice message` (Text)
- `message_type`: `audio` (Text)
- `attachment`: [Select your audio file] (File)

**Expected Response:**
```json
{
    "message_id": 3,
    "content": "Voice message",
    "message_type": "audio",
    "attachment": "/media/message_files/1/audio.mp3",
    "sender_display_name": "Test Saraf 1",
    "sender_employee_name": null,
    "file_size": "1.2 MB",
    "created_at": "2024-01-15T10:45:00Z",
    "deliveries": [
        {
            "delivery_id": 3,
            "recipient_name": "Test Saraf 2",
            "delivery_status": "sent",
            "sent_at": "2024-01-15T10:45:00Z",
            "delivered_at": null,
            "read_at": null
        }
    ]
}
```

---

### 7. Send Message as Employee (Automatic Detection)

**Endpoint:** `POST http://localhost:8000/api/messages/messages/send/`

**Headers:**
```
Authorization: Bearer EMPLOYEE_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "conversation_id": 1,
    "content": "Message sent by employee",
    "message_type": "text"
}
```

**Expected Response:**
```json
{
    "message_id": 4,
    "content": "Message sent by employee",
    "message_type": "text",
    "attachment": null,
    "sender_display_name": "Test Saraf 1",
    "sender_employee_name": "Test Employee 1",
    "file_size": null,
    "created_at": "2024-01-15T10:50:00Z",
    "deliveries": [
        {
            "delivery_id": 4,
            "recipient_name": "Test Saraf 2",
            "delivery_status": "sent",
            "sent_at": "2024-01-15T10:50:00Z",
            "delivered_at": null,
            "read_at": null
        }
    ]
}
```

**Note:** When an employee logs in and sends a message, the system automatically detects the employee and includes their name in the response. No need to manually specify `employee_id`.

---

### 8. Send Message as Employee (Manual Override)

**Endpoint:** `POST http://localhost:8000/api/messages/messages/send/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "conversation_id": 1,
    "content": "Message sent by specific employee",
    "message_type": "text",
    "employee_id": 1
}
```

**Note:** You can also manually specify which employee sent the message by including `employee_id` in the request.

---

### 9. Update Message Status

**Endpoint:** `PATCH http://localhost:8000/api/messages/messages/{message_id}/status/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "delivery_status": "read"
}
```

**Example:** `PATCH http://localhost:8000/api/messages/messages/1/status/`

**Expected Response:**
```json
{
    "message": "Status updated successfully"
}
```

**Important Notes:**
- **Only recipients can update message status** - senders cannot update delivery status for their own messages
- **Message must exist** and the user must be a recipient of that message
- **Valid status values**: `sent`, `delivered`, `read`

**Common Errors:**
- `"You cannot update delivery status for messages you sent"` - You're trying to update status for a message you sent
- `"Message not found or you are not authorized to update its status"` - Message doesn't exist or you're not a participant

---

### 10. Search Messages

**Endpoint:** `GET http://localhost:8000/api/messages/messages/search/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Query Parameters:**
- `q`: "test" (search query)
- `page`: 1 (optional)
- `page_size`: 20 (optional)

**Example:** `GET http://localhost:8000/api/messages/messages/search/?q=test`

**Expected Response:**
```json
{
    "messages": [
        {
            "message_id": 1,
            "content": "Hello! This is a test message.",
            "message_type": "text",
            "attachment": null,
            "sender_display_name": "Test Saraf 1",
            "sender_employee_name": null,
            "file_size": null,
            "created_at": "2024-01-15T10:35:00Z",
            "deliveries": [...]
        }
    ],
    "query": "test",
    "pagination": {
        "current_page": 1,
        "total_pages": 1,
        "total_count": 1,
        "has_next": false,
        "has_previous": false
    }
}
```

---

### 11. Get Message Statistics

**Endpoint:** `GET http://localhost:8000/api/messages/messages/stats/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Expected Response:**
```json
{
    "total_conversations": 1,
    "total_messages_sent": 5,
    "unread_messages": 2,
    "messages_by_type": [
        {
            "message_type": "text",
            "count": 3
        },
        {
            "message_type": "image",
            "count": 1
        },
        {
            "message_type": "audio",
            "count": 1
        }
    ],
    "recent_messages": [
        {
            "message_id": 5,
            "content": "Latest message",
            "message_type": "text",
            "sender_display_name": "Test Saraf 1",
            "created_at": "2024-01-15T11:00:00Z"
        }
    ]
}
```

---

### 12. Get In-App Notifications

**Endpoint:** `GET http://localhost:8000/api/messages/notifications/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Query Parameters (Optional):**
- `page`: 1
- `page_size`: 20

**Expected Response:**
```json
{
    "notifications": [
        {
            "notification_id": 1,
            "is_read": false,
            "created_at": "2024-01-15T10:35:00Z"
        }
    ],
    "unread_count": 1,
    "pagination": {
        "current_page": 1,
        "total_pages": 1,
        "total_count": 1,
        "has_next": false,
        "has_previous": false
    }
}
```

---

### 13. Mark Notification as Read

**Endpoint:** `PATCH http://localhost:8000/api/messages/notifications/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Expected Response:**
```json
{
    "message": "All notifications marked as read"
}
```

---

## Complete Testing Scenario

### Step-by-Step Testing Flow:

1. **Setup**: Create test Saraf accounts and get JWT token
2. **Create Conversation**: Create a conversation between two users
3. **Send Messages**: Send text, image, and audio messages
4. **Test Employee Messages**: Send messages with employee tracking
5. **Test Search**: Search for messages
6. **Test Notifications**: Check and manage notifications
7. **Test Statistics**: View message statistics
8. **Test Status Updates**: Update message delivery status

### Error Testing

Test these error scenarios:

1. **Invalid Token**: Use expired or invalid JWT token
2. **Missing Fields**: Send requests with missing required fields
3. **Invalid File Types**: Try uploading unsupported file formats
4. **Non-existent Resources**: Try accessing non-existent conversations/messages
5. **Permission Errors**: Test with users who don't have chat permission

---

## Common Issues and Solutions

### 1. Authentication Errors (401)
- **Issue**: Invalid or expired JWT token
- **Solution**: Get a new token using the `/api/saraf/login/` endpoint

#### Authentication Troubleshooting:
If you're getting 401 errors, check these:

1. **Token Format**: Ensure your Authorization header is: `Bearer YOUR_TOKEN`
2. **Token Claims**: The JWT token must contain `saraf_id` claim
3. **Token Expiration**: JWT tokens expire - get a fresh one if needed
4. **User Registration**: Make sure the user account exists and is verified

**Debug Steps:**
1. First, create a Saraf account: `POST /api/saraf/register/`
2. Get JWT token: `POST /api/saraf/login/`
3. Check token contains saraf_id in the payload
4. Use token in Authorization header: `Bearer <token>`

### 2. Content Validation Errors (400)
- **Issue**: "not a valid string for content"
- **Solution**: Ensure content field is sent as plain text string, not binary data

#### Content Validation Troubleshooting:
If you're getting content validation errors, check these:

1. **Form Data Format**: When using `multipart/form-data`, ensure content is sent as text, not file
2. **Content Type**: Content should be a string, not binary data or file upload
3. **Empty Content**: Content can be empty string `""` but not `null`
4. **Special Characters**: Ensure content doesn't contain invalid characters
5. **Array Values**: Some clients send form fields as arrays - the system handles this automatically

**Debug Steps:**
1. Use `multipart/form-data` for file uploads
2. Send content as plain text field
3. Ensure attachment is sent as file field
4. Check that content is not accidentally sent as file
5. Verify form data is properly formatted (not as arrays)
6. **Check Django server console** for debug output showing received data
7. **Look for DEBUG messages** that show data type and content

**Debug Output Example:**
When you send a request, you should see output like this in the Django console:
```
DEBUG: Received data type: <class 'django.http.request.QueryDict'>
DEBUG: Received data: <QueryDict: {'conversation_id': ['1'], 'content': ['Check out this image!'], 'message_type': ['image']}>
DEBUG: Processing multipart form data
DEBUG: Field 'conversation_id' value: ['1']
DEBUG: Field 'content' value: ['Check out this image!']
DEBUG: Field 'message_type' value: ['image']
DEBUG: Processed data: {'conversation_id': '1', 'content': 'Check out this image!', 'message_type': 'image', 'attachment': None, 'employee_id': None}
DEBUG: validate_content received: Check out this image! (type: <class 'str'>)
```

### 3. Permission Errors (403)
- **Issue**: User doesn't have chat permission
- **Solution**: Ensure user has 'chat' permission in employee settings

### 4. File Upload Errors (400)
- **Issue**: Invalid file format or size
- **Solution**: Check file type and size limits:
  - **Images**: JPG, JPEG, PNG, GIF
  - **Audio**: MP3, WAV, M4A, AAC
  - **Max Size**: 10MB

### 5. Message Status Update Errors (400/404)
- **Issue**: "Message delivery not found" or "You cannot update delivery status for messages you sent"
- **Solution**: Only recipients can update message delivery status, not senders

#### Message Status Troubleshooting:
If you're getting message status errors, check these:

1. **Sender vs Recipient**: Only message recipients can update delivery status
2. **Message Ownership**: You cannot update status for messages you sent
3. **Message Existence**: Ensure the message exists and you're a participant
4. **Authorization**: You must be a recipient of the message

**Debug Steps:**
1. Check if you're the sender or recipient of the message
2. Verify the message exists in the conversation
3. Ensure you're using the correct message ID
4. Use recipient account to update message status

### 6. Validation Errors (400)
- **Issue**: Missing required fields or invalid data
- **Solution**: Check request body format and required fields

---

## File Upload Guidelines

### Supported File Types:
- **Images**: JPG, JPEG, PNG, GIF
- **Audio**: MP3, WAV, M4A, AAC

### File Size Limits:
- **Maximum**: 10MB per file

### Upload Format:
- **Text Messages**: Use JSON format
- **File Messages**: Use multipart/form-data format

### Example File Upload in Postman:
1. Select `POST` method
2. Set URL: `http://localhost:8000/api/messages/messages/send/`
3. Add Authorization header: `Bearer YOUR_TOKEN`
4. Change Body to `form-data`
5. Add fields:
   - `conversation_id`: `1` (Text)
   - `content`: `Your message` (Text)
   - `message_type`: `image` (Text)
   - `attachment`: [Select File] (File)

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/messages/conversations/` | List conversations |
| POST | `/api/messages/conversations/create/` | Create conversation |
| GET | `/api/messages/conversations/{id}/` | Get conversation details |
| POST | `/api/messages/messages/send/` | Send message |
| PATCH | `/api/messages/messages/{id}/status/` | Update message status |
| GET | `/api/messages/messages/search/` | Search messages |
| GET | `/api/messages/messages/stats/` | Get statistics |
| GET | `/api/messages/notifications/` | Get notifications |
| PATCH | `/api/messages/notifications/` | Mark all notifications as read |
| PATCH | `/api/messages/notifications/{id}/` | Mark notification as read |

---

## Testing Checklist

- [ ] Create Saraf accounts
- [ ] Get JWT authentication token
- [ ] List conversations
- [ ] Create new conversation
- [ ] Get conversation details
- [ ] Send text message
- [ ] Send image message
- [ ] Send audio message
- [ ] Send message as employee
- [ ] Update message status
- [ ] Search messages
- [ ] Get message statistics
- [ ] Get notifications
- [ ] Mark notification as read
- [ ] Mark all notifications as read
- [ ] Test error scenarios
- [ ] Test file upload limits
- [ ] Test employee tracking functionality

---

## 🔍 **Employee Tracking Features**

### **Automatic Employee Detection**
- When an employee logs in, the system automatically detects their identity
- All actions (messages, conversations, etc.) include the employee's name
- No need to manually specify employee information

### **Message Tracking**
- **Saraf Name**: Shows the Saraf account name (e.g., "Test Saraf 1")
- **Employee Name**: Shows the specific employee name (e.g., "Test Employee 1")
- **Action Logs**: All actions are logged with employee information

### **Example Employee Message Response:**
```json
{
    "message_id": 4,
    "content": "Message from employee",
    "sender_display_name": "Test Saraf 1",      // Saraf account name
    "sender_employee_name": "Test Employee 1",    // Employee name
    "created_at": "2024-01-15T10:50:00Z"
}
```

### **Action Logging**
All employee actions are logged with:
- **User Type**: "employee"
- **User ID**: Employee ID
- **User Name**: Employee full name
- **Description**: Includes employee name in action description

---

## 🚀 **Quick Test Flow**

1. **Create Saraf Account** → Get Saraf Token
2. **Create Employee** → Employee gets Saraf-level permissions
3. **Employee Login** → Get Employee Token (with employee info)
4. **Send Message as Employee** → System automatically includes employee name
5. **Check Messages** → See both Saraf and Employee names

---

## 📝 **Notes**

- **Employee Permissions**: Employees have full Saraf-level permissions
- **Automatic Tracking**: Employee identity is automatically detected from JWT token
- **Action Logging**: All actions include employee information for audit trails
- **Message Attribution**: Messages show both Saraf account and specific employee names
- **No Manual Override Needed**: System handles employee detection automatically

---

**Happy Testing! 🎉**
- [ ] Test authentication errors
- [ ] Test permission errors

---

This comprehensive testing guide covers all messaging app APIs with detailed examples, expected responses, and troubleshooting tips. Use this guide to thoroughly test your messaging system!
