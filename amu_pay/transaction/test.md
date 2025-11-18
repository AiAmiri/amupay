# 💰 **Transaction Test Cases for Postman**

This document provides comprehensive test cases for all Transaction API endpoints using Postman.

## Prerequisites

1. **Test Environment**: Ensure the Django server is running
2. **Authentication**: Obtain JWT tokens for Saraf accounts and employees
3. **Test Data**: Prepare test Saraf accounts, currencies, and supported currencies
4. **Permissions**: Ensure employees have appropriate transaction permissions

## Environment Variables Setup

Create these variables in Postman:

```
TRANSACTION_BASE_URL: http://localhost:8000/api/transaction
SARAF_TOKEN: your_saraf_jwt_token_here
EMPLOYEE_TOKEN: your_employee_jwt_token_here
SARAF_ID: 1
EMPLOYEE_ID: 1
TRANSACTION_ID: 1
CURRENCY_CODE: USD
```

## Test Cases

### 1. Create Deposit Transaction

**Endpoint**: `POST {{TRANSACTION_BASE_URL}}/create/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "currency_code": "{{CURRENCY_CODE}}",
    "transaction_type": "deposit",
    "amount": "1000.00",
    "description": "Customer deposit for money exchange"
}
```

**Expected Response** (201 Created):
```json
{
    "message": "Transaction successfully recorded",
    "transaction": {
        "transaction_id": 1,
        "saraf_account": "ABC Exchange",
        "currency": "USD",
        "transaction_type": "deposit",
        "amount": "1000.00",
        "description": "Customer deposit for money exchange",
        "performer_user_id": 1,
        "performer_user_type": "saraf",
        "performer_full_name": "ABC Exchange",
        "performer_employee_id": null,
        "performer_employee_name": null,
        "balance_before": "5000.00",
        "balance_after": "6000.00",
        "created_at": "2024-01-01T10:00:00Z"
    }
}
```

---

### 2. Create Withdrawal Transaction

**Endpoint**: `POST {{TRANSACTION_BASE_URL}}/create/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "currency_code": "{{CURRENCY_CODE}}",
    "transaction_type": "withdrawal",
    "amount": "500.00",
    "description": "Cash withdrawal for customer"
}
```

**Expected Response** (201 Created):
```json
{
    "message": "Transaction successfully recorded",
    "transaction": {
        "transaction_id": 2,
        "saraf_account": "ABC Exchange",
        "currency": "USD",
        "transaction_type": "withdrawal",
        "amount": "500.00",
        "description": "Cash withdrawal for customer",
        "performer_user_id": 1,
        "performer_user_type": "saraf",
        "performer_full_name": "ABC Exchange",
        "performer_employee_id": null,
        "performer_employee_name": null,
        "balance_before": "6000.00",
        "balance_after": "5500.00",
        "created_at": "2024-01-01T10:30:00Z"
    }
}
```

---

### 3. Create Transaction with Employee

**Endpoint**: `POST {{TRANSACTION_BASE_URL}}/create/`

**Headers**:
```
Authorization: Bearer {{EMPLOYEE_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "currency_code": "EUR",
    "transaction_type": "deposit",
    "amount": "750.00",
    "description": "Employee processed deposit"
}
```

**Expected Response** (201 Created):
```json
{
    "message": "Transaction successfully recorded",
    "transaction": {
        "transaction_id": 3,
        "saraf_account": "ABC Exchange",
        "currency": "EUR",
        "transaction_type": "deposit",
        "amount": "750.00",
        "description": "Employee processed deposit",
        "performer_user_id": 1,
        "performer_user_type": "employee",
        "performer_full_name": "John Doe",
        "performer_employee_id": 1,
        "performer_employee_name": "John Doe",
        "balance_before": "2000.00",
        "balance_after": "2750.00",
        "created_at": "2024-01-01T11:00:00Z"
    }
}
```

---

