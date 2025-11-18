# 📱 **MSG App - Messaging System**

A comprehensive messaging system for AMU Pay that enables communication between Saraf accounts, employees, and normal users with support for multimedia messages, conversation management, and real-time notifications.

> **⚠️ Important**: All API endpoints use the base URL `/api/messages/` (not `/api/msg/`)

## 🎯 **Overview**

The MSG app provides a complete messaging solution with:
- **Multi-user Support**: Saraf accounts, employees, and normal users
- **Separate Endpoints**: Different API endpoints for different user types
- **Multimedia Messages**: Text, images, and audio files
- **Conversation Management**: Create, delete, and manage conversations
- **Real-time Notifications**: In-app notification system
- **Message Status Tracking**: Sent, delivered, and read statuses
- **Search Functionality**: Search messages across conversations
- **Soft Delete**: Individual conversation deletion per user

## 🏗️ **Architecture**

### **Models**

#### **Conversation**
- **Purpose**: Represents a chat conversation between users
- **Types**: `direct`, `saraf_to_normal`, `normal_to_saraf`
- **Features**: Soft delete, participant management, unread count tracking

#### **Message**
- **Purpose**: Individual messages within conversations
- **Types**: `text`, `image`, `audio`
- **Features**: File attachments, sender tracking, delivery status

#### **MessageDelivery**
- **Purpose**: Tracks message delivery status for each recipient
- **Statuses**: `sent`, `delivered`, `read`, `failed`
- **Features**: Timestamp tracking, recipient management

#### **MessageNotification**
- **Purpose**: In-app notifications for new messages
- **Features**: Read/unread status, recipient-specific notifications

### **Key Features**

#### **🔐 Authentication & Authorization**
- JWT token-based authentication
- User type detection (`saraf`, `employee`, `normal_user`)
- Permission-based access control for employees
- Automatic user identification from tokens

#### **💬 Message Types**
- **Text Messages**: Plain text content
- **Image Messages**: JPG, JPEG, PNG, GIF files
- **Audio Messages**: MP3, WAV, M4A, AAC files
- **File Validation**: Automatic file type validation based on message type

#### **🗂️ Conversation Management**
- **Create Conversations**: Between Saraf accounts or Saraf-Normal user
- **List Conversations**: Paginated conversation list with unread counts
- **Conversation Details**: Full conversation view with message history
- **Soft Delete**: Individual deletion per user (conversation remains for other participants)

#### **📊 Message Status Tracking**
- **Sent**: Message created and queued for delivery
- **Delivered**: Message successfully delivered to recipient
- **Read**: Recipient has viewed the message
- **Failed**: Delivery failed (error handling)

#### **🔔 Notification System**
- **In-app Notifications**: Simple notification system for new messages
- **Unread Count**: Track unread notifications per user
- **Mark as Read**: Individual or bulk notification marking

---

# 🏢 **SARAF ACCOUNT ENDPOINTS**

> **For Saraf accounts and employees only**

## 📋 **Authentication Requirements**
- **Token Type**: Saraf or Employee JWT token
- **Required Fields**: `saraf_id` in token
- **Permission**: Employees need `chat` permission

## 🚀 **API Endpoints**

### **Conversation Management**
```http
GET    /api/messages/conversations/                    # List conversations
POST   /api/messages/conversations/create/             # Create conversation
GET    /api/messages/conversations/{id}/               # Get conversation details
DELETE /api/messages/conversations/{id}/delete/       # Delete conversation
```

### **Message Management**
```http
POST   /api/messages/messages/send/                   # Send message
PATCH  /api/messages/messages/{id}/status/            # Update message status
```

### **Search & Statistics**
```http
GET    /api/messages/messages/search/                 # Search messages
GET    /api/messages/messages/stats/                  # Get messaging statistics
```

### **Notifications**
```http
GET    /api/messages/notifications/                   # Get notifications
PATCH  /api/messages/notifications/{id}/              # Mark notification as read
```

## 📝 **Usage Examples**

