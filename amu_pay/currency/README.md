# 💱 Currency Management API

## Endpoints

### 1. Get Available Currencies
```
GET /api/currency/available/
```
**Response:**
```json
{
    "currencies": [
        {
            "currency_code": "USD",
            "currency_name": "US Dollar",
            "symbol": "$",
            "is_active": true
        }
    ]
}
```

### 2. Add Supported Currency
```
POST /api/currency/supported/
Authorization: Bearer TOKEN

{
    "currency_code": "USD"
}
```

### 3. Get Supported Currencies
```
GET /api/currency/supported/
Authorization: Bearer TOKEN
```

### 4. Remove Supported Currency
```
DELETE /api/currency/supported/
Authorization: Bearer TOKEN
```
body:
{
    "currency_code": "EUR"
}

Response:
{
    "message": "Currency EUR successfully removed"
}

## Test in Postman

1. **Get all currencies** (no auth needed)
2. **Login as Saraf** to get token
3. **Add USD, AFN, EUR** as supported currencies
4. **View your supported currencies**
5. **Remove one currency** to test deletion
