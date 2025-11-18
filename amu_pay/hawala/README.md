# Hawala (Money Transfer) Feature

## Overview

The Hawala feature implements a comprehensive money transfer system that supports both internal transactions (both sarafs use the app) and external transactions (only one saraf uses the app).

## Key Features

### 1. Hawala Number as Primary Key
- **Primary Identifier**: Hawala number is used as the primary key for all transactions
- **Manual Entry Required**: Users must manually enter the hawala number when creating transactions
- **Unique Validation**: System ensures hawala numbers are unique across all transactions
- **String Format**: Hawala number can be any string format (e.g., "HW12345678", "c48b4e5c-33bd-47a5-a152-011a32f0672d")
- **No Auto-Generation**: No automatic ID generation - all identifiers are manually entered

### 2. Simplified Transaction Management
- **No Auto-Generated IDs**: System no longer generates automatic UUIDs
- **Manual Control**: All transaction identifiers are manually controlled by users
- **Direct Access**: Transactions can be accessed directly using hawala numbers
- **Cleaner URLs**: API endpoints use meaningful hawala numbers instead of UUIDs

### 3. Employee Identification
- **Automatic Association**: Each hawala transaction is automatically associated with the authenticated employee
- **Token-Based**: Employee information is extracted from the authentication token
- **Permission Checks**: System verifies employee permissions before allowing operations

### 4. Access Control & Security
- **Exchange ID Validation**: All operations verify that the exchange_id and hawala_number combination belongs to the authenticated saraf
- **Token-Only Access**: All saraf and employee information is extracted from authentication tokens, not request bodies
- **Permission-Based**: Employees can only perform operations they have permissions for

### 5. Transaction Modes

#### Mode 1: Internal Transactions (Both sarafs use app)
- Sending saraf creates transaction with destination saraf ID
- Receiving saraf can view and complete the transaction
- Automatic status updates when transaction is sent

#### Mode 2.1: External Sender (Only sender uses app)
- Sending saraf creates transaction for external destination
- Transaction marked as external with "pending/external receiver" status
- No automatic completion

#### Mode 2.2: External Receiver (Only receiver uses app)
- Receiving saraf creates transaction for external sender
- All details entered manually including receiver photo and phone
- Transaction marked as received immediately

### 5. Status Management
- **Pending**: Initial status for new transactions
- **Sent**: Transaction has been sent (internal mode)
- **Received**: Transaction received with receiver details
- **Completed**: Transaction fully completed
- **Cancelled**: Transaction cancelled

### 6. Received Hawala Filtering
- **Pending and Sent**: Received hawala endpoint shows pending and sent transactions
- **Shows Internal Transactions**: Displays both pending (newly created) and sent (when sender marked as sent) hawalas
- **Real-time Updates**: Status changes reflect immediately in listings

### 7. Receipt Generation
- **Automatic Generation**: Receipts are automatically generated when transactions are completed
- **Comprehensive Data**: Includes sender saraf info, hawala details, receiver info, and employee tracking
- **Secure Format**: Only public information included in customer-facing receipts
- **Multiple Formats**: JSON format suitable for display or PDF generation

## API Endpoints

### Send Hawala
- **URL**: `POST /api/hawala/send/`
- **Purpose**: Create new hawala transaction (Mode 1 & 2.1)
- **Authentication**: Required (SarafJWTAuthentication)
- **Required Fields**: hawala_number, sender_name, sender_phone, receiver_name, amount, currency_code, transfer_fee, destination_exchange_name, destination_exchange_address, destination_saraf_uses_app
- **Auto-Set Fields**: sender_exchange, sender_exchange_name, mode (determined by destination_saraf_uses_app)

### Receive Hawala List
- **URL**: `GET /api/hawala/receive/`
- **Purpose**: List transactions to receive (excludes completed)
- **Authentication**: Required (SarafJWTAuthentication)
- **Filters**: Only shows transactions for authenticated saraf