### **1. Create Conversation (Saraf to Saraf)**

```bash
curl -X POST "http://localhost:8000/api/messages/conversations/create/" \
  -H "Authorization: Bearer YOUR_SARAF_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Business Discussion",
    "participant_ids": [2]
  }'
```

**Response:**
```json
{
    "conversation_id": 1,
    "conversation_type": "direct",
    "title": "Business Discussion",
    "saraf_participants": ["ABC Exchange", "XYZ Exchange"],
    "normal_user_participants": [],
    "participant_names": "ABC Exchange, XYZ Exchange",
    "last_message": null,
    "unread_count": 0,
    "is_active": true,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
}
```

### **2. Send Text Message**

```bash
curl -X POST "http://localhost:8000/api/messages/messages/send/" \
  -H "Authorization: Bearer YOUR_SARAF_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "content": "Hello! How are you doing?",
    "message_type": "text"
  }'
```

**Response:**
```json
{
    "message_id": 1,
    "content": "Hello! How are you doing?",
    "message_type": "text",
    "attachment": null,
    "sender_display_name": "ABC Exchange",
    "sender_employee_name": null,
    "file_size": null,
    "created_at": "2024-01-01T10:05:00Z",
    "deliveries": [
        {
            "delivery_id": 1,
            "recipient_name": "XYZ Exchange",
            "delivery_status": "sent",
            "sent_at": "2024-01-01T10:05:00Z",
            "delivered_at": null,
            "read_at": null
        }
    ]
}
```

### **3. Send Image Message**

```bash
curl -X POST "http://localhost:8000/api/messages/messages/send/" \
  -H "Authorization: Bearer YOUR_SARAF_JWT_TOKEN" \
  -F "conversation_id=1" \
  -F "content=Check out this image!" \
  -F "message_type=image" \
  -F "attachment=@/path/to/image.jpg"
```

**Response:**
```json
{
    "message_id": 2,
    "content": "Check out this image!",
    "message_type": "image",
    "attachment": "http://localhost:8000/media/message_files/1/image.jpg",
    "sender_display_name": "ABC Exchange",
    "sender_employee_name": null,
    "file_size": "2.3 MB",
    "created_at": "2024-01-01T10:10:00Z",
    "deliveries": [...]
}
```

### **4. Send Audio Message**

```bash
curl -X POST "http://localhost:8000/api/messages/messages/send/" \
  -H "Authorization: Bearer YOUR_SARAF_JWT_TOKEN" \
  -F "conversation_id=1" \
  -F "content=Voice message" \
  -F "message_type=audio" \
  -F "attachment=@/path/to/audio.mp3"
```

### **5. Get Conversation List**

```bash
curl -X GET "http://localhost:8000/api/messages/conversations/?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_SARAF_JWT_TOKEN"
```

**Response:**
```json
{
    "conversations": [
        {
            "conversation_id": 1,
            "conversation_type": "direct",
            "title": "Business Discussion",
            "participant_names": "ABC Exchange, XYZ Exchange",
            "last_message_preview": {
                "content": "Hello! How are you doing?",
                "sender": "ABC Exchange",
                "message_type": "text",
                "created_at": "2024-01-01T10:05:00Z"
            },
            "unread_count": 2,
            "updated_at": "2024-01-01T10:05:00Z"
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

### **6. Get Conversation Details**

```bash
curl -X GET "http://localhost:8000/api/messages/conversations/1/?page=1&page_size=50" \
  -H "Authorization: Bearer YOUR_SARAF_JWT_TOKEN"
