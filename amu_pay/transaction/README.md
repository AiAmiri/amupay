# 💰 **Transaction App**

A comprehensive transaction management system for AMU Pay that enables Saraf (money exchange) businesses to record, track, and manage deposit and withdrawal transactions with automatic balance updates and detailed audit trails.

## 🎯 **Overview**

The Transaction app provides a complete financial transaction solution with:
- **Transaction Recording**: Deposit and withdrawal transaction creation
- **Automatic Balance Updates**: Real-time balance calculation and updates
- **Permission Control**: Employee permission-based transaction access
- **Time-based Filtering**: Filter transactions by time periods (day, week, month)
- **Currency Support**: Multi-currency transaction support
- **Audit Trail**: Complete transaction history with performer information
- **Transaction Management**: View, delete, and manage transactions

## 🏗️ **Architecture**

### **Models**

#### **Transaction**
- **Purpose**: Records all deposit and withdrawal transactions
- **Types**: `deposit` and `withdrawal` transaction types
- **Balance Tracking**: Automatic balance before/after calculation
- **Performer Tracking**: Complete performer information from JWT tokens
- **Currency Support**: Multi-currency transaction support

### **Key Features**

#### **💰 Transaction Management**
- **Deposit Transactions**: Record money deposits to Saraf accounts
- **Withdrawal Transactions**: Record money withdrawals from Saraf accounts
- **Automatic Balance Updates**: Real-time balance calculation
- **Transaction Validation**: Comprehensive transaction validation
- **Currency Validation**: Support for Saraf-supported currencies only

#### **🔒 Permission Control**
- **Employee Permissions**: Permission-based transaction access
- **Deposit Permissions**: `deposit_to_account` permission required
- **Withdrawal Permissions**: `withdraw_from_account` permission required
- **History Permissions**: `view_history` permission for transaction viewing
- **Delete Permissions**: `delete_transaction` permission for transaction deletion

#### **📊 Transaction Filtering**
- **Time-based Filtering**: Filter by last day, week, month, or all time
- **Currency Filtering**: Filter transactions by specific currency
- **Type Filtering**: Filter by deposit or withdrawal transactions
- **Limit Control**: Configurable transaction limit (max 100)

#### **👤 Performer Tracking**
- **JWT Integration**: Automatic performer information extraction
- **User Type Tracking**: Saraf account vs employee performer tracking
- **Employee Information**: Employee ID and name tracking
- **Audit Trail**: Complete performer information for compliance

#### **🔄 Balance Management**
- **Automatic Updates**: Real-time balance updates on transaction creation
- **Balance Restoration**: Balance restoration on transaction deletion
- **Balance Validation**: Negative balance prevention
- **Transaction Count**: Automatic transaction count updates

#### **📈 Reporting & Analytics**
- **Transaction History**: Complete transaction history with pagination
- **Performance Metrics**: Transaction count and balance tracking
- **Time-based Reports**: Filtered reports by time periods
- **Currency Reports**: Currency-specific transaction reports

## 🚀 **API Endpoints**

### **Transaction Management**
```http
POST   /api/transaction/create/                   # Create new transaction
GET    /api/transaction/                         # List transactions
GET    /api/transaction/<id>/                    # Get transaction details
DELETE /api/transaction/<id>/delete/              # Delete transaction
```

## 📋 **Usage Examples**

### **1. Create Deposit Transaction**

```bash
curl -X POST "http://localhost:8000/api/transaction/create/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "currency_code": "USD",
    "transaction_type": "deposit",
    "amount": "1000.00",
    "description": "Customer deposit for money exchange"
  }'
```

**Response:**
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

### **2. Create Withdrawal Transaction**

```bash
curl -X POST "http://localhost:8000/api/transaction/create/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "currency_code": "USD",
    "transaction_type": "withdrawal",
    "amount": "500.00",
    "description": "Cash withdrawal for customer"
  }'
```

