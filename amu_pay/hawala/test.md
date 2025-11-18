# AMU Pay API Test Cases for Postman

This document provides comprehensive test cases for all AMU Pay API endpoints using Postman, including Hawala, Messaging, and other core functionalities.

## Prerequisites

1. **Authentication Token**: Obtain a valid JWT token from saraf authentication
2. **Test Data**: Prepare test data for currencies, exchanges, and transactions
3. **Environment Variables**: Set up Postman environment variables

## Environment Variables Setup

Create these variables in Postman:

```
BASE_URL: http://localhost:8000/api/hawala
AUTH_TOKEN: your_jwt_token_here
SARAF_ID: 1
EMPLOYEE_ID: 1
```

## Test Cases

### 1. Get Supported Currencies

**Endpoint**: `GET {{BASE_URL}}/supported-currencies/`

**Headers**:
```
Authorization: Bearer {{AUTH_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "message": "Supported currencies retrieved successfully",
    "currencies": [
        {
            "code": "USD",
            "name": "US Dollar",
            "name_local": "Dollar",
            "symbol": "$",
            "added_at": "2024-01-01T00:00:00Z"
        },
        {
            "code": "AFN",
            "name": "Afghan Afghani",
            "name_local": "Afghani",
            "symbol": "؋",
            "added_at": "2024-01-01T00:00:00Z"
        }
    ],
    "count": 2
}
```

---

### 2. Create Internal Hawala Transaction (Mode 1)

**Endpoint**: `POST {{BASE_URL}}/send/`

**Headers**:
```
Authorization: Bearer {{AUTH_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "hawala_id": "550",
    "hawala_number": "HW001",
    "sender_name": "Ahmad Khan",
    "sender_phone": "+93701234567",
    "receiver_name": "Fatima Ali",
    "receiver_phone": "+93707654321",
    "amount": 1000.00,
    "currency_code": "AFN",
    "transfer_fee": 50.00,
    "destination_exchange_id": 2,
    "destination_exchange_name": "ABC Exchange",
    "destination_exchange_address": "123 Main St, Kabul",
    "destination_saraf_uses_app": true,
    "notes": "Family transfer"
}
```

**Expected Response** (201 Created):
```json
{
    "message": "Hawala transaction created successfully",
    "hawala": {
        "hawala_id": "550e8400-e29b-41d4-a716-446655440000",
        "hawala_number": "HW001",
        "sender_name": "Ahmad Khan",
        "sender_phone": "+93701234567",
        "receiver_name": "Fatima Ali",
        "receiver_phone": "+93707654321",
        "amount": "1000.00",
        "currency": "AFN",
        "currency_code": "AFN",
        "transfer_fee": "50.00",
        "total_amount": "1050.00",
        "status": "pending",
        "mode": "internal",
        "created_at": "2024-01-01T10:00:00Z",
        "supported_currencies": [...]
    }
}
```

---

### 3. Create External Hawala Transaction (Mode 2.1)

**Endpoint**: `POST {{BASE_URL}}/send/`

**Headers**:
```
Authorization: Bearer {{AUTH_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "hawala_id": "550e8400-e29b-41d4-a716-446655440001",
    "hawala_number": "HW002",
    "sender_name": "John Doe",
    "sender_phone": "+1234567890",
    "receiver_name": "Jane Smith",
    "receiver_phone": "+1987654321",
    "amount": 500.00,
    "currency_code": "USD",
    "transfer_fee": 25.00,
    "destination_exchange_name": "XYZ Exchange",
    "destination_exchange_address": "456 Oak St, New York",
    "destination_saraf_uses_app": false,
    "notes": "Business payment"
}
```

**Expected Response** (201 Created):
```json
{
    "message": "Hawala transaction created successfully",
    "hawala": {
        "hawala_id": "550e8400-e29b-41d4-a716-446655440001",
        "hawala_number": "HW002",
        "sender_name": "John Doe",
        "sender_phone": "+1234567890",
        "receiver_name": "Jane Smith",
        "receiver_phone": "+1987654321",
        "amount": "500.00",
        "currency": "USD",
        "currency_code": "USD",
        "transfer_fee": "25.00",
        "total_amount": "525.00",
        "status": "pending",
        "mode": "external_sender",
        "created_at": "2024-01-01T10:30:00Z",
        "supported_currencies": [...]
    }
}
```