### 4. List All Transactions

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "transactions": [
        {
            "transaction_id": 3,
            "currency": "EUR",
            "transaction_type": "deposit",
            "amount": "750.00",
            "description": "Employee processed deposit",
            "performer_full_name": "John Doe",
            "performer_employee_name": "John Doe",
            "balance_before": "2000.00",
            "balance_after": "2750.00",
            "created_at": "2024-01-01T11:00:00Z"
        },
        {
            "transaction_id": 2,
            "currency": "USD",
            "transaction_type": "withdrawal",
            "amount": "500.00",
            "description": "Cash withdrawal for customer",
            "performer_full_name": "ABC Exchange",
            "performer_employee_name": null,
            "balance_before": "6000.00",
            "balance_after": "5500.00",
            "created_at": "2024-01-01T10:30:00Z"
        },
        {
            "transaction_id": 1,
            "currency": "USD",
            "transaction_type": "deposit",
            "amount": "1000.00",
            "description": "Customer deposit for money exchange",
            "performer_full_name": "ABC Exchange",
            "performer_employee_name": null,
            "balance_before": "5000.00",
            "balance_after": "6000.00",
            "created_at": "2024-01-01T10:00:00Z"
        }
    ],
    "count": 3,
    "saraf_name": "ABC Exchange",
    "time_filter": {
        "filter": "all",
        "description": "All transactions"
    },
    "filters_applied": {
        "currency": null,
        "type": null,
        "time": "all",
        "limit": 50
    }
}
```

---

### 5. List Transactions with Time Filter (Last Day)

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/?time=day`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "transactions": [
        {
            "transaction_id": 3,
            "currency": "EUR",
            "transaction_type": "deposit",
            "amount": "750.00",
            "description": "Employee processed deposit",
            "performer_full_name": "John Doe",
            "performer_employee_name": "John Doe",
            "balance_before": "2000.00",
            "balance_after": "2750.00",
            "created_at": "2024-01-01T11:00:00Z"
        }
    ],
    "count": 1,
    "saraf_name": "ABC Exchange",
    "time_filter": {
        "filter": "day",
        "description": "Last 24 hours"
    },
    "filters_applied": {
        "currency": null,
        "type": null,
        "time": "day",
        "limit": 50
    }
}
```

---

### 6. List Transactions with Time Filter (Last Week)

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/?time=week`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "transactions": [
        {
            "transaction_id": 3,
            "currency": "EUR",
            "transaction_type": "deposit",
            "amount": "750.00",
            "description": "Employee processed deposit",
            "performer_full_name": "John Doe",
            "performer_employee_name": "John Doe",
            "balance_before": "2000.00",
            "balance_after": "2750.00",
            "created_at": "2024-01-01T11:00:00Z"
        },
        {
            "transaction_id": 2,
            "currency": "USD",
            "transaction_type": "withdrawal",
            "amount": "500.00",
            "description": "Cash withdrawal for customer",
            "performer_full_name": "ABC Exchange",
            "performer_employee_name": null,
            "balance_before": "6000.00",
            "balance_after": "5500.00",
            "created_at": "2024-01-01T10:30:00Z"
        },
        {
            "transaction_id": 1,
            "currency": "USD",
            "transaction_type": "deposit",
            "amount": "1000.00",
            "description": "Customer deposit for money exchange",
            "performer_full_name": "ABC Exchange",
            "performer_employee_name": null,
            "balance_before": "5000.00",
            "balance_after": "6000.00",
            "created_at": "2024-01-01T10:00:00Z"
        }
    ],
    "count": 3,
    "saraf_name": "ABC Exchange",
    "time_filter": {
        "filter": "week",
        "description": "Last 7 days"
    },
    "filters_applied": {
        "currency": null,
        "type": null,
        "time": "week",
        "limit": 50
    }
}
```

---

### 7. List Transactions with Time Filter (Last Month)

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/?time=month`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "transactions": [
        {
            "transaction_id": 3,
            "currency": "EUR",
            "transaction_type": "deposit",
            "amount": "750.00",
            "description": "Employee processed deposit",
            "performer_full_name": "John Doe",
            "performer_employee_name": "John Doe",
            "balance_before": "2000.00",
            "balance_after": "2750.00",
            "created_at": "2024-01-01T11:00:00Z"
        },
        {
            "transaction_id": 2,
            "currency": "USD",
            "transaction_type": "withdrawal",
            "amount": "500.00",
            "description": "Cash withdrawal for customer",
            "performer_full_name": "ABC Exchange",
            "performer_employee_name": null,
            "balance_before": "6000.00",
            "balance_after": "5500.00",
            "created_at": "2024-01-01T10:30:00Z"
        },
        {
            "transaction_id": 1,
            "currency": "USD",
            "transaction_type": "deposit",
            "amount": "1000.00",
            "description": "Customer deposit for money exchange",
            "performer_full_name": "ABC Exchange",
            "performer_employee_name": null,
            "balance_before": "5000.00",
            "balance_after": "6000.00",
            "created_at": "2024-01-01T10:00:00Z"
        }
    ],
    "count": 3,
    "saraf_name": "ABC Exchange",
    "time_filter": {
        "filter": "month",
        "description": "Last 30 days"
    },
    "filters_applied": {
        "currency": null,
        "type": null,
        "time": "month",
        "limit": 50
    }
}
```

---

### 8. List Transactions with Currency Filter

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/?currency=USD`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "transactions": [
        {
            "transaction_id": 2,
            "currency": "USD",
            "transaction_type": "withdrawal",
            "amount": "500.00",
            "description": "Cash withdrawal for customer",
            "performer_full_name": "ABC Exchange",
            "performer_employee_name": null,
            "balance_before": "6000.00",
            "balance_after": "5500.00",
            "created_at": "2024-01-01T10:30:00Z"
        },
        {
            "transaction_id": 1,
            "currency": "USD",
            "transaction_type": "deposit",
            "amount": "1000.00",
            "description": "Customer deposit for money exchange",
            "performer_full_name": "ABC Exchange",
            "performer_employee_name": null,
            "balance_before": "5000.00",
            "balance_after": "6000.00",
            "created_at": "2024-01-01T10:00:00Z"
        }
    ],
    "count": 2,
    "saraf_name": "ABC Exchange",
    "time_filter": {
        "filter": "all",
        "description": "All transactions"
    },
    "filters_applied": {
        "currency": "USD",
        "type": null,
        "time": "all",
        "limit": 50
    }
}
```

---

### 9. List Transactions with Type Filter (Deposits Only)

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/?type=deposit`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "transactions": [
        {
            "transaction_id": 3,
            "currency": "EUR",
            "transaction_type": "deposit",
            "amount": "750.00",
            "description": "Employee processed deposit",
            "performer_full_name": "John Doe",
            "performer_employee_name": "John Doe",
            "balance_before": "2000.00",
            "balance_after": "2750.00",
            "created_at": "2024-01-01T11:00:00Z"
        },
        {
            "transaction_id": 1,
            "currency": "USD",
            "transaction_type": "deposit",
            "amount": "1000.00",
            "description": "Customer deposit for money exchange",
            "performer_full_name": "ABC Exchange",
            "performer_employee_name": null,
            "balance_before": "5000.00",
            "balance_after": "6000.00",
            "created_at": "2024-01-01T10:00:00Z"
        }
    ],
    "count": 2,
    "saraf_name": "ABC Exchange",
    "time_filter": {
        "filter": "all",
        "description": "All transactions"
    },
    "filters_applied": {
        "currency": null,
        "type": "deposit",
        "time": "all",
        "limit": 50
    }
}
```

---

### 10. List Transactions with Type Filter (Withdrawals Only)

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/?type=withdrawal`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "transactions": [
        {
            "transaction_id": 2,
            "currency": "USD",
            "transaction_type": "withdrawal",
            "amount": "500.00",
            "description": "Cash withdrawal for customer",
            "performer_full_name": "ABC Exchange",
            "performer_employee_name": null,
            "balance_before": "6000.00",
            "balance_after": "5500.00",
            "created_at": "2024-01-01T10:30:00Z"
        }
    ],
    "count": 1,
    "saraf_name": "ABC Exchange",
    "time_filter": {
        "filter": "all",
        "description": "All transactions"
    },
    "filters_applied": {
        "currency": null,
        "type": "withdrawal",
        "time": "all",
        "limit": 50
    }
}
```

---

### 11. List Transactions with Limit

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/?limit=2`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "transactions": [
        {
            "transaction_id": 3,
            "currency": "EUR",
            "transaction_type": "deposit",
            "amount": "750.00",
            "description": "Employee processed deposit",
            "performer_full_name": "John Doe",
            "performer_employee_name": "John Doe",
            "balance_before": "2000.00",
            "balance_after": "2750.00",
            "created_at": "2024-01-01T11:00:00Z"
        },
        {
            "transaction_id": 2,
            "currency": "USD",
            "transaction_type": "withdrawal",
            "amount": "500.00",
            "description": "Cash withdrawal for customer",
            "performer_full_name": "ABC Exchange",
            "performer_employee_name": null,
            "balance_before": "6000.00",
            "balance_after": "5500.00",
            "created_at": "2024-01-01T10:30:00Z"
        }
    ],
    "count": 2,
    "saraf_name": "ABC Exchange",
    "time_filter": {
        "filter": "all",
        "description": "All transactions"
    },
    "filters_applied": {
        "currency": null,
        "type": null,
        "time": "all",
        "limit": 2
    }
}
```

---

### 12. List Transactions with Multiple Filters

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/?currency=USD&type=deposit&time=week&limit=10`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "transactions": [
        {
            "transaction_id": 1,
            "currency": "USD",
            "transaction_type": "deposit",
            "amount": "1000.00",
            "description": "Customer deposit for money exchange",
            "performer_full_name": "ABC Exchange",
            "performer_employee_name": null,
            "balance_before": "5000.00",
            "balance_after": "6000.00",
            "created_at": "2024-01-01T10:00:00Z"
        }
    ],
    "count": 1,
    "saraf_name": "ABC Exchange",
    "time_filter": {
        "filter": "week",
        "description": "Last 7 days"
    },
    "filters_applied": {
        "currency": "USD",
        "type": "deposit",
        "time": "week",
        "limit": 10
    }
}
```

---

### 13. Get Transaction Details

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/{{TRANSACTION_ID}}/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "transaction": {
        "transaction_id": 1,
        "saraf_account": "ABC Exchange",
        "currency": "USD",
        "transaction_type": "deposit",
        "amount": "1000.00",
        "description": "Customer deposit for money exchange",
        "performer_user_id": 1,
        "performer_user_type": "saraf",
        "performer_full_name": "ABC Exchange",
        "performer_employee_id": null,
        "performer_employee_name": null,
        "balance_before": "5000.00",
        "balance_after": "6000.00",
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T10:00:00Z"
    }
}
```

