# Exchange Logic Explanation

## 🔄 Exchange Transaction Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXCHANGE TRANSACTION FLOW                    │
└─────────────────────────────────────────────────────────────────┘

1. REQUEST CREATION
   ┌─────────────────┐
   │ Client Request  │
   │ POST /api/exchange/create/ │
   └─────────┬───────┘
             │
             ▼
   ┌─────────────────┐
   │ Authentication  │
   │ JWT Token       │
   └─────────┬───────┘
             │
             ▼
   ┌─────────────────┐
   │ Permission      │
   │ Check           │
   └─────────┬───────┘
             │
             ▼

2. DATA VALIDATION
   ┌─────────────────┐
   │ Serializer      │
   │ Validation      │
   │ - Required fields │
   │ - Currency codes │
   │ - Amounts > 0   │
   │ - Different currencies │
   └─────────┬───────┘
             │
             ▼
   ┌─────────────────┐
   │ Transaction     │
   │ Type Validation │
   │ - customer: requires account_id │
   │ - exchanger: requires account_id │
   │ - person: no account_id │
   └─────────┬───────┘
             │
             ▼

3. DATABASE TRANSACTION (ATOMIC)
   ┌─────────────────┐
   │ Create Exchange │
   │ Transaction     │
   │ Record          │
   └─────────┬───────┘
             │
             ▼
   ┌─────────────────┐
   │ Update Balances │
   │ Based on Type   │
   └─────────┬───────┘
             │
             ▼
   ┌─────────────────┐
   │ Log Action      │
   │ ActionLog       │
   └─────────┬───────┘
             │
             ▼
   ┌─────────────────┐
   │ Return Response │
   │ Success/Error   │
   └─────────────────┘
```

## 💰 Balance Update Logic

### Transaction Types and Balance Updates:

#### 1. CUSTOMER Transaction (customer_account_id required)
```
Customer sells USD 1000 → Buys AFN 85000
Rate: 85 AFN per 1 USD

CUSTOMER BALANCE:
- USD: -1000 (withdrawal)
- AFN: +85000 (deposit)

SARAF BALANCE:
- USD: +1000 (deposit - saraf receives)
- AFN: -85000 (withdrawal - saraf gives)
```

#### 2. EXCHANGER Transaction (customer_account_id required)
```
Exchanger sells EUR 500 → Buys USD 550
Rate: 1.1 USD per 1 EUR

EXCHANGER BALANCE:
- EUR: -500 (withdrawal)
- USD: +550 (deposit)

SARAF BALANCE:
- EUR: +500 (deposit - saraf receives)
- USD: -550 (withdrawal - saraf gives)
```

#### 3. PERSON Transaction (no customer_account_id)
```
Person sells USD 200 → Buys AFN 17000
Rate: 85 AFN per 1 USD

SARAF BALANCE ONLY:
- USD: +200 (deposit - saraf receives)
- AFN: -17000 (withdrawal - saraf gives)
```

## 🔍 Key Components Explained

### 1. ExchangeTransaction Model
- **Primary Fields**: name, transaction_type, sell_currency, sell_amount, buy_currency, buy_amount, rate
- **Automatic Fields**: transaction_date (auto-set), created_at, updated_at
- **Relationships**: saraf_account, customer_account (optional), performed_by_saraf/employee
- **Validation**: Currency codes (3 chars), different currencies, positive amounts, valid transaction types

### 2. Transaction Types
- **person**: Individual person (no customer account needed)
- **exchanger**: Other exchange house (requires customer account)
- **customer**: Regular customer (requires customer account)

### 3. Balance Management
- **SarafBalance**: Tracks saraf's currency balances
- **CustomerBalance**: Tracks customer/exchanger balances
- **Transaction Logging**: Records all balance changes for audit

### 4. API Endpoints
- **GET /api/exchange/**: List transactions with filters
- **POST /api/exchange/create/**: Create new transaction
- **GET /api/exchange/{id}/**: Get specific transaction
- **PUT /api/exchange/{id}/**: Update transaction
- **DELETE /api/exchange/{id}/**: Delete transaction

### 5. Security Features
- **JWT Authentication**: Required for all operations
- **Permission Checking**: Employee permissions for create/update/delete
- **Saraf Isolation**: Users can only access their own saraf's transactions
- **Customer Account Validation**: Ensures customer accounts belong to same saraf

### 6. Filtering and Search
- **Currency Filters**: sell_currency, buy_currency
- **Type Filter**: transaction_type
- **Name Search**: Case-insensitive name search
- **Time Filters**: today, week, month, custom date range
- **Performer Search**: Search by who performed the transaction
- **Pagination**: Configurable page size and page number

## 🔄 Complete Exchange Flow Example

### Request:
```json
POST /api/exchange/create/
{
    "name": "John Doe",
    "transaction_type": "customer",
    "sell_currency": "USD",
    "sell_amount": 1000.00,
    "buy_currency": "AFN",
    "buy_amount": 85000.00,
    "rate": 85.0000,
    "notes": "Regular customer exchange",
    "customer_account_id": 123
}
```

### Process:
1. **Authentication**: Validate JWT token
2. **Permission**: Check if user can create exchanges
3. **Validation**: Validate all fields and transaction type requirements
4. **Customer Account**: Verify customer account belongs to saraf
5. **Database Transaction**:
   - Create ExchangeTransaction record
   - Update CustomerBalance (USD -1000, AFN +85000)
   - Update SarafBalance (USD +1000, AFN -85000)
   - Create Transaction logs for audit
   - Create ActionLog entry
6. **Response**: Return created transaction with full details

### Response:
```json
{
    "message": "Exchange transaction created successfully",
    "transaction": {
        "id": 456,
        "name": "John Doe",
        "transaction_type": "customer",
        "sell_currency": "USD",
        "sell_amount": "1000.00",
        "buy_currency": "AFN",
        "buy_amount": "85000.00",
        "rate": "85.0000",
        "notes": "Regular customer exchange",
        "transaction_date": "2025-10-25T18:30:00Z",
        "customer_account_info": {
            "account_id": 123,
            "account_number": "CUST001",
            "full_name": "John Doe",
            "account_type": "customer",
            "phone": "+93790976268"
        },
        "performed_by_info": {
            "type": "employee",
            "id": "EMP001",
            "name": "Employee Name"
        }
    }
}
```

This exchange system provides a complete currency exchange management solution with automatic balance updates, comprehensive validation, and full audit trails.