### Receive Hawala Detail
- **URL**: `GET /api/hawala/receive/<hawala_number>/`
- **Purpose**: Get specific transaction details
- **Authentication**: Required (SarafJWTAuthentication)
- **Access Control**: Validates exchange_id and hawala_number combination

### Update Received Hawala
- **URL**: `PATCH /api/hawala/receive/<hawala_number>/`
- **Purpose**: Update transaction with receiver details
- **Authentication**: Required (SarafJWTAuthentication)
- **Required Fields**: receiver_phone, receiver_photo

### External Receive Hawala
- **URL**: `POST /api/hawala/external-receive/`
- **Purpose**: Create external transaction (Mode 2.2)
- **Authentication**: Required (SarafJWTAuthentication)
- **Required Fields**: hawala_number, sender_name, receiver_name, amount, etc.

### List All Hawalas
- **URL**: `GET /api/hawala/list-all/`
- **Purpose**: List all hawalas for authenticated saraf with filters
- **Authentication**: Required (SarafJWTAuthentication)
- **Query Parameters**:
  - `employee`: Filter by employee name ("all", "EN2", specific name)
  - `time_range`: Filter by time ("today", "week", "month", "all")
  - `limit`: Number of results (default: 50)
  - `offset`: Pagination offset (default: 0)

### Hawala History
- **URL**: `GET /api/hawala/history/`
- **Purpose**: Get transaction history with filters
- **Authentication**: Required (SarafJWTAuthentication)
- **Query Parameters**:
  - `type`: "sent", "received", "all"
  - `status`: "pending", "sent", "received", "completed", "cancelled", "all"

### Update Status
- **URL**: `PATCH /api/hawala/status/<hawala_number>/`
- **Purpose**: Update transaction status
- **Authentication**: Required (SarafJWTAuthentication)
- **Access Control**: Validates ownership

### Statistics
- **URL**: `GET /api/hawala/statistics/`
- **Purpose**: Get transaction statistics for authenticated saraf
- **Authentication**: Required (SarafJWTAuthentication)

### Receipt Management
- **URL**: `GET /api/hawala/receipt/<hawala_number>/`
- **Purpose**: Get receipt for completed hawala transaction
- **Authentication**: Required (SarafJWTAuthentication)
- **Access Control**: Validates ownership

### Generate Receipt
- **URL**: `POST /api/hawala/generate-receipt/<hawala_number>/`
- **Purpose**: Manually generate receipt for completed transaction
- **Authentication**: Required (SarafJWTAuthentication)
- **Access Control**: Validates ownership

### Supported Currencies
- **URL**: `GET /api/hawala/supported-currencies/`
- **Purpose**: Get list of currencies supported by the saraf
- **Authentication**: Required (SarafJWTAuthentication)
- **Access Control**: Requires authentication

### Normal User Lookup
- **URL**: `POST /api/hawala/lookup-by-phone/`
- **Purpose**: Allow normal users to lookup hawala transactions by receiver phone number
- **Authentication**: Not required (public endpoint)
- **Required Fields**: receiver_phone

## Query Filters and Parameters

### Hawala History Filters (`GET /api/hawala/history/`)
- **`type`**: Filter by transaction type
  - `"sent"` - Only transactions sent by you
  - `"received"` - Only transactions received by you
  - `"all"` - Both sent and received (default)
- **`status`**: Filter by transaction status
  - `"pending"` - Pending transactions
  - `"sent"` - Sent transactions
  - `"received"` - Received transactions
  - `"completed"` - Completed transactions
  - `"all"` - All statuses (default)
- **`time_range`**: Filter by time period ✨ **NEW**
  - `"today"` - Transactions from today
  - `"week"` - Transactions from last 7 days
  - `"month"` - Transactions from last 30 days
  - `"all"` - All time periods (default)
- **`limit`**: Number of results per page (default: 50)
- **`offset`**: Pagination offset (default: 0)

### List All Hawalas Filters (`GET /api/hawala/list-all/`)
- **`employee`**: Filter by employee name
  - `"all"` - All employees (default)
  - `"EN2"` - Specific employee pattern
  - `"John Doe"` - Specific employee name
