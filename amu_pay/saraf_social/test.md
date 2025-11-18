# 💬 **Saraf Social Test Cases for Postman**

This document provides comprehensive test cases for all Saraf Social API endpoints using Postman.

## Prerequisites

1. **Test Environment**: Ensure the Django server is running
2. **Authentication**: Obtain JWT tokens for normal users and Saraf employees
3. **Test Data**: Prepare test Saraf accounts and normal user accounts
4. **Permissions**: Ensure Saraf employees have comment management permissions

## Environment Variables Setup

Create these variables in Postman:

```
SARAF_SOCIAL_BASE_URL: http://localhost:8000/api/saraf-social
NORMAL_USER_TOKEN: your_normal_user_jwt_token_here
SARAF_TOKEN: your_saraf_jwt_token_here
SARAF_ID: 1
COMMENT_ID: 1
LIKE_ID: 1
```

## Test Cases

### 1. Like a Saraf Account

**Endpoint**: `POST {{SARAF_SOCIAL_BASE_URL}}/like/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "saraf_id": "{{SARAF_ID}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Successfully liked",
    "liked": true,
    "saraf_id": 1,
    "saraf_name": "ABC Exchange"
}
```

---

### 2. Like Same Saraf Account Again (Already Liked)

**Endpoint**: `POST {{SARAF_SOCIAL_BASE_URL}}/like/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "saraf_id": "{{SARAF_ID}}"
}
```

**Expected Response** (200 OK):
```json
{
    "message": "Already liked",
    "liked": true,
    "saraf_id": 1,
    "saraf_name": "ABC Exchange"
}
```

---

### 3. Create a Comment

**Endpoint**: `POST {{SARAF_SOCIAL_BASE_URL}}/comment/create/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "saraf_id": "{{SARAF_ID}}",
    "content": "Great service! Very professional and fast transactions."
}
```

**Expected Response** (201 Created):
```json
{
    "message": "Comment created successfully",
    "comment": {
        "comment_id": 1,
        "saraf_account": "ABC Exchange",
        "normal_user": "John Doe",
        "content": "Great service! Very professional and fast transactions.",
        "status": "pending",
        "is_public": true,
        "created_at": "2024-01-01T10:00:00Z"
    }
}
```



---

### 7. Delete Own Comment

**Endpoint**: `DELETE {{SARAF_SOCIAL_BASE_URL}}/comment/{{COMMENT_ID}}/delete/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "message": "Comment deleted successfully",
    "comment_id": 1,
    "saraf_id": 1,
    "saraf_name": "ABC Exchange"
}
```

---

### 8. Get Saraf Statistics (Public)

**Endpoint**: `GET {{SARAF_SOCIAL_BASE_URL}}/saraf/{{SARAF_ID}}/stats/`

**Headers**:
```
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "saraf_id": 1,
    "saraf_name": "ABC Exchange",
    "total_likes": 25,
    "total_comments": 15,
    "approved_comments": 12,
    "pending_comments": 3,
    "last_updated": "2024-01-01T10:00:00Z"
}
```

---

### 9. Get Saraf Comments (Public)

**Endpoint**: `GET {{SARAF_SOCIAL_BASE_URL}}/saraf/{{SARAF_ID}}/comments/`