---

### 4. Create External Receive Transaction (Mode 2.2)

**Endpoint**: `POST {{BASE_URL}}/external-receive/`

**Headers**:
```
Authorization: Bearer {{AUTH_TOKEN}}
Content-Type: multipart/form-data
```

**Request Body** (Form Data):
```
hawala_id: 550e8400-e29b-41d4-a716-446655440002
hawala_number: HW003
sender_name: External Sender
sender_phone: +1111111111
receiver_name: Local Receiver
receiver_phone: +2222222222
receiver_photo: [FILE UPLOAD]
amount: 750.00
currency_code: EUR
transfer_fee: 37.50
destination_exchange_name: External Exchange
destination_exchange_address: 789 Pine St, London
notes: External transaction
```

**Expected Response** (201 Created):
```json
{
    "message": "External hawala transaction created successfully",
    "hawala": {
        "hawala_id": "550e8400-e29b-41d4-a716-446655440002",
        "hawala_number": "HW003",
        "sender_name": "External Sender",
        "sender_phone": "+1111111111",
        "receiver_name": "Local Receiver",
        "receiver_phone": "+2222222222",
        "amount": "750.00",
        "currency": "EUR",
        "currency_code": "EUR",
        "transfer_fee": "37.50",
        "total_amount": "787.50",
        "status": "received",
        "mode": "external_receiver",
        "created_at": "2024-01-01T11:00:00Z"
    }
}
```

---

### 5. Get Hawala Transaction Details

**Endpoint**: `GET {{BASE_URL}}/detail/{{hawala_id}}/`

**Headers**:
```
Authorization: Bearer {{AUTH_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "message": "Hawala transaction retrieved successfully",
    "hawala": {
        "hawala_id": "550e8400-e29b-41d4-a716-446655440000",
        "hawala_number": "HW001",
        "sender_name": "Ahmad Khan",
        "sender_phone": "+93701234567",
        "receiver_name": "Fatima Ali",
        "receiver_phone": "+93707654321",
        "amount": "1000.00",
        "currency": "AFN",
        "currency_code": "AFN",
        "transfer_fee": "50.00",
        "total_amount": "1050.00",
        "status": "pending",
        "mode": "internal",
        "created_at": "2024-01-01T10:00:00Z",
        "supported_currencies": [...]
    }
}
```

---

### 6. List All Hawalas with Filters

**Endpoint**: `GET {{BASE_URL}}/list-all/`

**Headers**:
```
Authorization: Bearer {{AUTH_TOKEN}}
Content-Type: application/json
```

**Query Parameters**:
```
employee: all
time_range: all
```

**Expected Response** (200 OK):
```json
{
    "message": "Hawala transactions retrieved successfully",
    "hawalas": [
        {
            "hawala_id": "550e8400-e29b-41d4-a716-446655440000",
            "hawala_number": "HW001",
            "sender_name": "Ahmad Khan",
            "receiver_name": "Fatima Ali",
            "amount": "1000.00",
            "transfer_fee": "50.00",
            "total_amount": "1050.00",
            "currency_display": {
                "code": "AFN",
                "name": "Afghan Afghani",
                "symbol": "؋"
            },
            "status": "pending",
            "mode": "internal",
            "created_at": "2024-01-01T10:00:00Z"
        }
    ],
    "count": 1,
    "filters": {
        "employee": "all",
        "time_range": "all"
    }
}
```

---

### 7. List Received Hawalas (Pending Only)

**Endpoint**: `GET {{BASE_URL}}/receive/`

**Headers**:
```
Authorization: Bearer {{AUTH_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "message": "Received hawala transactions retrieved successfully",
    "hawalas": [
        {
            "hawala_id": "550e8400-e29b-41d4-a716-446655440000",
            "hawala_number": "HW001",
            "sender_name": "Ahmad Khan",
            "receiver_name": "Fatima Ali",
            "amount": "1000.00",
            "transfer_fee": "50.00",
            "total_amount": "1050.00",
            "currency_display": {
                "code": "AFN",
                "name": "Afghan Afghani",
                "symbol": "؋"
            },
            "status": "pending",
            "mode": "internal",
            "created_at": "2024-01-01T10:00:00Z"
        }
    ],
    "count": 1
}
```