---

### 14. Delete Transaction

**Endpoint**: `DELETE {{TRANSACTION_BASE_URL}}/{{TRANSACTION_ID}}/delete/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (200 OK):
```json
{
    "message": "Transaction successfully deleted and balance updated"
}
```

---

## Error Test Cases

### 1. Create Transaction Without Authentication

**Endpoint**: `POST {{TRANSACTION_BASE_URL}}/create/`

**Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
    "currency_code": "{{CURRENCY_CODE}}",
    "transaction_type": "deposit",
    "amount": "1000.00",
    "description": "Customer deposit for money exchange"
}
```

**Expected Response** (401 Unauthorized):
```json
{
    "detail": "Authentication credentials were not provided."
}
```

---

### 2. Create Transaction with Invalid Currency

**Endpoint**: `POST {{TRANSACTION_BASE_URL}}/create/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "currency_code": "INVALID",
    "transaction_type": "deposit",
    "amount": "1000.00",
    "description": "Customer deposit for money exchange"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "error": "Invalid data sent",
    "details": {
        "currency_code": ["Currency is not supported"]
    }
}
```

---

### 3. Create Transaction with Negative Amount

**Endpoint**: `POST {{TRANSACTION_BASE_URL}}/create/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "currency_code": "{{CURRENCY_CODE}}",
    "transaction_type": "deposit",
    "amount": "-1000.00",
    "description": "Customer deposit for money exchange"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "error": "Invalid data sent",
    "details": {
        "amount": ["Amount must be positive"]
    }
}
```