- **`time_range`**: Filter by time period
  - `"today"` - Transactions from today
  - `"week"` - Transactions from last 7 days
  - `"month"` - Transactions from last 30 days
  - `"all"` - All time periods (default)
- **`status`**: Filter by transaction status
  - `"pending"` - Pending transactions
  - `"completed"` - Completed transactions
  - `"all"` - All statuses (default)
- **`limit`**: Number of results per page (default: 50)
- **`offset`**: Pagination offset (default: 0)

### Receive Hawala List Filters (`GET /api/hawala/receive/`)
- **Automatic Filter**: Only shows transactions where you are the destination exchange
- **Status Filter**: Shows transactions with `"pending"` or `"sent"` status (internal transactions)
- **Ordering**: Results ordered by creation date (newest first)

### Phone Lookup Filters (`POST /api/hawala/lookup-by-phone/`)
- **Automatic Filter**: Only shows transactions with status `"pending"` or `"completed"`
- **Ordering**: Results ordered by creation date (newest first)

## Transaction Status Flow

### Status Flow Logic
The hawala system uses a four-status flow for proper tracking:

1. **`pending`** - Initial status when hawala is created by sender
2. **`sent`** - Status when sender marks transaction as sent (internal mode)
3. **`received`** - Status when receiver processes the hawala transaction
4. **`completed`** - Final status when transaction is fully completed

### Status Transitions
- **`pending` → `sent`**: When sender marks internal transaction as sent
- **`pending` → `completed`**: When receiver directly completes pending transaction
- **`sent` → `received`**: When receiver processes sent transaction
- **`received` → `completed`**: When receiver completes the transaction
- **No transitions from completed**: Once completed, status cannot be changed

### Business Logic
- **Sender creates hawala**: Status automatically set to `pending`
- **Internal transaction sent**: Status changes to `sent` automatically
- **Receiver processes hawala**: Can process `pending` or `sent` transactions, updates to `received` then `completed`
- **Receipt generation**: Only available for `completed` transactions

## Data Model

### HawalaTransaction Model

#### Core Fields
- `hawala_number`: Primary key - Manual hawala number (required, unique)
- `status`: Transaction status (pending, completed)
- `mode`: Transaction mode (internal, external_sender, external_receiver)

#### Sender Information
- `sender_name`: Name of person sending money
- `sender_phone`: Sender's phone number
- `sender_exchange`: Foreign key to SarafAccount (sending exchange)
- `sender_exchange_name`: Name of sending exchange

#### Receiver Information
- `receiver_name`: Name of person receiving money
- `receiver_phone`: Receiver's phone number (filled by receiving saraf)
- `receiver_photo`: Photo of receiver (taken by receiving saraf)

#### Transaction Details
- `amount`: Transfer amount (DecimalField)
- `currency`: Foreign key to Currency model
- `transfer_fee`: Transfer fee charged
- `notes`: Additional notes or comments

#### Destination Exchange
- `destination_exchange_id`: ID of destination exchange (if using app)
- `destination_exchange_name`: Name of destination exchange
- `destination_exchange_address`: Address of destination exchange
- `destination_saraf_uses_app`: Boolean indicating if destination uses app

#### Tracking
- `created_by_employee`: Employee who created transaction
- `received_by_employee`: Employee who received transaction
- `created_at`: Creation timestamp
- `sent_at`: Sent timestamp
- `received_at`: Received timestamp
- `completed_at`: Completed timestamp
- `updated_at`: Last update timestamp

## HawalaReceipt Model

### Core Fields
- `receipt_id`: UUID primary key (auto-generated)
- `hawala_transaction`: One-to-one relationship with HawalaTransaction
- `generated_at`: Receipt generation timestamp
- `generated_by_employee`: Employee who generated the receipt
- `receipt_data`: JSON field containing structured receipt information
- `is_active`: Receipt status (active/inactive)

### Receipt Data Structure
The `receipt_data` JSON field contains:

#### Sender Saraf Information
- `saraf_name`: Full name of saraf
- `exchange_name`: Business name
- `saraf_id`: Unique saraf identifier
- `phone`: Contact phone number
- `email`: Contact email
- `amu_pay_code`: AmuPay code
- `address`: Business address
- `province`: Province/state

#### Hawala Details
- `hawala_number`: Manual hawala number (primary key)
- `amount`: Transfer amount
- `currency`: Currency information (code, name, symbol)
- `transfer_fee`: Fee charged
- `total_amount`: Total amount including fee
- `created_at`: Transaction creation time
- `completed_at`: Transaction completion time
- `status`: Current status
- `mode`: Transaction mode
- `notes`: Additional notes

#### Receiver Information
- `receiver_name`: Name of receiver
- `receiver_phone`: Receiver's phone number
- `sender_name`: Name of sender
- `sender_phone`: Sender's phone number

#### Destination Exchange
- `exchange_name`: Destination exchange name
- `exchange_address`: Destination address
- `exchange_id`: Destination exchange ID

#### Employee Information
- `created_by`: Employee who created transaction
- `received_by`: Employee who received transaction
- `generated_by`: Employee who generated receipt

## Validation Rules

### Hawala Number
- Required field
- Must be unique across all transactions
- Validated on creation and update

### Auto-Set Fields
- **currency**: Automatically set from currency_code field (read-only)
- **sender_exchange**: Automatically set from authenticated user's saraf account
- **sender_exchange_name**: Automatically set from authenticated user's exchange name
- **mode**: Automatically determined based on destination_saraf_uses_app:
  - `internal`: When destination_saraf_uses_app is true and destination_exchange_id is provided
  - `external_sender`: When destination_saraf_uses_app is false
- **created_by_employee**: Automatically set if authenticated user is an employee

### Exchange ID and Hawala Number Combination
- All operations verify that the combination belongs to authenticated saraf
- Returns 403 Forbidden if access denied
- Prevents unauthorized access to transactions

### Amount and Fees
- Amount must be greater than zero
- Transfer fee cannot be negative
- Total amount calculated as amount + transfer_fee

### Status Transitions
- `pending` → `sent`, `cancelled`
- `sent` → `received`, `cancelled`
- `received` → `completed`
- `completed` → (no transitions)
- `cancelled` → (no transitions)

## Security Features

### Authentication
- Uses SarafJWTAuthentication for all endpoints
- Supports both SarafAccount and SarafEmployee authentication
- Token contains user type, IDs, and permissions

### Authorization
- Permission-based access control
- Employees must have specific permissions (send_transfer, receive_transfer)
- Saraf accounts have full access to their own transactions

### Data Protection
- All saraf and employee information extracted from tokens
- No sensitive data in request bodies
- Proper validation of ownership before operations

### Receipt Security
- **No Sensitive Data**: Receipts contain only public information suitable for customer delivery
- **Filtered Information**: Sensitive data like passwords, tokens, or internal IDs are excluded
- **Public Format**: Receipt data is structured for customer consumption without exposing internal system details
- **Access Control**: Only transaction owners can access their receipts

## Currency Management

### Saraf-Specific Currency Support
The hawala system now uses only currencies that each saraf has added to their supported currencies list. This ensures that:

- **Validation**: Only currencies supported by the saraf can be used in transactions
- **Security**: Prevents unauthorized currency usage
- **Flexibility**: Each saraf can support different currencies based on their business needs

### Supported Currencies API
- **Endpoint**: `GET /api/hawala/supported-currencies/`
- **Purpose**: Get list of currencies supported by the authenticated saraf
- **Response**: Returns currency codes, names, symbols, and addition dates
- **Authentication**: Requires valid saraf or employee token

### Currency Validation Rules
- **Active Check**: Currency must be active in the system
- **Saraf Support**: Currency must be supported by the saraf
- **Error Messages**: Clear feedback when unsupported currencies are used
- **Automatic Filtering**: Transaction lists include supported currencies information

## Usage Examples