**Response:**
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
        "performer_user_type": "employee",
        "performer_full_name": "John Doe",
        "performer_employee_id": 1,
        "performer_employee_name": "John Doe",
        "balance_before": "6000.00",
        "balance_after": "5500.00",
        "created_at": "2024-01-01T10:30:00Z"
    }
}
```

### **3. List All Transactions**

```bash
curl -X GET "http://localhost:8000/api/transaction/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
    "transactions": [
        {
            "transaction_id": 2,
            "currency": "USD",
            "transaction_type": "withdrawal",
            "amount": "500.00",
            "description": "Cash withdrawal for customer",
            "performer_full_name": "John Doe",
            "performer_employee_name": "John Doe",
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
        "currency": null,
        "type": null,
        "time": "all",
        "limit": 50
    }
}
```

### **4. List Transactions with Time Filter (Last Day)**

```bash
curl -X GET "http://localhost:8000/api/transaction/?time=day" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
    "transactions": [
        {
            "transaction_id": 2,
            "currency": "USD",
            "transaction_type": "withdrawal",
            "amount": "500.00",
            "description": "Cash withdrawal for customer",
            "performer_full_name": "John Doe",
            "performer_employee_name": "John Doe",
            "balance_before": "6000.00",
            "balance_after": "5500.00",
            "created_at": "2024-01-01T10:30:00Z"
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

### **5. List Transactions with Currency Filter**

```bash
curl -X GET "http://localhost:8000/api/transaction/?currency=USD" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
    "transactions": [
        {
            "transaction_id": 2,
            "currency": "USD",
            "transaction_type": "withdrawal",
            "amount": "500.00",
            "description": "Cash withdrawal for customer",
            "performer_full_name": "John Doe",
            "performer_employee_name": "John Doe",
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
        "currency": "USD",
        "type": null,
        "time": "all",
        "limit": 50
    }
}
```

### **6. List Transactions with Type Filter (Deposits Only)**

```bash
curl -X GET "http://localhost:8000/api/transaction/?type=deposit" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
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

### **7. List Transactions with Multiple Filters**

```bash
curl -X GET "http://localhost:8000/api/transaction/?currency=USD&type=deposit&time=week&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
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

### **8. Get Transaction Details**

```bash
curl -X GET "http://localhost:8000/api/transaction/1/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
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

### **9. Delete Transaction**

```bash
curl -X DELETE "http://localhost:8000/api/transaction/1/delete/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
    "message": "Transaction successfully deleted and balance updated"
}
```

### **10. Create Transaction with Employee**

```bash
curl -X POST "http://localhost:8000/api/transaction/create/" \
  -H "Authorization: Bearer EMPLOYEE_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "currency_code": "EUR",
    "transaction_type": "deposit",
    "amount": "750.00",
    "description": "Employee processed deposit"
  }'