---

### 8. Update Hawala Status

**Endpoint**: `PATCH {{BASE_URL}}/status/{{hawala_id}}/`

**Headers**:
```
Authorization: Bearer {{AUTH_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "status": "completed",
    "notes": "Transaction completed successfully"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Hawala transaction status updated successfully",
    "hawala": {
        "hawala_id": "550e8400-e29b-41d4-a716-446655440000",
        "hawala_number": "HW001",
        "sender_name": "Ahmad Khan",
        "sender_phone": "+93701234567",
        "receiver_name": "Fatima Ali",
        "receiver_phone": "+93707654321",
        "amount": "1000.00",
        "currency": "AFN",
        "currency_code": "AFN",
        "transfer_fee": "50.00",
        "total_amount": "1050.00",
        "status": "completed",
        "mode": "internal",
        "created_at": "2024-01-01T10:00:00Z",
        "completed_at": "2024-01-01T12:00:00Z",
        "supported_currencies": [...]
    }
}
```

---

### 9. Get Hawala Receipt

**Endpoint**: `GET {{BASE_URL}}/receipt/{{hawala_id}}/`

**Headers**:
```
Authorization: Bearer {{AUTH_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "receipt_data": {
        "receipt_id": "receipt-uuid-here",
        "hawala_number": "HW001",
        "hawala_id": "550e8400-e29b-41d4-a716-446655440000",
        "transaction_date": "2024-01-01T10:00:00Z",
        "completion_date": "2024-01-01T12:00:00Z",
        "status": "Completed",
        "amount": {
            "amount": "1000.00",
            "currency": "AFN",
            "currency_name": "Afghan Afghani",
            "symbol": "؋"
        },
        "transfer_fee": {
            "fee": "50.00",
            "currency": "AFN"
        },
        "total_amount": {
            "total": "1050.00",
            "currency": "AFN"
        },
        "sender_info": {
            "name": "Ahmad Khan",
            "phone": "+93701234567"
        },
        "receiver_info": {
            "name": "Fatima Ali",
            "phone": "+93707654321"
        },
        "exchange_info": {
            "sender_exchange": {
                "name": "Test Exchange",
                "amu_pay_code": "TE001"
            },
            "destination_exchange": {
                "name": "ABC Exchange",
                "amu_pay_code": "ABC001"
            }
        }
    }
}
```

---

### 10. Generate Receipt Manually

**Endpoint**: `POST {{BASE_URL}}/generate-receipt/{{hawala_id}}/`

**Headers**:
```
Authorization: Bearer {{AUTH_TOKEN}}
Content-Type: application/json
```

**Expected Response** (201 Created):
```json
{
    "message": "Receipt generated successfully",
    "receipt": {
        "receipt_data": {
            "receipt_id": "receipt-uuid-here",
            "hawala_number": "HW001",
            "hawala_id": "550e8400-e29b-41d4-a716-446655440000",
            "transaction_date": "2024-01-01T10:00:00Z",
            "completion_date": "2024-01-01T12:00:00Z",
            "status": "Completed",
            "amount": {
                "amount": "1000.00",
                "currency": "AFN",
                "currency_name": "Afghan Afghani",
                "symbol": "؋"
            },
            "transfer_fee": {
                "fee": "50.00",
                "currency": "AFN"
            },
            "total_amount": {
                "total": "1050.00",
                "currency": "AFN"
            },
            "sender_info": {
                "name": "Ahmad Khan",
                "phone": "+93701234567"
            },
            "receiver_info": {
                "name": "Fatima Ali",
                "phone": "+93707654321"
            },
            "exchange_info": {
                "sender_exchange": {
                    "name": "Test Exchange",
                    "amu_pay_code": "TE001"
                },
                "destination_exchange": {
                    "name": "ABC Exchange",
                    "amu_pay_code": "ABC001"
                }
            }
        }
    }
}
```

---

### 11. Get Hawala Statistics

**Endpoint**: `GET {{BASE_URL}}/statistics/`