### Creating Internal Hawala (Mode 1)
```json
POST /api/hawala/send/
{
    "hawala_number": "HW12345678",
    "sender_name": "John Doe",
    "sender_phone": "+1234567890",
    "receiver_name": "Jane Smith",
    "amount": "1000.00",
    "currency_code": "USD",
    "transfer_fee": "10.00",
    "destination_exchange_id": 2,
    "destination_exchange_name": "ABC Exchange",
    "destination_exchange_address": "123 Main St, City",
    "destination_saraf_uses_app": true,
    "notes": "Payment for services"
}
```

### Creating External Hawala (Mode 2.1)
```json
POST /api/hawala/send/
{
    "hawala_number": "HW87654321",
    "sender_name": "John Doe",
    "sender_phone": "+1234567890",
    "receiver_name": "Jane Smith",
    "amount": "500.00",
    "currency_code": "AFN",
    "transfer_fee": "5.00",
    "destination_exchange_name": "XYZ Exchange",
    "destination_exchange_address": "456 Oak St, City",
    "destination_saraf_uses_app": false,
    "notes": "Family transfer"
}
```

### Receiving Hawala (Mode 1)
```json
PATCH /api/hawala/receive/<hawala_number>/
{
    "receiver_phone": "+9876543210",
    "receiver_photo": <file>,
    "notes": "Transaction completed successfully"
}
```

### External Receive (Mode 2.2)
```json
POST /api/hawala/external-receive/
{
    "hawala_number": "HW11111111",
    "sender_name": "External Sender",
    "sender_phone": "+1111111111",
    "receiver_name": "Local Receiver",
    "receiver_phone": "+2222222222",
    "receiver_photo": <file>,
    "amount": "750.00",
    "currency_code": "EUR",
    "transfer_fee": "7.50",
    "destination_exchange_name": "External Exchange",
    "destination_exchange_address": "789 Pine St, City",
    "notes": "External transaction"
}
```

### Normal User Lookup
```json
POST /api/hawala/lookup-by-phone/
{
    "receiver_phone": "+1234567890"
}

Response:
{
    "message": "Hawala transactions found",
    "transactions": [
        {
            "hawala_number": "HW12345678",
            "sender_name": "John Doe",
            "receiver_name": "Jane Smith",
            "amount": "1000.00",
            "currency": "USD",
            "status": "sent",
            "created_at": "2024-01-15T10:00:00Z"
        }
    ]
}
```

### Filtering All Hawalas
```
GET /api/hawala/list-all/?employee=EN2&time_range=week&limit=20&offset=0
```

### Hawala History with Filters
```
GET /api/hawala/history/?type=sent&status=completed&limit=10&offset=0
```

### Filtering by Time Range
```
GET /api/hawala/list-all/?time_range=today&limit=50
```

### Filtering by Employee
```
GET /api/hawala/list-all/?employee=John Doe&limit=25
```

### Pagination Example
```
GET /api/hawala/history/?limit=20&offset=40
```

### Filtered Response Format
All filtered endpoints return responses with pagination information:
```json
{
    "message": "Hawala transaction history retrieved successfully",
    "hawalas": [
        {
            "hawala_number": "HW12345678",
            "sender_name": "John Doe",
            "receiver_name": "Jane Smith",
            "amount": "1000.00",
            "currency": "USD",
            "status": "completed",
            "created_at": "2024-01-15T10:00:00Z"
        }
    ],
    "count": 1,
    "total_count": 25,
    "offset": 0,
    "limit": 50
}
```