---

### 4. Create Transaction with Invalid Type

**Endpoint**: `POST {{TRANSACTION_BASE_URL}}/create/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "currency_code": "{{CURRENCY_CODE}}",
    "transaction_type": "invalid",
    "amount": "1000.00",
    "description": "Customer deposit for money exchange"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "error": "Invalid data sent",
    "details": {
        "transaction_type": ["Invalid transaction type"]
    }
}
```

---

### 5. Create Transaction Without Permission (Employee)

**Endpoint**: `POST {{TRANSACTION_BASE_URL}}/create/`

**Headers**:
```
Authorization: Bearer {{EMPLOYEE_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "currency_code": "{{CURRENCY_CODE}}",
    "transaction_type": "deposit",
    "amount": "1000.00",
    "description": "Customer deposit for money exchange"
}
```

**Expected Response** (403 Forbidden):
```json
{
    "error": "You do not have permission to deposit to account"
}
```

---

### 6. List Transactions Without Permission (Employee)

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/`

**Headers**:
```
Authorization: Bearer {{EMPLOYEE_TOKEN}}
Content-Type: application/json
```

**Expected Response** (403 Forbidden):
```json
{
    "error": "You do not have permission to view history"
}
```

---

### 7. Get Transaction Details Without Permission (Employee)

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/{{TRANSACTION_ID}}/`