**Headers**:
```
Authorization: Bearer {{AUTH_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "message": "Hawala statistics retrieved successfully",
    "statistics": {
        "total_transactions": 10,
        "total_amount": "15000.00",
        "total_fees": "750.00",
        "status_breakdown": {
            "pending": 3,
            "sent": 2,
            "received": 2,
            "completed": 3,
            "cancelled": 0
        },
        "currency_breakdown": {
            "AFN": {
                "count": 5,
                "total_amount": "8000.00"
            },
            "USD": {
                "count": 3,
                "total_amount": "5000.00"
            },
            "EUR": {
                "count": 2,
                "total_amount": "2000.00"
            }
        },
        "mode_breakdown": {
            "internal": 6,
            "external_sender": 2,
            "external_receiver": 2
        }
    }
}
```

---

## Error Test Cases

### 1. Invalid Authentication

**Endpoint**: `GET {{BASE_URL}}/supported-currencies/`

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

### 2. Duplicate Hawala ID

**Endpoint**: `POST {{BASE_URL}}/send/`

**Request Body**:
```json
{
    "hawala_id": "550e8400-e29b-41d4-a716-446655440000",
    "hawala_number": "HW004",
    "sender_name": "Test User",
    "sender_phone": "+1234567890",
    "receiver_name": "Test Receiver",
    "receiver_phone": "+1987654321",
    "amount": 100.00,
    "currency_code": "USD",
    "transfer_fee": 5.00,
    "destination_exchange_id": 2,
    "notes": "Test transaction"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "error": "Validation failed",
    "details": {
        "hawala_id": ["Hawala ID already exists. Please use a different ID."]
    }
}
```

---

### 3. Unsupported Currency

**Endpoint**: `POST {{BASE_URL}}/send/`

**Request Body**:
```json
{
    "hawala_id": "550e8400-e29b-41d4-a716-446655440003",
    "hawala_number": "HW005",
    "sender_name": "Test User",
    "sender_phone": "+1234567890",
    "receiver_name": "Test Receiver",
    "receiver_phone": "+1987654321",
    "amount": 100.00,
    "currency_code": "BTC",
    "transfer_fee": 5.00,
    "destination_exchange_id": 2,
    "notes": "Test transaction"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "error": "Validation failed",
    "details": {
        "currency_code": ["Currency 'BTC' is not supported by your exchange. Please add this currency to your supported currencies first."]
    }
}
```

---

### 4. Access Denied

**Endpoint**: `GET {{BASE_URL}}/detail/invalid-hawala-id/`

**Headers**:
```
Authorization: Bearer {{AUTH_TOKEN}}
Content-Type: application/json
```

**Expected Response** (403 Forbidden):
```json
{
    "error": "Access denied. This hawala transaction does not belong to your exchange."
}
```

---

## Test Execution Order

1. **Setup**: Get authentication token and set environment variables
2. **Supported Currencies**: Test currency endpoint
3. **Create Transactions**: Test all three transaction creation modes
4. **List Operations**: Test listing and filtering
5. **Status Updates**: Test status transitions
6. **Receipt Operations**: Test receipt generation and retrieval
7. **Statistics**: Test statistics endpoint
8. **Error Cases**: Test validation and error handling

## Postman Collection Setup

1. Create a new collection named "Hawala API Tests"
2. Add all endpoints as requests
3. Set up environment variables
4. Add pre-request scripts for dynamic data generation
5. Add test scripts for response validation

## Dynamic Data Generation

Use these Postman pre-request scripts for dynamic data:

```javascript
// Generate random UUID
pm.environment.set("random_uuid", pm.variables.replaceIn('{{$randomUUID}}'));

// Generate random hawala number
pm.environment.set("random_hawala_number", "HW" + Math.floor(Math.random() * 10000));

// Generate random phone number
pm.environment.set("random_phone", "+93" + Math.floor(Math.random() * 100000000));
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
```

---

# 📱 **MSG App Test Cases**

## Environment Variables Setup

Add these variables to your Postman environment:

```
MSG_BASE_URL: http://localhost:8000/api/msg
SARAF_AUTH_TOKEN: your_saraf_jwt_token_here
NORMAL_USER_AUTH_TOKEN: your_normal_user_jwt_token_here
SARAF_ID: 1
NORMAL_USER_ID: 1
CONVERSATION_ID: 1
MESSAGE_ID: 1
```

## Saraf Account Messaging Tests

### 1. List Conversations

**Endpoint**: `GET {{MSG_BASE_URL}}/conversations/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: application/json
```