### Receipt Generation
```json
GET /api/hawala/receipt/<hawala_number>/
Response:
{
    "message": "Receipt retrieved successfully",
    "receipt": {
        "receipt_id": "123e4567-e89b-12d3-a456-426614174000",
        "generated_at": "2024-01-15T10:30:00Z",
        "receipt_type": "hawala_completion_receipt",
        "hawala_details": {
            "hawala_number": "HW12345678",
            "amount": 1000.00,
            "currency": {
                "code": "USD",
                "name": "US Dollar",
                "symbol": "$"
            },
            "transfer_fee": 10.00,
            "total_amount": 1010.00,
            "created_at": "2024-01-15T09:00:00Z",
            "completed_at": "2024-01-15T10:30:00Z",
            "status": "completed"
        },
        "sender_saraf": {
            "saraf_name": "ABC Exchange",
            "exchange_name": "ABC Exchange",
            "phone": "+1234567890",
            "address": "123 Main St, City"
        },
        "receiver_info": {
            "receiver_name": "Jane Smith",
            "receiver_phone": "+9876543210",
            "sender_name": "John Doe",
            "sender_phone": "+1234567890"
        },
        "destination_exchange": {
            "exchange_name": "XYZ Exchange",
            "exchange_address": "456 Oak St, City"
        },
        "employee_info": {
            "handled_by": "Employee Name"
        }
    }
}
```

## Admin Interface

The Django admin interface provides comprehensive management of hawala transactions:

- **List View**: Shows key transaction details with filtering options
- **Detail View**: Full transaction information with organized fieldsets
- **Bulk Actions**: Mark multiple transactions as sent, received, completed, or cancelled
- **Search**: Search by hawala number, names, phone numbers, exchange names
- **Filters**: Filter by status, mode, currency, exchange, etc.
- **Read-only Protection**: Completed/cancelled transactions become read-only

## Error Handling

### Common Error Responses

#### 400 Bad Request
- Validation errors (missing required fields, invalid data)
- Invalid status transitions
- Business logic violations

#### 403 Forbidden
- Permission denied (employee lacks required permission)
- Access denied (transaction doesn't belong to authenticated saraf)

#### 404 Not Found
- Hawala transaction not found
- Invalid hawala_number

#### 500 Internal Server Error
- Unexpected server errors
- Database connection issues

### Error Response Format
```json
{
    "error": "Error message",
    "details": "Detailed error information or validation errors"
}
```

## Performance Considerations

### Database Optimization
- Proper indexing on frequently queried fields
- Select_related for foreign key optimization
- Pagination for large result sets

### Query Optimization
- Efficient filtering and ordering
- Minimal database hits per request
- Cached statistics calculations

## Future Enhancements

### Potential Improvements
1. **Real-time Notifications**: WebSocket support for real-time updates
2. **Bulk Operations**: Support for bulk transaction creation
3. **Advanced Reporting**: Detailed analytics and reporting features
4. **Mobile Optimization**: Enhanced mobile API responses
5. **Audit Trail**: Comprehensive audit logging for compliance
6. **Multi-currency Support**: Enhanced currency conversion features
7. **Integration APIs**: Third-party payment gateway integration

### Scalability Considerations
1. **Database Sharding**: Partition transactions by exchange or date
2. **Caching Layer**: Redis caching for frequently accessed data
3. **API Rate Limiting**: Prevent abuse and ensure fair usage
4. **Background Processing**: Async processing for heavy operations
5. **Microservices**: Split into smaller, focused services

## Recent Updates

### Hawala ID Removal (Latest Update)
- **Removed Auto-Generated UUIDs**: System no longer generates automatic `hawala_id` fields
- **Hawala Number as Primary Key**: `hawala_number` is now the primary key for all transactions
- **Simplified URLs**: All endpoints now use `hawala_number` instead of UUIDs
- **Database Migration**: Applied migration `0003_remove_hawala_id_use_hawala_number_as_pk`
- **Backward Compatibility**: All existing functionality maintained with cleaner implementation

### Benefits of the Update
- **User-Friendly URLs**: Direct access using meaningful hawala numbers
- **Simplified System**: No more dual identifier system
- **Better Performance**: Single primary key reduces database complexity
- **Easier Integration**: APIs use consistent hawala number format

## Conclusion

The Hawala feature provides a robust, secure, and scalable money transfer system that supports both internal and external transactions. With comprehensive validation, security measures, and flexible API endpoints, it meets the requirements for a professional financial application while maintaining data integrity and user security.
