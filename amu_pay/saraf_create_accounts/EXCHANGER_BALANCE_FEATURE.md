# Exchanger Balance Feature

## Overview

This feature adds a comprehensive balance endpoint for exchanger accounts that shows how exchanger transactions affect the saraf's main balance.

## New Endpoint

### GET `/api/customer-accounts/<account_id>/exchanger-balance/`

Get detailed balance information for an exchanger account including its impact on the saraf account.

**Authentication**: Required (JWT token)

**URL Parameters**:
- `account_id` (int): The exchanger account ID

**Response**:
```json
{
    "message": "Exchanger balance retrieved successfully",
    "account": {
        "account_id": 1,
        "account_number": "0011234567",
        "full_name": "John Doe",
        "phone": "0790123456",
        "account_type": "exchanger"
    },
    "exchanger_balances": [
        {
            "balance_id": 1,
            "currency_code": "AFN",
            "balance": "5000.00",
            "total_deposits": "10000.00",
            "total_withdrawals": "5000.00",
            "transaction_count": 15
        }
    ],
    "saraf_balances_impact": [
        {
            "currency_code": "AFN",
            "currency_name": "Afghan Afghani",
            "currency_symbol": "؋",
            "saraf_balance": "50000.00",
            "total_deposits": "100000.00",
            "total_withdrawals": "50000.00",
            "transaction_count": 150
        }
    ],
    "exchanger_statistics": [
        {
            "currency__currency_code": "AFN",
            "currency__currency_name": "Afghan Afghani",
            "currency__symbol": "؋",
            "total_given": 5000.00,
            "total_taken": 3000.00,
            "given_count": 10,
            "taken_count": 8
        }
    ],
    "note": "Saraf balances show the net impact of all exchanger transactions on the saraf account"
}
```

## How Exchange Transactions Affect Balances

### Transaction Flow

When you perform exchange operations on an exchanger account, they automatically affect the saraf's balance:

#### 1. Give Money (Give Money to Exchanger)
- **Exchanger Balance**: Increases (positive)
- **Saraf Balance**: Decreases (negative)
- **Logic**: You're giving money to the exchanger, so your saraf balance goes down

#### 2. Take Money (Take Money from Exchanger)
- **Exchanger Balance**: Decreases (negative)
- **Saraf Balance**: Increases (positive)
- **Logic**: You're taking money back from the exchanger, so your saraf balance goes up

### Balance Update Logic

The balance updates happen automatically in `CustomerTransaction.save()` method:

```python
# In CustomerTransaction.save()
if transaction_type in ['deposit', 'take_money']:
    # These operations increase saraf balance
    saraf_balance.balance += amount
    saraf_balance.total_deposits += amount
elif transaction_type in ['withdrawal', 'give_money']:
    # These operations decrease saraf balance
    saraf_balance.balance -= amount
    saraf_balance.total_withdrawals += amount
```

## Use Cases

### 1. Check Exchanger Balance
Get the current balance for a specific exchanger:
```bash
GET /api/customer-accounts/123/exchanger-balance/
```

### 2. View Saraf Impact
See how this exchanger's transactions have affected your saraf balance:
```bash
GET /api/customer-accounts/123/exchanger-balance/
# Look at "saraf_balances_impact" field
```

### 3. Monitor Exchanger Statistics
Track how much you've given and taken from the exchanger:
```bash
GET /api/customer-accounts/123/exchanger-balance/
# Look at "exchanger_statistics" field
```

## Business Logic

### Transaction Types for Exchangers

1. **give_money**: You give money to the exchanger
   - Exchanger balance ↗ (increases)
   - Saraf balance ↘ (decreases)

2. **take_money**: You take money from the exchanger
   - Exchanger balance ↘ (decreases)
   - Saraf balance ↗ (increases)

### Automatic Balance Sync

- All exchanger transactions automatically update both exchanger and saraf balances
- No manual balance reconciliation needed
- All changes are auditable through transaction history

## Related Endpoints

- `GET /api/customer-accounts/<account_id>/balances/` - Standard customer balance
- `POST /api/customer-accounts/<account_id>/give-money/` - Give money to exchanger
- `POST /api/customer-accounts/<account_id>/take-money/` - Take money from exchanger
- `GET /api/customer-accounts/<account_id>/given-amounts/` - Total given amounts
- `GET /api/customer-accounts/<account_id>/taken-amounts/` - Total taken amounts

## Error Handling

- **401 Unauthorized**: Missing or invalid JWT token
- **404 Not Found**: Account not found or not an exchanger type
- **403 Forbidden**: User doesn't have permission

## Example Workflow

1. Create an exchanger account
2. Give 1000 AFN to the exchanger
   - Exchanger balance: +1000 AFN
   - Saraf balance: -1000 AFN
3. Exchanger performs business operations
4. Take 800 AFN back from exchanger
   - Exchanger balance: -800 AFN (net: +200 AFN)
   - Saraf balance: +800 AFN (net: -200 AFN)
5. Check balance to see net impact
   - Exchanger still owes you: 200 AFN
   - Your saraf balance is down by: 200 AFN

This provides full visibility into the financial relationship between your saraf and the exchanger.