**Query Parameters**:
```
page: 1
page_size: 20
```

**Expected Response** (200 OK):
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

---

### 2. Create Conversation

**Endpoint**: `POST {{MSG_BASE_URL}}/conversations/create/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "title": "Business Discussion",
    "participant_ids": [2]
}
```

**Expected Response** (201 Created):
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

---

### 3. Get Conversation Details

**Endpoint**: `GET {{MSG_BASE_URL}}/conversations/{{CONVERSATION_ID}}/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: application/json
```

**Query Parameters**:
```
page: 1
page_size: 50
```

**Expected Response** (200 OK):
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

---

### 4. Send Text Message

**Endpoint**: `POST {{MSG_BASE_URL}}/messages/send/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "conversation_id": 1,
    "content": "Hello! How are you doing?",
    "message_type": "text"
}
```

**Expected Response** (201 Created):
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

---

### 5. Send Image Message

**Endpoint**: `POST {{MSG_BASE_URL}}/messages/send/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: multipart/form-data
```

**Request Body** (Form Data):
```
conversation_id: 1
content: Check out this image!
message_type: image
attachment: [FILE UPLOAD - image.jpg]
```

**Expected Response** (201 Created):
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

---

### 6. Send Audio Message

**Endpoint**: `POST {{MSG_BASE_URL}}/messages/send/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: multipart/form-data
```

**Request Body** (Form Data):
```
conversation_id: 1
content: Voice message
message_type: audio
attachment: [FILE UPLOAD - audio.mp3]
```

**Expected Response** (201 Created):
```json
{
    "message_id": 3,
    "content": "Voice message",
    "message_type": "audio",
    "attachment": "http://localhost:8000/media/message_files/1/audio.mp3",
    "sender_display_name": "ABC Exchange",
    "sender_employee_name": null,
    "file_size": "1.5 MB",
    "created_at": "2024-01-01T10:15:00Z",
    "deliveries": [...]
}
```

---

### 7. Update Message Status

**Endpoint**: `PATCH {{MSG_BASE_URL}}/messages/{{MESSAGE_ID}}/status/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "delivery_status": "read"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Status updated successfully"
}
```

---

### 8. Search Messages

**Endpoint**: `GET {{MSG_BASE_URL}}/messages/search/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: application/json
```

**Query Parameters**:
```
q: hello
page: 1
page_size: 20
```

**Expected Response** (200 OK):
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

---

### 9. Get Messaging Statistics