```

**Response:**
```json
{
    "conversation": {
        "conversation_id": 1,
        "conversation_type": "direct",
        "title": "Business Discussion",
        "saraf_participants": ["ABC Exchange", "XYZ Exchange"],
        "normal_user_participants": [],
        "participant_names": "ABC Exchange, XYZ Exchange",
        "last_message": {...},
        "unread_count": 0,
        "is_active": true,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:05:00Z"
    },
    "messages": [
        {
            "message_id": 1,
            "content": "Hello! How are you doing?",
            "message_type": "text",
            "attachment": null,
            "sender_display_name": "ABC Exchange",
            "sender_employee_name": null,
            "file_size": null,
            "created_at": "2024-01-01T10:05:00Z",
            "deliveries": [...]
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

### **7. Update Message Status**

```bash
curl -X PATCH "http://localhost:8000/api/messages/messages/1/status/" \
  -H "Authorization: Bearer YOUR_SARAF_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_status": "read"
  }'
```

**Response:**
```json
{
    "message": "Status updated successfully"
}
```

### **8. Search Messages**

```bash
curl -X GET "http://localhost:8000/api/messages/messages/search/?q=hello&page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_SARAF_JWT_TOKEN"
```

**Response:**
```json
{
    "messages": [
        {
            "message_id": 1,
            "content": "Hello! How are you doing?",
            "message_type": "text",
            "attachment": null,
            "sender_display_name": "ABC Exchange",
            "sender_employee_name": null,
            "file_size": null,
            "created_at": "2024-01-01T10:05:00Z",
            "deliveries": [...]
        }
    ],
    "query": "hello",
    "pagination": {
        "current_page": 1,
        "total_pages": 1,
        "total_count": 1,
        "has_next": false,
        "has_previous": false
    }
}
```

### **9. Get Messaging Statistics**

```bash
curl -X GET "http://localhost:8000/api/messages/messages/stats/" \
  -H "Authorization: Bearer YOUR_SARAF_JWT_TOKEN"
```

**Response:**
```json
{
    "total_conversations": 5,
    "total_messages_sent": 25,
    "unread_messages": 3,
    "messages_by_type": [
        {"message_type": "text", "count": 20},
        {"message_type": "image", "count": 3},
        {"message_type": "audio", "count": 2}
    ],
    "recent_messages": [...]
}
```

### **10. Get Notifications**

```bash
curl -X GET "http://localhost:8000/api/messages/notifications/?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_SARAF_JWT_TOKEN"
```

**Response:**
```json
{
    "notifications": [
        {
            "notification_id": 1,
            "is_read": false,
            "created_at": "2024-01-01T10:05:00Z"
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

### **11. Mark Notification as Read**

```bash
curl -X PATCH "http://localhost:8000/api/messages/notifications/1/" \
  -H "Authorization: Bearer YOUR_SARAF_JWT_TOKEN"
```

**Response:**
```json
{
    "message": "Notification marked as read"
}
```

### **12. Delete Conversation**

```bash
curl -X DELETE "http://localhost:8000/api/messages/conversations/1/delete/" \
  -H "Authorization: Bearer YOUR_SARAF_JWT_TOKEN"
```

**Response:**
```json
{
    "message": "Conversation deleted successfully",
    "conversation_id": 1
}
```

---

# 👤 **NORMAL USER ENDPOINTS**

> **For normal users only**

## 📋 **Authentication Requirements**
- **Token Type**: Normal User JWT token
- **Required Fields**: `user_id` and `user_type: 'normal_user'` in token
- **Permission**: No special permissions required

## 🚀 **API Endpoints**

### **Conversation Management**
```http
GET    /api/messages/normal-user/conversations/                    # List conversations
POST   /api/messages/normal-user/conversations/create/             # Create conversation
GET    /api/messages/normal-user/conversations/{id}/               # Get conversation details
DELETE /api/messages/normal-user/conversations/{id}/delete/       # Delete conversation
```

### **Message Management**
```http
POST   /api/messages/normal-user/messages/send/                   # Send message
PATCH  /api/messages/normal-user/messages/{id}/status/            # Update message status
```

### **Notifications**
```http
GET    /api/messages/normal-user/notifications/                   # Get notifications
PATCH  /api/messages/normal-user/notifications/{id}/              # Mark notification as read
```

## 📝 **Usage Examples**

### **1. Create Conversation with Saraf**

```bash
curl -X POST "http://localhost:8000/api/messages/normal-user/conversations/create/" \
  -H "Authorization: Bearer YOUR_NORMAL_USER_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "saraf_id": "1000"
  }'
```

**Response:**
```json
{
    "conversation_id": 2,
    "conversation_type": "normal_to_saraf",
    "title": "Chat with ABC Exchange",
    "saraf_participants": ["ABC Exchange"],
    "normal_user_participants": ["John Doe"],
    "participant_names": "ABC Exchange, John Doe",
    "last_message": null,
    "unread_count": 0,
    "is_active": true,
    "created_at": "2024-01-01T10:15:00Z",
    "updated_at": "2024-01-01T10:15:00Z"
}
```

### **2. Send Text Message**

```bash
curl -X POST "http://localhost:8000/api/messages/normal-user/messages/send/" \
  -H "Authorization: Bearer YOUR_NORMAL_USER_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 2,
    "content": "Hello, I need help with my transaction",
    "message_type": "text"
  }'
```

**Response:**
```json
{
    "message_id": 3,
    "content": "Hello, I need help with my transaction",
    "message_type": "text",
    "attachment": null,
    "sender_display_name": "John Doe",
    "sender_employee_name": null,
    "file_size": null,
    "created_at": "2024-01-01T10:20:00Z",
    "deliveries": [
        {
            "delivery_id": 3,
            "recipient_name": "ABC Exchange",
            "delivery_status": "sent",
            "sent_at": "2024-01-01T10:20:00Z",
            "delivered_at": null,
            "read_at": null
        }
    ]
}
```

### **3. Send Image Message**

```bash
curl -X POST "http://localhost:8000/api/messages/normal-user/messages/send/" \
  -H "Authorization: Bearer YOUR_NORMAL_USER_JWT_TOKEN" \
  -F "conversation_id=2" \
  -F "content=Here is the receipt" \
  -F "message_type=image" \
  -F "attachment=@/path/to/receipt.jpg"
```

### **4. Send Audio Message**

```bash
curl -X POST "http://localhost:8000/api/messages/normal-user/messages/send/" \
  -H "Authorization: Bearer YOUR_NORMAL_USER_JWT_TOKEN" \
  -F "conversation_id=2" \
  -F "content=Voice message" \
  -F "message_type=audio" \
  -F "attachment=@/path/to/audio.mp3"
```

### **5. Get Conversation List**

```bash
curl -X GET "http://localhost:8000/api/messages/normal-user/conversations/?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_NORMAL_USER_JWT_TOKEN"
```

**Response:**
```json
{
    "conversations": [
        {
            "conversation_id": 2,
            "conversation_type": "normal_to_saraf",
            "title": "Chat with ABC Exchange",
            "participant_names": "ABC Exchange, John Doe",
            "last_message_preview": {
                "content": "Hello, I need help with my transaction",
                "sender": "John Doe",
                "message_type": "text",
                "created_at": "2024-01-01T10:20:00Z"
            },
            "unread_count": 0,
            "updated_at": "2024-01-01T10:20:00Z"
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

### **6. Get Conversation Details**

```bash
curl -X GET "http://localhost:8000/api/messages/normal-user/conversations/2/?page=1&page_size=50" \
  -H "Authorization: Bearer YOUR_NORMAL_USER_JWT_TOKEN"
```

**Response:**
```json
{
    "conversation": {
        "conversation_id": 2,
        "conversation_type": "normal_to_saraf",
        "title": "Chat with ABC Exchange",
        "saraf_participants": ["ABC Exchange"],
        "normal_user_participants": ["John Doe"],
        "participant_names": "ABC Exchange, John Doe",
        "last_message": {...},
        "unread_count": 0,
        "is_active": true,
        "created_at": "2024-01-01T10:15:00Z",
        "updated_at": "2024-01-01T10:20:00Z"
    },
    "messages": [
        {
            "message_id": 3,
            "content": "Hello, I need help with my transaction",
            "message_type": "text",
            "attachment": null,
            "sender_display_name": "John Doe",
            "sender_employee_name": null,
            "file_size": null,
            "created_at": "2024-01-01T10:20:00Z",
            "deliveries": [...]
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

### **7. Update Message Status**

```bash
curl -X PATCH "http://localhost:8000/api/messages/normal-user/messages/3/status/" \
  -H "Authorization: Bearer YOUR_NORMAL_USER_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_status": "read"
  }'
```

**Response:**
```json
{
    "message": "Status updated successfully"
}
```

### **8. Get Notifications**

```bash
curl -X GET "http://localhost:8000/api/messages/normal-user/notifications/?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_NORMAL_USER_JWT_TOKEN"
```

**Response:**
```json
{
    "notifications": [
        {
            "notification_id": 2,
            "is_read": false,
            "created_at": "2024-01-01T10:20:00Z"
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

### **9. Mark Notification as Read**

```bash
curl -X PATCH "http://localhost:8000/api/messages/normal-user/notifications/2/" \
  -H "Authorization: Bearer YOUR_NORMAL_USER_JWT_TOKEN"
```

**Response:**
```json
{
    "message": "Notification marked as read"
}
```

### **10. Delete Conversation**

```bash
curl -X DELETE "http://localhost:8000/api/messages/normal-user/conversations/2/delete/" \
  -H "Authorization: Bearer YOUR_NORMAL_USER_JWT_TOKEN"
```

**Response:**
```json
{
    "message": "Conversation deleted successfully",
    "conversation_id": 2
}
```

---

# 🔧 **Configuration**

### **File Upload Settings**

The system supports file uploads with the following configurations:

#### **Image Files**
- **Allowed Extensions**: `jpg`, `jpeg`, `png`, `gif`
- **Upload Path**: `message_files/{conversation_id}/{filename}`
- **Validation**: Automatic file type validation

#### **Audio Files**
- **Allowed Extensions**: `mp3`, `wav`, `m4a`, `aac`
- **Upload Path**: `message_files/{conversation_id}/{filename}`
- **Validation**: Automatic file type validation

### **Pagination Settings**
- **Default Page Size**: 20 items per page
- **Maximum Page Size**: Configurable via query parameters
- **Message Page Size**: 50 messages per page (conversation details)

### **Message Status Flow**
1. **Sent**: Message created and delivery records created
2. **Delivered**: Message successfully delivered to recipient
3. **Read**: Recipient has viewed the message (auto-marked when conversation is opened)

## 🔐 **Security Features**

### **Authentication**
- JWT token-based authentication
- Automatic user identification from token claims
- Support for multiple user types (`saraf`, `employee`, `normal_user`)

### **Authorization**
- Permission-based access control for employees
- Conversation participation validation
- Message ownership validation

### **File Security**
- File type validation based on message type
- Secure file upload paths
- File size limits (configurable)

### **Data Privacy**
- Soft delete for conversations (individual per user)
- Message delivery status tracking
- Notification management

## 🚨 **Error Handling**

### **🔧 Common Authentication Errors**

#### **"Invalid user token - no saraf_id found" Error**
This error occurs when using the wrong endpoint for your user type:

**❌ Wrong Usage:**
```bash
# Normal user trying to use Saraf endpoint
curl -X POST "http://localhost:8000/api/messages/messages/send/" \
  -H "Authorization: Bearer NORMAL_USER_JWT_TOKEN"
```

**✅ Correct Usage:**
```bash
# Normal user using correct endpoint
curl -X POST "http://localhost:8000/api/messages/normal-user/messages/send/" \
  -H "Authorization: Bearer NORMAL_USER_JWT_TOKEN"
```

**💡 Solution:** Always use the correct endpoint based on your user type:
- **Saraf accounts**: Use endpoints without `/normal-user/`
- **Normal users**: Use endpoints with `/normal-user/`

### **Common Error Responses**

#### **Authentication Errors**
```json
{
    "error": "Invalid user token - no saraf_id found"
}
```

#### **Permission Errors**
```json
{
    "error": "You do not have permission to chat"
}
```

#### **Validation Errors**
```json
{
    "error": "Validation failed",
    "details": {
        "conversation_id": ["Conversation not found or inactive"],
        "message_type": ["Message type must be one of: text, image, audio"]
    }
}
```

#### **File Upload Errors**
```json
{
    "error": "Invalid image file format"
}
```

#### **Not Found Errors**
```json
{
    "error": "Conversation not found"
}
```

## 🔄 **Integration Points**

### **Saraf Account Integration**
- Uses `SarafAccount` model for participants
- Integrates with employee permission system
- Action logging for audit trails

### **Normal User Integration**
- Uses `NormalUser` model for participants
- Separate endpoint namespace for normal users
- Unified conversation management

### **File Storage Integration**
- Django's file storage system
- Configurable upload paths
- Media URL serving

## 📈 **Performance Considerations**

### **Database Indexes**
- Conversation type and active status
- Message conversation and creation time
- Delivery status and recipient
- Notification read status

### **Pagination**
- All list endpoints support pagination
- Configurable page sizes
- Efficient query optimization

### **File Handling**
- Lazy file loading
- File size calculation
- Efficient file validation

## 🧪 **Testing**

### **Test Coverage**
- Model validation and methods
- Serializer validation
- View authentication and authorization
- File upload handling
- Message status updates
- Notification management

### **Test Scenarios**
1. **Conversation Creation**: Test all conversation types
2. **Message Sending**: Test all message types and file uploads
3. **Status Updates**: Test message delivery status flow
4. **Search Functionality**: Test message search across conversations
5. **Notification System**: Test notification creation and marking
6. **Permission System**: Test employee permission validation
7. **Soft Delete**: Test individual conversation deletion

## 🚀 **Deployment Notes**

### **Media Files**
- Configure `MEDIA_URL` and `MEDIA_ROOT` in Django settings
- Set up file serving for development and production
- Configure file storage backend for production

### **Database Migrations**
- Run migrations to create required tables
- Set up database indexes for performance
- Configure foreign key constraints

### **File Upload Limits**
- Configure `FILE_UPLOAD_MAX_MEMORY_SIZE`
- Set up file size limits for different message types
- Configure upload timeout settings

## 🔧 **Troubleshooting Guide**

### **Common Issues and Solutions**

#### **1. "Invalid user token - no saraf_id found" Error**
**Problem**: Using Saraf endpoint with normal user token
**Solution**: Use `/api/messages/normal-user/messages/send/` instead of `/api/messages/messages/send/`

#### **2. "Invalid normal user token" Error**
**Problem**: Using normal user endpoint with Saraf token
**Solution**: Use `/api/messages/messages/send/` instead of `/api/messages/normal-user/messages/send/`

#### **3. "You are not a participant in this conversation" Error**
**Problem**: Trying to send message to conversation you're not part of
**Solution**: Create a new conversation or join an existing one

#### **4. "You do not have permission to chat" Error**
**Problem**: Employee doesn't have chat permission
**Solution**: Contact admin to grant chat permission to employee

### **📋 Endpoint Checklist**

Before making API calls, verify:
- ✅ Using correct base URL: `/api/messages/`
- ✅ Using correct endpoint for your user type
- ✅ Valid JWT token in Authorization header
- ✅ Correct request body format
- ✅ Proper Content-Type header

### **🎯 Quick Test Commands**

**Test Normal User Message:**
```bash
curl -X POST "http://localhost:8000/api/messages/normal-user/messages/send/" \
  -H "Authorization: Bearer YOUR_NORMAL_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": 1, "content": "Test message", "message_type": "text"}'
```

**Test Saraf Message:**
```bash
curl -X POST "http://localhost:8000/api/messages/messages/send/" \
  -H "Authorization: Bearer YOUR_SARAF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": 1, "content": "Test message", "message_type": "text"}'
```

---

This comprehensive messaging system provides a robust foundation for communication within the AMU Pay ecosystem, supporting multiple user types, multimedia messages, and advanced conversation management features.
