# Exchange Money App - Currency Exchange Management System

This application is designed for managing currency exchange transactions between exchange houses and their customers, providing advanced features for currency exchange operations.

## 📋 Table of Contents

- [Main Features](#main-features)
- [Data Models](#data-models)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Filters and Search](#filters-and-search)
- [Security Features](#security-features)
- [Permission System](#permission-system)
- [Phone Validation System](#phone-validation-system)
- [Installation and Setup](#installation-and-setup)
- [Testing](#testing)
- [System Benefits](#system-benefits)

## 🚀 Main Features

### 1. Currency Exchange Management

#### Main Transaction Fields:
- **Name (name)**: Name of the exchange partner or customer
- **Transaction Type (transaction_type)**: Type of exchange
  - `person`: Individual person
  - `exchanger`: Other exchange house
  - `customer`: Customer
- **Sell Currency (sell_currency)**: Currency code being sold (e.g., USD, AFN, EUR)
- **Sell Amount (sell_amount)**: Amount of currency being sold
- **Buy Currency (buy_currency)**: Currency code being bought
- **Buy Amount (buy_amount)**: Amount of currency being bought
- **Rate (rate)**: Exchange rate (how much buy currency for 1 sell currency)
- **Notes (notes)**: Additional notes about the transaction
- **Transaction Date (transaction_date)**: Date and time of the transaction

### 2. Automatic Features

- **Automatic Performer Detection**: System automatically detects whether the transaction was performed by exchange house or employee
- **Permission Checking**: Checking required permissions for different operations
- **Automatic Validation**: Automatic validation of currency codes, amounts, and rates
- **Automatic Conversion**: Currency codes are automatically converted to uppercase
- **Automatic Transaction Date**: transaction_date is automatically set to current timestamp
- **Automatic Balance Updates**: Exchange transactions automatically update saraf balances
  - **Sell Amount**: Decreases saraf's balance of the sold currency (withdrawal)
  - **Buy Amount**: Increases saraf's balance of the bought currency (deposit)
  - **Atomic Transactions**: Uses database transactions to ensure consistency

### 3. Advanced Search and Filtering

- **Filter by Sell Currency**: Search by sell currency code
- **Filter by Buy Currency**: Search by buy currency code
- **Filter by Type**: Search by exchange type
- **Search by Name**: Search by customer or exchange house name
- **Time Filter**: Search exchanges from one day, one week, and one month ago
- **Date Range Search**: Search within a specific time range
- **Search by Performer**: Search by transaction performer name

### 4. Afghan Phone Number Integration

- **Strict Validation**: Only accepts Afghan mobile numbers starting with `07` (e.g., `0790976268`)
- **WhatsApp Compatibility**: Automatically formats numbers for WhatsApp OTP delivery
- **System-wide Consistency**: Ensures uniform phone validation across all modules
- **Error Handling**: Provides clear error messages for invalid phone formats

### 5. Customer Account Integration

- **Optional Linking**: Exchange transactions can be linked to registered customer accounts
- **Account Validation**: Ensures customer accounts belong to the same saraf
- **Rich Information**: Provides detailed customer account information in responses
- **Transaction History**: Links exchange transactions to customer transaction history

### 6. Automatic Balance Management

- **Smart Balance Updates**: Automatically updates balances based on transaction type
- **Customer Transactions**: Updates both customer and saraf balances
- **Exchanger Transactions**: Updates both exchanger and saraf balances
- **Person Transactions**: Updates only saraf balance
- **Transaction Logging**: Maintains complete audit trail for all balance changes

#### **Balance Update Logic (From Saraf's Perspective):**

**Important:** All transactions are from the Saraf's perspective:
- `sell_currency` = Saraf sells → Saraf's balance decreases (withdrawal)
- `buy_currency` = Saraf buys → Saraf's balance increases (deposit)

**Customer/Exchanger Transactions:**
- `sell_currency` (e.g., USD): 
  - Customer USD balance increases (customer buys USD - opposite of saraf)
  - Saraf USD balance decreases (saraf sells USD)
- `buy_currency` (e.g., AFN):
  - Customer AFN balance decreases (customer sells AFN - opposite of saraf)
  - Saraf AFN balance increases (saraf buys AFN)

**Person Transactions:**
- `sell_currency` (e.g., USD): Saraf USD balance decreases (saraf sells USD)
- `buy_currency` (e.g., AFN): Saraf AFN balance increases (saraf buys AFN)

## 🗄️ Data Models

### ExchangeTransaction Model

```python
class ExchangeTransaction(models.Model):
    # Basic information
    name = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    
    # Currency information
    sell_currency = models.CharField(max_length=3)
    sell_amount = models.DecimalField(max_digits=15, decimal_places=2)
    buy_currency = models.CharField(max_length=3)
    buy_amount = models.DecimalField(max_digits=15, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    
    # Additional information
    notes = models.TextField(blank=True, null=True)
    transaction_date = models.DateTimeField(default=timezone.now)
    
    # Account information
    saraf_account = models.ForeignKey('saraf_account.SarafAccount', on_delete=models.CASCADE)
    customer_account = models.ForeignKey('saraf_create_accounts.SarafCustomerAccount', on_delete=models.SET_NULL, null=True, blank=True)
    performed_by_saraf = models.ForeignKey('saraf_account.SarafAccount', on_delete=models.SET_NULL, null=True)
    performed_by_employee = models.ForeignKey('saraf_account.SarafEmployee', on_delete=models.SET_NULL, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Indexes for Optimization:

- `saraf_account` + `transaction_date`
- `sell_currency` + `buy_currency`
- `transaction_type`
- `transaction_date`
- `name`

## 💰 Balance Update System

### How Exchange Transactions Affect Saraf Balances

When an exchange transaction is created, the system automatically updates the saraf's balance for both currencies involved:

#### Example: USD to AFN Exchange
```json
{
    "sell_currency": "USD",
    "sell_amount": 100.00,
    "buy_currency": "AFN", 
    "buy_amount": 7550.00,
    "rate": 75.50
}
```

**Balance Changes:**
- **USD Balance**: Decreases by 100.00 USD (saraf sold USD)
- **AFN Balance**: Increases by 7550.00 AFN (saraf bought AFN)

#### Balance Update Logic

1. **Sell Currency**: `sell_amount` → **WITHDRAWAL** (decreases balance)
2. **Buy Currency**: `buy_amount` → **DEPOSIT** (increases balance)

#### Safety Features

- **Atomic Transactions**: Both exchange creation and balance updates happen in a single database transaction
- **Balance Validation**: Prevents negative balances (insufficient funds error)
- **Automatic Balance Creation**: Creates balance records if they don't exist
- **Transaction Consistency**: If any part fails, the entire operation is rolled back

#### Error Handling

- **Insufficient Balance**: If saraf doesn't have enough sell currency, transaction fails
- **Invalid Currency**: If currency doesn't exist, transaction fails
- **Database Errors**: All operations are rolled back if any error occurs

## 🔌 API Endpoints

### Exchange Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/exchange/` | List exchanges (with optional filters) |
| `POST` | `/api/exchange/create/` | Create new exchange |
| `GET` | `/api/exchange/{exchange_id}/` | View specific exchange details |
| `PUT` | `/api/exchange/{exchange_id}/` | Update specific exchange |
| `DELETE` | `/api/exchange/{exchange_id}/` | Delete specific exchange |

## 💡 Usage Examples

### 1. Create Currency Exchange Transaction

**Note:** `sell_amount` and `buy_amount` fields are **required** and must be greater than 0. `transaction_date` is automatically set to the current timestamp. Customer account linking and balance updates are handled automatically based on transaction type.

#### **Transaction Types and Requirements:**

- **`customer`**: Requires `customer_account_id`, updates both customer and saraf balances
- **`exchanger`**: Requires `customer_account_id`, updates both exchanger and saraf balances  
- **`person`**: No customer account needed, updates only saraf balance

#### **Customer Transaction Example:**
```bash
POST /api/exchange/create/
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
    "name": "Ahmed Customer",
    "transaction_type": "customer",
    "sell_currency": "USD",
    "sell_amount": 100.00,
    "buy_currency": "AFN",
    "buy_amount": 7550.00,
    "rate": 75.50,
    "notes": "Customer exchange request",
    "customer_account_id": 1
}
```

#### **Person Transaction Example:**
```bash
POST /api/exchange/create/
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
    "name": "Random Person",
    "transaction_type": "person",
    "sell_currency": "USD",
    "sell_amount": 100.00,
    "buy_currency": "AFN",
    "buy_amount": 7550.00,
    "rate": 75.50,
    "notes": "Person exchange request"
}
```

**Required Fields:**
- `sell_amount`: Amount of currency being sold (must be > 0)
- `buy_amount`: Amount of currency being bought (must be > 0)

**Conditional Required Fields:**
- `customer_account_id`: Required for `customer` and `exchanger` transaction types

**Automatically Set Fields:**
- `transaction_date`: Automatically set to current timestamp

**Error Response (Missing Required Fields):**
```json
{
    "error": "Invalid data",
    "details": {
        "sell_amount": ["This field is required."],
        "buy_amount": ["This field is required."]
    }
}
```

**Error Response (Missing Customer Account for Customer/Exchanger):**
```json
{
    "error": "Invalid data",
    "details": {
        "non_field_errors": ["Customer account ID is required for customer transactions"]
    }
}
```

**Error Response (Customer Account Provided for Person):**
```json
{
    "error": "Invalid data",
    "details": {
        "non_field_errors": ["Customer account ID should not be provided for person transactions"]
    }
}
```

**Success Response:**
```json
{
    "message": "Exchange transaction created successfully",
    "transaction": {
        "id": 1,
        "name": "Exchange House Ahmed",
        "transaction_type": "customer",
        "sell_currency": "USD",
        "sell_amount": "100.00",
        "buy_currency": "AFN",
        "buy_amount": "7550.00",
        "rate": "75.5000",
        "notes": "Customer exchange request",
        "transaction_date": "2025-10-25T16:26:31.224580Z",
        "saraf_account": 1,
        "customer_account": 1,
        "customer_account_info": {
            "account_id": 1,
            "account_number": "0013339070",
            "full_name": "Ahmed Customer",
            "account_type": "customer",
            "phone": "0791234567"
        },
        "performed_by_info": {
            "type": "employee",
            "id": 1,
            "name": "Test Employee"
        },
        "created_at": "2025-10-25T16:26:31.227658Z",
        "updated_at": "2025-10-25T16:26:31.227658Z"
    }
}
```

### 2. Get Exchange List

```bash
GET /api/exchange/
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
    "message": "Exchange transactions list",
    "transactions": [
        {
            "id": 1,
            "name": "Exchange House Ahmed",
            "transaction_type": "customer",
            "sell_currency": "USD",
            "sell_amount": "100.00",
            "buy_currency": "AFN",
            "buy_amount": "7550.00",
            "rate": "75.5000",
            "transaction_date": "2024-01-15T14:30:00Z",
            "saraf_name": "Test Saraf",
            "performed_by_name": "Test Employee",
            "created_at": "2024-01-15T14:30:00Z"
        }
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_count": 1,
        "total_pages": 1
    }
}
```

### 3. Update Transaction

```bash
PUT /api/exchange/1/
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>

{
    "name": "Exchange House Ahmed Mohammadi",
    "notes": "Updated exchange request"
}
```

## 🔍 Filters and Search

### Supported Query Parameters:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `sell_currency` | string | Filter by sell currency | `USD` |
| `buy_currency` | string | Filter by buy currency | `AFN` |
| `transaction_type` | string | Filter by transaction type | `customer` |
| `name` | string | Search by name | `Ahmed` |
| `performed_by` | string | Search by performer | `Employee` |
| `time_filter` | string | Time filter | `today`, `week`, `month` |
| `start_date` | date | Start date (YYYY-MM-DD) | `2024-01-01` |
| `end_date` | date | End date (YYYY-MM-DD) | `2024-01-31` |
| `page` | integer | Page number | `1` |
| `page_size` | integer | Items per page | `20` |

### Filter Examples:

```bash
# Filter by currencies
GET /api/exchange/?sell_currency=USD&buy_currency=AFN

# Filter by transaction type
GET /api/exchange/?transaction_type=customer

# Search by name
GET /api/exchange/?name=Ahmed

# Time filter
GET /api/exchange/?time_filter=today

# Date range
GET /api/exchange/?start_date=2024-01-01&end_date=2024-01-31

# Combined filters
GET /api/exchange/?sell_currency=USD&transaction_type=customer&time_filter=week
```

## 🔒 Security Features

### Authentication
- **JWT Token**: All operations require valid JWT token
- **Token Validation**: Checking token validity and expiration
- **User Context**: Extracting user information from token

### Permissions
- **Employees**: Must have `create_exchange` permission
- **Exchange Houses**: Can manage their own transactions
- **Access Restriction**: Each exchange house only has access to their own transactions

### Validation
- **Currency Codes**: Must be exactly 3 characters
- **Amounts**: Must be positive and required
  - `sell_amount`: Required, must be > 0
  - `buy_amount`: Required, must be > 0
- **Rate**: Must be positive
- **Different Currencies**: Sell and buy currencies must be different
- **Transaction Type**: Must be from allowed values

### Logging
- **Action Log**: Recording all operations in ActionLog
- **User Tracking**: Tracking the user who performed the operation
- **Timestamp**: Recording exact time of operations

## 👥 Permission System

| Operation | Required Permission | Description |
|-----------|-------------------|-------------|
| **View Exchanges** | Authentication | All authenticated users |
| **Create Exchanges** | `create_exchange` | Employees with permission |
| **Update Exchanges** | `create_exchange` | Employees with permission |
| **Delete Exchanges** | `create_exchange` | Employees with permission |
| **Search Exchanges** | Authentication | All authenticated users |

## 🔗 Customer Account Integration

### Benefits of Linking Exchange Transactions to Customer Accounts:

1. **Complete Transaction History**: Track all customer interactions in one place
2. **Customer Relationship Management**: Build comprehensive customer profiles
3. **Transaction Analytics**: Analyze customer exchange patterns and preferences
4. **Account Balance Tracking**: Monitor customer balances across different currencies
5. **Audit Trail**: Maintain detailed records for compliance and reporting
6. **Customer Service**: Provide better support with complete transaction history

### How It Works:

1. **Optional Linking**: Customer account linking is completely optional
2. **Validation**: System ensures customer accounts belong to the same saraf
3. **Rich Data**: Exchange responses include detailed customer information
4. **Transaction History**: Linked transactions appear in customer account history
5. **Balance Updates**: Exchange transactions can update customer balances

### Use Cases:

- **Regular Customers**: Link transactions for frequent customers
- **Account Holders**: Connect exchanges to customer account holders
- **Transaction Tracking**: Maintain complete audit trails
- **Customer Analytics**: Analyze customer exchange patterns
- **Compliance**: Meet regulatory requirements for transaction tracking

## 📱 Phone Validation System

### Afghan Mobile Number Validation

The system now uses a **strict Afghan mobile number validation** system that only accepts Afghan mobile numbers starting with `07`. This affects all phone number inputs across the system.

#### **Valid Afghan Phone Formats:**
- `0790976268` → Converts to `+93790976268`
- `+93790976268` → Accepted as-is

#### **Invalid Formats (Rejected):**
- `0891234567` → Error: Must start with 07
- `079123456` → Error: Too short (9 digits)
- `07912345678` → Error: Too long (11 digits)
- `+1234567890` → Error: Not Afghan number
- `1234567890` → Error: Not Afghan number

#### **Phone Validation Functions:**

The system uses shared phone validation utilities located in `utils/phone_validation.py`:

```python
from utils.phone_validation import validate_and_format_phone_number

# Example usage
phone = "0790976268"
formatted_phone = validate_and_format_phone_number(phone)
# Result: "+93790976268"
```

#### **Error Messages:**

When invalid phone numbers are provided, the system returns clear error messages:

```json
{
    "error": "Phone number must be a valid Afghan mobile number starting with 07 (e.g., 0790976268)"
}
```

#### **Impact on Exchange System:**

While the exchange module doesn't directly handle phone numbers, this validation system affects:

1. **Customer Account Creation**: When creating customer accounts for exchange transactions
2. **Saraf Registration**: When exchange houses register with phone numbers
3. **WhatsApp OTP**: When sending verification codes to Afghan numbers
4. **System Integration**: Ensures consistency across all modules

#### **WhatsApp Integration:**

The phone validation system is specifically designed to work with WhatsApp OTP functionality:

- **Format**: Afghan numbers are automatically converted to international format (`+93XXXXXXXXX`)
- **WhatsApp API**: Compatible with Twilio WhatsApp Business API
- **OTP Delivery**: Ensures proper delivery of verification codes

#### **Migration Notes:**

If you have existing phone numbers in the system that don't follow the `07XXXXXXXX` format:

1. **Update existing data** to use the correct Afghan format
2. **Validate phone numbers** before creating new records
3. **Test WhatsApp functionality** with the new validation

#### **Best Practices:**

1. **Always use Afghan format**: `0790976268` (10 digits, starting with 07)
2. **Validate before saving**: Use the validation functions before storing phone numbers
3. **Handle errors gracefully**: Provide clear error messages to users
4. **Test WhatsApp delivery**: Ensure phone numbers can receive WhatsApp messages

## 🛠️ Installation and Setup

### Prerequisites
- Python 3.8+
- Django 5.2+
- MySQL/PostgreSQL
- Redis (optional)

### Installation Steps

1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Setup Database:**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Create Admin User:**
```bash
python manage.py createsuperuser
```

4. **Run Server:**
```bash
python manage.py runserver
```

### Django Settings

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'exchange',
    'rest_framework',
    'rest_framework_simplejwt',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'saraf_account.authentication.SarafJWTAuthentication',
    ),
}
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run exchange module tests
python manage.py test exchange

# Run specific test
python manage.py test exchange.tests.ExchangeTransactionModelTest.test_exchange_transaction_creation
```

### Available Tests

#### ExchangeTransactionModelTest
- ✅ `test_exchange_transaction_creation` - Create transaction
- ✅ `test_currency_code_validation` - Currency code validation
- ✅ `test_same_currency_validation` - Same currency validation
- ✅ `test_negative_amount_validation` - Negative amount validation
- ✅ `test_get_performed_by_info` - Get performer information
- ✅ `test_calculate_rate` - Calculate rate

#### ExchangeTransactionViewTest
- ✅ `test_exchange_transaction_list_view` - Test list view
- ✅ `test_exchange_transaction_create_view` - Test create view
- ✅ `test_exchange_transaction_detail_view` - Test detail view

### Test Coverage
- **Models**: 100% coverage
- **Serializers**: Complete validation
- **Views**: Structure and existence tests

## 📊 System Benefits

### 1. Easy Management
- Simple and understandable user interface
- Complete CRUD operations
- User-friendly error handling

### 2. Powerful Search
- Multiple filters
- Text search
- Advanced time filtering
- Pagination

### 3. Flexibility
- Support for different types of exchanges
- Ability to add new fields
- Extensible structure

### 4. High Security
- JWT authentication
- Permission system
- Complete validation
- Operation logging

### 5. Optimal Performance
- Optimized indexes
- Optimized queries
- Result caching
- Pagination

### 6. Maintainability
- Clean and documented code
- Complete tests
- Modular structure
- Comprehensive documentation

## 🔄 Impact of Operations on Exchange House Account

When performing currency exchange transaction:

1. **Decrease sell currency amount** from exchange house account
2. **Increase buy currency amount** to exchange house account
3. **Record transaction** in system
4. **Update account balances**
5. **Log for tracking**

## 📈 Statistics and Reporting

### Available Reports:
- Daily/weekly/monthly transactions
- Exchange statistics by currency
- Employee performance
- Exchange profit and loss

### Reporting APIs:
```bash
# Daily statistics
GET /api/exchange/stats/daily/

# Weekly statistics
GET /api/exchange/stats/weekly/

# Monthly statistics
GET /api/exchange/stats/monthly/
```

## 🚀 Future Roadmap

### Planned Features:
- [ ] Advanced reporting API
- [ ] Real-time notifications
- [ ] Cryptocurrency support
- [ ] Automatic rate pricing system
- [ ] Integration with external systems
- [ ] Analytical dashboard
- [ ] Data export to Excel/PDF

---

## 📞 Support

For questions and support:
- **Documentation**: This README file
- **Tests**: `tests.py` file
- **Examples**: Usage examples section

---

**Version**: 1.2.0  
**Last Updated**: 2025-10-25  
**Status**: Production Ready ✅

### Recent Updates (v1.2.0):
- ✅ **Transaction Type Logic**: Implemented automatic customer account linking based on transaction type
- ✅ **Smart Balance Updates**: Automatic balance management for customer, exchanger, and person transactions
- ✅ **Customer Account Requirements**: customer_account_id required for customer/exchanger transactions
- ✅ **Person Transaction Support**: Simplified person transactions without customer account requirements
- ✅ **Enhanced Validation**: Improved validation for transaction type requirements
- ✅ **Transaction Logging**: Complete audit trail for all balance changes
- ✅ **Afghan Phone Validation**: Implemented strict validation for Afghan mobile numbers (07XXXXXXXX format)
- ✅ **WhatsApp Integration**: Enhanced WhatsApp OTP functionality for Afghan numbers
- ✅ **Required Amount Fields**: Made sell_amount and buy_amount required fields in exchange creation
- ✅ **Automatic Transaction Date**: transaction_date is now automatically set to current timestamp
- ✅ **Customer Account Integration**: Exchange transactions can now be linked to customer accounts
- ✅ **System Consistency**: Updated phone validation across all modules
- ✅ **Error Handling**: Improved error messages for invalid phone formats and customer accounts
- ✅ **Documentation**: Added comprehensive phone validation and customer account documentation