**Endpoint**: `GET {{MSG_BASE_URL}}/messages/stats/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
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

---

### 10. Get Notifications

**Endpoint**: `GET {{MSG_BASE_URL}}/notifications/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: application/json
```

**Query Parameters**:
```
page: 1
page_size: 20
```

**Expected Response** (200 OK):
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

---

### 11. Mark Notification as Read

**Endpoint**: `PATCH {{MSG_BASE_URL}}/notifications/{{NOTIFICATION_ID}}/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "message": "Notification marked as read"
}
```

---

### 12. Delete Conversation

**Endpoint**: `DELETE {{MSG_BASE_URL}}/conversations/{{CONVERSATION_ID}}/delete/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "message": "Conversation deleted successfully",
    "conversation_id": 1
}
```

---

## Normal User Messaging Tests

### 1. List Normal User Conversations

**Endpoint**: `GET {{MSG_BASE_URL}}/normal-user/conversations/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_AUTH_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "conversations": [
        {
            "conversation_id": 2,
            "conversation_type": "normal_to_saraf",
            "title": "Chat with ABC Exchange",
            "participant_names": "ABC Exchange, John Doe",
            "last_message_preview": {
                "content": "Hi, I need help with my transaction",
                "sender": "John Doe",
                "message_type": "text",
                "created_at": "2024-01-01T10:20:00Z"
            },
            "unread_count": 0,
            "updated_at": "2024-01-01T10:20:00Z"
        }
    ],
    "pagination": {...}
}
```

---

### 2. Create Normal User Conversation

**Endpoint**: `POST {{MSG_BASE_URL}}/normal-user/conversations/create/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_AUTH_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "saraf_id": 1
}
```

**Expected Response** (201 Created):
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

---

### 3. Send Message as Normal User

**Endpoint**: `POST {{MSG_BASE_URL}}/normal-user/messages/send/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_AUTH_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "conversation_id": 2,
    "content": "Hi, I need help with my transaction",
    "message_type": "text"
}
```

**Expected Response** (201 Created):
```json
{
    "message_id": 4,
    "content": "Hi, I need help with my transaction",
    "message_type": "text",
    "attachment": null,
    "sender_display_name": "John Doe",
    "sender_employee_name": null,
    "file_size": null,
    "created_at": "2024-01-01T10:20:00Z",
    "deliveries": [...]
}
```

---

## MSG App Error Test Cases

### 1. Invalid Authentication

**Endpoint**: `GET {{MSG_BASE_URL}}/conversations/`

**Headers**:
```
Authorization: Bearer invalid_token
Content-Type: application/json
```

**Expected Response** (401 Unauthorized):
```json
{
    "error": "Invalid user token - no saraf_id found"
}
```

---

### 2. Invalid Conversation ID

**Endpoint**: `GET {{MSG_BASE_URL}}/conversations/999/`

**Headers**:
```
Authorization: Bearer {{SARAF_AUTH_TOKEN}}
Content-Type: application/json
```

**Expected Response** (404 Not Found):
```json
{
    "error": "Conversation not found"
}
```

---

### 3. Invalid Message Type

**Endpoint**: `POST {{MSG_BASE_URL}}/messages/send/`

**Request Body**:
```json
{
    "conversation_id": 1,
    "content": "Test message",
    "message_type": "invalid_type"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "error": "Validation failed",
    "details": {
        "message_type": ["Message type must be one of: text, image, audio"]
    }
}
```

---

### 4. Invalid File Type for Image

**Endpoint**: `POST {{MSG_BASE_URL}}/messages/send/`

**Request Body** (Form Data):
```
conversation_id: 1
content: Test image
message_type: image
attachment: [FILE UPLOAD - document.pdf]
```

**Expected Response** (400 Bad Request):
```json
{
    "error": "Validation failed",
    "details": {
        "non_field_errors": ["Invalid image file format"]
    }
}
```

---

### 5. Permission Denied for Employee

**Endpoint**: `GET {{MSG_BASE_URL}}/conversations/`

**Headers**:
```
Authorization: Bearer EMPLOYEE_WITHOUT_CHAT_PERMISSION_TOKEN
Content-Type: application/json
```

**Expected Response** (403 Forbidden):
```json
{
    "error": "You do not have permission to chat"
}
```

---

## MSG App Test Execution Order

1. **Setup**: Get authentication tokens for Saraf and Normal User
2. **Create Conversations**: Test conversation creation for both user types
3. **Send Messages**: Test all message types (text, image, audio)
4. **Message Status**: Test message delivery status updates
5. **Search**: Test message search functionality
6. **Notifications**: Test notification system
7. **Statistics**: Test messaging statistics
8. **Delete**: Test conversation deletion
9. **Error Cases**: Test validation and error handling

## MSG App Postman Collection Setup

1. Create a new collection named "MSG App Tests"
2. Add all messaging endpoints as requests
3. Set up environment variables for tokens and IDs
4. Add pre-request scripts for dynamic data generation
5. Add test scripts for response validation

## MSG App Dynamic Data Generation

Use these Postman pre-request scripts for dynamic data:

```javascript
// Generate random conversation title
pm.environment.set("random_title", "Test Conversation " + Math.floor(Math.random() * 1000));

// Generate random message content
pm.environment.set("random_message", "Test message " + Math.floor(Math.random() * 1000));

// Generate random participant ID
pm.environment.set("random_participant_id", Math.floor(Math.random() * 10) + 1);
```

## MSG App Response Validation Scripts

Add these test scripts to validate responses:

```javascript
// Check response status
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Check response structure
pm.test("Response has required fields", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('conversations');
});

// Check authentication
pm.test("Response is not unauthorized", function () {
    pm.expect(pm.response.code).to.not.equal(401);
});

// Check pagination
pm.test("Response has pagination", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('pagination');
});
```

This comprehensive test suite covers all MSG App endpoints with various scenarios including success cases, error cases, and edge cases for both Saraf accounts and Normal users.

---

This comprehensive test suite covers all AMU Pay API endpoints with various scenarios including success cases, error cases, and edge cases.