**Headers**:
```
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
    "saraf_id": 1,
    "saraf_name": "ABC Exchange",
    "comments": [
        {
            "comment_id": 1,
            "content": "Great service! Very professional and fast transactions.",
            "normal_user": "John Doe",
            "created_at": "2024-01-01T10:00:00Z"
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

### 10. Get All Saraf Statistics (Public)

**Endpoint**: `GET {{SARAF_SOCIAL_BASE_URL}}/saraf/stats/`

**Headers**:
```
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
    "saraf_stats": [
        {
            "saraf_id": 1,
            "saraf_name": "ABC Exchange",
            "total_likes": 25,
            "approved_comments": 12,
            "last_updated": "2024-01-01T10:00:00Z"
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

### 11. Get User's Likes

**Endpoint**: `GET {{SARAF_SOCIAL_BASE_URL}}/user/likes/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_TOKEN}}
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
    "user_likes": [
        {
            "like_id": 1,
            "saraf_account": "ABC Exchange",
            "saraf_id": 1,
            "created_at": "2024-01-01T10:00:00Z"
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

### 12. Get User's Comments

**Endpoint**: `GET {{SARAF_SOCIAL_BASE_URL}}/user/comments/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_TOKEN}}
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
    "user_comments": [
        {
            "comment_id": 1,
            "saraf_account": "ABC Exchange",
            "saraf_id": 1,
            "content": "Great service! Very professional and fast transactions.",
            "status": "approved",
            "is_public": true,
            "created_at": "2024-01-01T10:00:00Z"
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

## Error Test Cases

### 1. Like Without Authentication

**Endpoint**: `POST {{SARAF_SOCIAL_BASE_URL}}/like/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "saraf_id": "{{SARAF_ID}}"
}
```

**Expected Response** (401 Unauthorized):
```json
{
    "detail": "Authentication credentials were not provided."
}
```

---

### 2. Like with Saraf Token (Wrong User Type)

**Endpoint**: `POST {{SARAF_SOCIAL_BASE_URL}}/like/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "saraf_id": "{{SARAF_ID}}"
}
```

**Expected Response** (403 Forbidden):
```json
{
    "error": "Only normal users can like Saraf accounts"
}
```

---

### 3. Like Non-existent Saraf

**Endpoint**: `POST {{SARAF_SOCIAL_BASE_URL}}/like/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "saraf_id": 999
}
```

**Expected Response** (404 Not Found):
```json
{
    "detail": "Not found."
}
```

---

### 4. Create Comment with Short Content

**Endpoint**: `POST {{SARAF_SOCIAL_BASE_URL}}/comment/create/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "saraf_id": "{{SARAF_ID}}",
    "content": "Short"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "content": ["Comment must be at least 10 characters long"]
}
```

---

### 5. Create Comment with Long Content

**Endpoint**: `POST {{SARAF_SOCIAL_BASE_URL}}/comment/create/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "saraf_id": "{{SARAF_ID}}",
    "content": "This is a very long comment that exceeds the maximum allowed length of 500 characters. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium."
}
```

**Expected Response** (400 Bad Request):
```json
{
    "content": ["Comment cannot exceed 500 characters"]
}
```

---

### 6. Create Comment with Saraf Token (Wrong User Type)

**Endpoint**: `POST {{SARAF_SOCIAL_BASE_URL}}/comment/create/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "saraf_id": "{{SARAF_ID}}",
    "content": "Great service! Very professional and fast transactions."
}
```

**Expected Response** (403 Forbidden):
```json
{
    "error": "Only normal users can comment on Saraf accounts"
}
```

---

### 7. Manage Comment with Normal User Token (Wrong User Type)

**Endpoint**: `PATCH {{SARAF_SOCIAL_BASE_URL}}/comment/{{COMMENT_ID}}/manage/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "action": "approve"
}
```

**Expected Response** (403 Forbidden):
```json
{
    "error": "Only Saraf employees can manage comments"
}
```

---

### 8. Manage Comment Without Permission

**Endpoint**: `PATCH {{SARAF_SOCIAL_BASE_URL}}/comment/{{COMMENT_ID}}/manage/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "action": "approve"
}
```

**Expected Response** (403 Forbidden):
```json
{
    "error": "You do not have permission to manage comments"
}
```

---

### 9. Delete Someone Else's Comment

**Endpoint**: `DELETE {{SARAF_SOCIAL_BASE_URL}}/comment/{{COMMENT_ID}}/delete/`

**Headers**:
```
Authorization: Bearer {{NORMAL_USER_TOKEN}}
Content-Type: application/json
```

**Expected Response** (403 Forbidden):
```json
{
    "error": "You can only delete your own comments"
}
```

---

### 10. Manage Comment with Invalid Action

**Endpoint**: `PATCH {{SARAF_SOCIAL_BASE_URL}}/comment/{{COMMENT_ID}}/manage/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "action": "invalid_action"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "action": ["Invalid action. Must be one of: approve, reject, hide"]
}
```

---

### 11. Get Statistics for Non-existent Saraf

**Endpoint**: `GET {{SARAF_SOCIAL_BASE_URL}}/saraf/999/stats/`

**Headers**:
```
Content-Type: application/json
```

**Expected Response** (404 Not Found):
```json
{
    "detail": "Not found."
}
```

---

### 12. Get Comments for Inactive Saraf

**Endpoint**: `GET {{SARAF_SOCIAL_BASE_URL}}/saraf/{{SARAF_ID}}/comments/`

**Headers**:
```
Content-Type: application/json
```

**Expected Response** (404 Not Found):
```json
{
    "detail": "Not found."
}
```

---

## Test Execution Order

1. **Setup**: Configure environment variables and test data
2. **Like System**: Test like creation and duplicate prevention
3. **Comment System**: Test comment creation and validation
4. **Comment Management**: Test comment approval, rejection, and hiding
5. **User Activity**: Test user like and comment history
6. **Public Endpoints**: Test public statistics and comments
7. **Error Cases**: Test validation errors and edge cases

## Postman Collection Setup

1. Create a new collection named "Saraf Social Tests"
2. Add all endpoints as requests
3. Set up environment variables
4. Add pre-request scripts for dynamic data generation
5. Add test scripts for response validation

## Dynamic Data Generation

Use these Postman pre-request scripts for dynamic data:

```javascript
// Generate random Saraf ID
pm.environment.set("random_saraf_id", Math.floor(Math.random() * 100) + 1);

// Generate random comment ID
pm.environment.set("random_comment_id", Math.floor(Math.random() * 1000) + 1);

// Generate random like ID
pm.environment.set("random_like_id", Math.floor(Math.random() * 1000) + 1);

// Generate random comment content
const comments = [
    "Great service! Very professional and fast transactions.",
    "Excellent customer service and competitive rates.",
    "Highly recommended for money exchange services.",
    "Fast and reliable service with good rates.",
    "Professional staff and quick processing."
];
pm.environment.set("random_comment", comments[Math.floor(Math.random() * comments.length)]);
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

// Check like response
pm.test("Like response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('liked');
    pm.expect(jsonData).to.have.property('saraf_id');
    pm.expect(jsonData).to.have.property('saraf_name');
});

// Check comment response
pm.test("Comment response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('comment');
    pm.expect(jsonData.comment).to.have.property('comment_id');
    pm.expect(jsonData.comment).to.have.property('content');
    pm.expect(jsonData.comment).to.have.property('status');
});

// Check statistics response
pm.test("Statistics response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('saraf_id');
    pm.expect(jsonData).to.have.property('total_likes');
    pm.expect(jsonData).to.have.property('total_comments');
});

// Check pagination response
pm.test("Pagination response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('pagination');
    pm.expect(jsonData.pagination).to.have.property('current_page');
    pm.expect(jsonData.pagination).to.have.property('total_pages');
});
```

## Test Scenarios

### **Complete Like Flow**
1. Like Saraf account → Verify like creation → Try to like again → Verify duplicate prevention

### **Complete Comment Flow**
1. Create comment → Approve comment → Verify public visibility → Hide comment → Verify hidden status

### **Comment Moderation Flow**
1. Create comment → Approve comment → Reject comment → Hide comment → Delete comment

### **User Activity Flow**
1. Like Saraf account → Create comment → View user likes → View user comments

### **Public Display Flow**
1. Create and approve comments → View public statistics → View public comments

### **Error Handling**
1. Invalid authentication → Validation errors → Permission errors → Not found errors

## Performance Testing

### **Load Testing Scenarios**
1. **Concurrent Likes**: Test multiple simultaneous likes
2. **Comment Creation**: Test comment creation under load
3. **Statistics Display**: Test statistics loading performance
4. **Pagination Performance**: Test pagination with large datasets

### **Security Testing**
1. **Authentication**: Test JWT token validation
2. **Permission Control**: Test employee permission validation
3. **Ownership Validation**: Test user ownership verification
4. **Content Validation**: Test comment content validation

## Business Logic Testing

### **Like System Testing**
1. Test one-time like functionality
2. Test duplicate like prevention
3. Test like statistics updates
4. Test like count accuracy

### **Comment System Testing**
1. Test comment content validation
2. Test comment status management
3. Test comment visibility control
4. Test comment ownership verification

### **Moderation System Testing**
1. Test comment approval process
2. Test comment rejection process
3. Test comment hiding functionality
4. Test permission-based moderation

### **Statistics System Testing**
1. Test statistics calculation accuracy
2. Test statistics caching performance
3. Test statistics update triggers
4. Test public statistics display

This comprehensive test suite covers all Saraf Social endpoints with various scenarios including success cases, error cases, and edge cases for like system, comment system, moderation tools, and public statistics display.
