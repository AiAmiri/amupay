# 💰 Balance Management API

## Endpoints

### 1. Get All Balances
```
GET /api/balance/
Authorization: Bearer TOKEN
```
**Response:**
```json
{
    "balances": [
        {
            "currency": {
                "currency_code": "USD",
                "currency_name": "US Dollar",
                "symbol": "$"
            },
            "balance": "1000.00",
            "total_deposits": "1500.00",
            "total_withdrawals": "500.00",
            "transaction_count": 5
        }
    ]
}
```

### 2. Get Specific Currency Balance
```
GET /api/balance/USD/
Authorization: Bearer TOKEN
```

## Test in Postman

1. **Login as Saraf** to get token
2. **Add some supported currencies** first
3. **Create some transactions** to generate balances
4. **View all balances**
5. **View specific currency balance**

## Notes
- Balances are automatically created when first transaction occurs
- Balance = Total Deposits - Total Withdrawals
- Only supported currencies will show balances