```

**Response:**
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

## 🔧 **Configuration**

### **Transaction Types**
- **Deposit**: Money added to Saraf account balance
- **Withdrawal**: Money removed from Saraf account balance
- **Validation**: Transaction type validation and processing

### **Currency Support**
- **Multi-Currency**: Support for all Saraf-supported currencies
- **Currency Validation**: Only Saraf-supported currencies allowed
- **Balance Tracking**: Separate balance tracking per currency

### **Permission System**
- **Deposit Permission**: `deposit_to_account` permission required
- **Withdrawal Permission**: `withdraw_from_account` permission required
- **History Permission**: `view_history` permission for viewing
- **Delete Permission**: `delete_transaction` permission for deletion

### **Time Filtering**
- **Day**: Last 24 hours
- **Week**: Last 7 days
- **Month**: Last 30 days
- **All**: All transactions (no time filter)

### **Amount Validation**
- **Decimal Precision**: 2 decimal places for amounts
- **Maximum Digits**: 15 digits total (including decimals)
- **Positive Values**: Only positive amounts allowed
- **Balance Validation**: Prevents negative balances

## 🔐 **Security Features**

### **Authentication**
- **JWT Tokens**: JWT-based authentication for all endpoints
- **User Validation**: Saraf account and employee validation
- **Permission Control**: Permission-based access control

### **Transaction Security**
- **Balance Validation**: Prevents negative balance creation
- **Currency Validation**: Only supported currencies allowed
- **Amount Validation**: Comprehensive amount validation
- **Performer Tracking**: Complete performer information tracking

### **Permission Security**
- **Employee Permissions**: Permission-based transaction access
- **Action Validation**: Permission validation for each action
- **Audit Trail**: Complete audit trail for all transactions

### **Data Privacy**
- **Transaction Privacy**: Transactions only visible to Saraf account
- **Performer Privacy**: Performer information included for audit
- **Balance Privacy**: Balance information only visible to authorized users

## 📊 **Database Schema**

### **Transaction Table**
```sql
CREATE TABLE transaction_transaction (
    transaction_id BIGINT PRIMARY KEY,
    saraf_account_id BIGINT REFERENCES saraf_account_sarafaccount(saraf_id),
    currency_id BIGINT REFERENCES currency_currency(currency_id),
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    description TEXT NULL,
    performer_user_id BIGINT NOT NULL,
    performer_user_type VARCHAR(20) NOT NULL,
    performer_full_name VARCHAR(255) NOT NULL,
    performer_employee_id BIGINT NULL,
    performer_employee_name VARCHAR(255) NULL,
    balance_before DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 🚨 **Error Handling**

### **Common Error Responses**

#### **Authentication Errors**
```json
{
    "error": "Invalid user information"
}
```

#### **Permission Errors**
```json
{
    "error": "You do not have permission to deposit to account"
}
```

#### **Validation Errors**
```json
{
    "error": "Invalid data sent",
    "details": {
        "amount": ["Amount must be positive"],
        "currency_code": ["Currency is not supported"]
    }
}
```

#### **Balance Errors**
```json
{
    "error": "Cannot delete deposit transaction",
    "details": "Current balance (1000.00 USD) is less than deposit amount (1500.00 USD). This would result in negative balance."
}
```

#### **Not Found Errors**
```json
{
    "error": "Transaction not found"
}
```

## 🔄 **Integration Points**

### **JWT Integration**
- **Token Validation**: JWT token validation for all endpoints
- **User Information**: Automatic user information extraction
- **Permission Extraction**: Employee permission extraction from tokens

### **Saraf Account Integration**
- **Account Validation**: Saraf account existence and status validation
- **Employee Management**: Employee permission validation
- **Balance Management**: Integration with Saraf balance system

### **Currency Integration**
- **Currency Validation**: Currency existence and support validation
- **Multi-Currency Support**: Support for multiple currencies
- **Balance Tracking**: Currency-specific balance tracking

### **Django Integration**
- **Model Integration**: Standard Django model patterns
- **Serializer Validation**: DRF serializer-based validation
- **View Integration**: APIView-based endpoint implementation
- **Transaction Management**: Atomic transaction management

## 📈 **Performance Considerations**

### **Database Indexes**
- Saraf account and currency indexes for fast lookups
- Transaction type and created at indexes for filtering
- Performer user ID indexes for audit queries

### **Transaction Management**
- Atomic transaction management for data consistency
- Efficient balance updates and calculations
- Optimized transaction queries for large datasets

### **Filtering Performance**
- Efficient time-based filtering with database indexes
- Optimized currency and type filtering
- Configurable limits for performance control

### **Caching Strategy**
- Balance caching for frequently accessed data
- Transaction count caching for performance
- Currency support caching for validation

## 🧪 **Testing**

### **Test Coverage**
- Model validation and methods
- Serializer validation and data processing
- View authentication and authorization
- Transaction creation and validation
- Balance updates and calculations
- Permission validation and enforcement

### **Test Scenarios**
1. **Transaction Creation**: Test deposit and withdrawal creation
2. **Balance Updates**: Test automatic balance updates
3. **Permission Control**: Test permission-based access control
4. **Time Filtering**: Test time-based transaction filtering
5. **Currency Filtering**: Test currency-specific filtering
6. **Transaction Deletion**: Test transaction deletion and balance restoration
7. **Error Handling**: Test validation errors and edge cases

## 🚀 **Deployment Notes**

### **Environment Variables**
- **JWT Settings**: `SECRET_KEY` for token validation
- **Database Settings**: Database configuration for transaction storage
- **Currency Settings**: Currency support configuration

### **Database Migrations**
- Run migrations to create required tables
- Set up database indexes for performance
- Configure foreign key constraints

### **Performance Configuration**
- Configure database indexes
- Set up transaction limits
- Configure balance update settings

## 🔧 **Development Setup**

### **Required Dependencies**
```python
# Django and DRF
django>=4.0
djangorestframework>=3.14
djangorestframework-simplejwt>=5.0

# Database
django[postgresql]  # For PostgreSQL support
```

### **Settings Configuration**
```python
# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# Transaction settings
TRANSACTION_LIMIT = 100  # Maximum transactions per request
```

## 📚 **API Documentation**

### **Create Transaction Endpoint**
- **URL**: `/api/transaction/create/`
- **Method**: `POST`
- **Description**: Create new deposit or withdrawal transaction
- **Required Fields**: `currency_code`, `transaction_type`, `amount`
- **Response**: Transaction details with balance information

### **List Transactions Endpoint**
- **URL**: `/api/transaction/`
- **Method**: `GET`
- **Description**: List transactions with filtering options
- **Query Parameters**: `currency`, `type`, `time`, `limit`
- **Response**: Filtered transaction list with metadata

### **Transaction Details Endpoint**
- **URL**: `/api/transaction/<id>/`
- **Method**: `GET`
- **Description**: Get detailed transaction information
- **Response**: Complete transaction details

### **Delete Transaction Endpoint**
- **URL**: `/api/transaction/<id>/delete/`
- **Method**: `DELETE`
- **Description**: Delete transaction and restore balance
- **Response**: Deletion confirmation

This comprehensive Transaction system provides a complete financial transaction management solution with automatic balance updates, permission control, time-based filtering, and detailed audit trails for Saraf businesses.