**Headers**:
```
Authorization: Bearer {{EMPLOYEE_TOKEN}}
Content-Type: application/json
```

**Expected Response** (403 Forbidden):
```json
{
    "error": "You do not have permission to view history"
}
```

---

### 8. Delete Transaction Without Permission (Employee)

**Endpoint**: `DELETE {{TRANSACTION_BASE_URL}}/{{TRANSACTION_ID}}/delete/`

**Headers**:
```
Authorization: Bearer {{EMPLOYEE_TOKEN}}
Content-Type: application/json
```

**Expected Response** (403 Forbidden):
```json
{
    "error": "You do not have permission to delete transactions"
}
```

---

### 9. Get Non-existent Transaction

**Endpoint**: `GET {{TRANSACTION_BASE_URL}}/999/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (404 Not Found):
```json
{
    "detail": "Not found."
}
```

---

### 10. Delete Non-existent Transaction

**Endpoint**: `DELETE {{TRANSACTION_BASE_URL}}/999/delete/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (404 Not Found):
```json
{
    "detail": "Not found."
}
```

---

### 11. Delete Transaction That Would Cause Negative Balance

**Endpoint**: `DELETE {{TRANSACTION_BASE_URL}}/{{TRANSACTION_ID}}/delete/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Expected Response** (400 Bad Request):
```json
{
    "error": "Cannot delete deposit transaction",
    "details": "Current balance (1000.00 USD) is less than deposit amount (1500.00 USD). This would result in negative balance."
}
```

---

### 12. Create Transaction with Unsupported Currency

**Endpoint**: `POST {{TRANSACTION_BASE_URL}}/create/`

**Headers**:
```
Authorization: Bearer {{SARAF_TOKEN}}
Content-Type: application/json
```

**Request Body**:
```json
{
    "currency_code": "BTC",
    "transaction_type": "deposit",
    "amount": "1000.00",
    "description": "Customer deposit for money exchange"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "error": "Currency BTC is not in your supported currencies list"
}
```

---

## Test Execution Order

1. **Setup**: Configure environment variables and test data
2. **Transaction Creation**: Test deposit and withdrawal creation
3. **Transaction Listing**: Test transaction listing with various filters
4. **Transaction Details**: Test transaction detail retrieval
5. **Transaction Deletion**: Test transaction deletion and balance restoration
6. **Permission Testing**: Test permission-based access control
7. **Error Cases**: Test validation errors and edge cases

## Postman Collection Setup

1. Create a new collection named "Transaction Tests"
2. Add all endpoints as requests
3. Set up environment variables
4. Add pre-request scripts for dynamic data generation
5. Add test scripts for response validation

## Dynamic Data Generation

Use these Postman pre-request scripts for dynamic data:

```javascript
// Generate random transaction ID
pm.environment.set("random_transaction_id", Math.floor(Math.random() * 1000) + 1);

// Generate random amount
pm.environment.set("random_amount", (Math.random() * 10000).toFixed(2));

// Generate random currency codes
const currencies = ["USD", "EUR", "GBP", "AFN", "PKR"];
pm.environment.set("random_currency", currencies[Math.floor(Math.random() * currencies.length)]);

// Generate random transaction type
const types = ["deposit", "withdrawal"];
pm.environment.set("random_type", types[Math.floor(Math.random() * types.length)]);

// Generate random descriptions
const descriptions = [
    "Customer deposit for money exchange",
    "Cash withdrawal for customer",
    "Employee processed transaction",
    "Business transaction",
    "Customer service transaction"
];
pm.environment.set("random_description", descriptions[Math.floor(Math.random() * descriptions.length)]);
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

// Check transaction response
pm.test("Transaction response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('transaction');
    pm.expect(jsonData.transaction).to.have.property('transaction_id');
    pm.expect(jsonData.transaction).to.have.property('amount');
    pm.expect(jsonData.transaction).to.have.property('transaction_type');
});

// Check transaction list response
pm.test("Transaction list response has correct structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('transactions');
    pm.expect(jsonData).to.have.property('count');
    pm.expect(jsonData).to.have.property('saraf_name');
    pm.expect(jsonData).to.have.property('time_filter');
});

// Check balance validation
pm.test("Balance after is greater than balance before for deposits", function () {
    const jsonData = pm.response.json();
    if (jsonData.transaction && jsonData.transaction.transaction_type === 'deposit') {
        pm.expect(parseFloat(jsonData.transaction.balance_after)).to.be.above(parseFloat(jsonData.transaction.balance_before));
    }
});

// Check balance validation
pm.test("Balance after is less than balance before for withdrawals", function () {
    const jsonData = pm.response.json();
    if (jsonData.transaction && jsonData.transaction.transaction_type === 'withdrawal') {
        pm.expect(parseFloat(jsonData.transaction.balance_after)).to.be.below(parseFloat(jsonData.transaction.balance_before));
    }
});
```

## Test Scenarios

### **Complete Transaction Flow**
1. Create deposit → Verify balance update → Create withdrawal → Verify balance update → Delete transaction → Verify balance restoration

### **Time Filtering Flow**
1. Create transactions → Filter by day → Filter by week → Filter by month → Filter by all

### **Currency Filtering Flow**
1. Create transactions in different currencies → Filter by USD → Filter by EUR → Filter by all currencies

### **Type Filtering Flow**
1. Create deposits and withdrawals → Filter by deposits → Filter by withdrawals → Filter by all types

### **Permission Testing Flow**
1. Test with Saraf token → Test with employee token → Test without permissions → Test with different permissions

### **Error Handling**
1. Invalid authentication → Validation errors → Permission errors → Not found errors → Balance errors

## Performance Testing

### **Load Testing Scenarios**
1. **Concurrent Transactions**: Test multiple simultaneous transactions
2. **Transaction Creation**: Test transaction creation under load
3. **Transaction Listing**: Test transaction listing performance
4. **Filter Performance**: Test filtering performance with large datasets

### **Security Testing**
1. **Authentication**: Test JWT token validation
2. **Permission Control**: Test employee permission validation
3. **Balance Validation**: Test balance validation and negative balance prevention
4. **Currency Validation**: Test currency support validation

## Business Logic Testing

### **Transaction System Testing**
1. Test deposit transaction creation and balance updates
2. Test withdrawal transaction creation and balance updates
3. Test transaction deletion and balance restoration
4. Test balance validation and negative balance prevention

### **Filtering System Testing**
1. Test time-based filtering (day, week, month, all)
2. Test currency-based filtering
3. Test type-based filtering (deposit, withdrawal)
4. Test limit-based filtering

### **Permission System Testing**
1. Test Saraf account permissions
2. Test employee permissions for different actions
3. Test permission-based access control
4. Test unauthorized access prevention

### **Balance System Testing**
1. Test automatic balance updates
2. Test balance restoration on deletion
3. Test negative balance prevention
4. Test balance accuracy and consistency

This comprehensive test suite covers all Transaction endpoints with various scenarios including success cases, error cases, and edge cases for transaction creation, listing, filtering, and management.
