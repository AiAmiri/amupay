# Saraf Create Accounts App

این اپلیکیشن برای مدیریت حساب‌های مشتریان توسط صراف‌ها طراحی شده است.

## ویژگی‌های اصلی

### 1. ایجاد حساب مشتری
- **شماره حساب**: هر صراف می‌تواند شماره حساب منحصر به فرد برای مشتریان خود ایجاد کند
- **نام کامل**: اختیاری
- **نوع حساب**: اجباری (مشتری یا صراف)
- **شماره تلفن**: اجباری (10 رقم که با صفر شروع می‌شود)
- **آدرس**: اختیاری
- **شغل**: اختیاری
- **عکس**: اختیاری

### 2. عملیات مالی برای مشتریان
- **واریز (Deposit)**: مشتری پول به حساب خود واریز می‌کند
- **برداشت (Withdrawal)**: مشتری از حساب خود پول برداشت می‌کند

### 3. عملیات مالی برای صراف‌ها
- **دادن پول (Give Money)**: صراف پول به حساب صراف دیگر می‌دهد
- **گرفتن پول (Take Money)**: صراف از حساب صراف دیگر پول می‌گیرد

### 4. مدیریت موجودی
- **موجودی خودکار**: سیستم به طور خودکار موجودی هر مشتری را بر اساس ارز محاسبه می‌کند
- **محاسبه موجودی**:
  - برای مشتریان: موجودی = واریزها - برداشت‌ها
  - برای صراف‌ها: موجودی = پول‌های داده شده - پول‌های گرفته شده

### 5. اتصال به سیستم موجودی صراف
- **واریز و گرفتن پول**: موجودی صراف افزایش می‌یابد
- **برداشت و دادن پول**: موجودی صراف کاهش می‌یابد
- **همگام‌سازی خودکار**: تمام تراکنش‌ها به طور خودکار با سیستم `saraf_balance` همگام می‌شوند

## API Endpoints

### مدیریت حساب‌ها
- `POST /api/saraf-create-accounts/create/` - ایجاد حساب جدید
- `GET /api/saraf-create-accounts/list/` - لیست حساب‌های مشتریان
- `GET /api/saraf-create-accounts/{account_id}/` - جزئیات حساب خاص
- `PUT /api/saraf-create-accounts/{account_id}/` - ویرایش حساب
- `DELETE /api/saraf-create-accounts/{account_id}/` - حذف حساب

### عملیات مالی
- `POST /api/saraf-create-accounts/{account_id}/deposit/` - واریز پول
- `POST /api/saraf-create-accounts/{account_id}/withdraw/` - برداشت پول
- `POST /api/saraf-create-accounts/{account_id}/give-money/` - دادن پول (برای صراف‌ها)
- `POST /api/saraf-create-accounts/{account_id}/take-money/` - گرفتن پول (برای صراف‌ها)

### مشاهده تراکنش‌ها
- `GET /api/saraf-create-accounts/{account_id}/transactions/` - لیست تراکنش‌های حساب
- `GET /api/saraf-create-accounts/public/transactions/{phone}/` - مشاهده عمومی تراکنش‌ها با شماره تلفن
- `GET /api/saraf-create-accounts/public/all-accounts/{phone}/` - مشاهده همه حساب‌ها و تراکنش‌ها در تمام صراف‌ها

### مدیریت موجودی
- `GET /api/saraf-create-accounts/{account_id}/balances/` - موجودی‌های حساب

### خلاصه مبالغ
- `GET /api/saraf-create-accounts/{account_id}/withdrawal-amounts/` - مجموع مبالغ برداشت شده بر اساس ارز
- `GET /api/saraf-create-accounts/{account_id}/deposit-amounts/` - مجموع مبالغ واریز شده بر اساس ارز
- `GET /api/saraf-create-accounts/{account_id}/given-amounts/` - مجموع مبالغ داده شده بر اساس ارز (برای صراف‌ها)
- `GET /api/saraf-create-accounts/{account_id}/taken-amounts/` - مجموع مبالغ گرفته شده بر اساس ارز (برای صراف‌ها)

## مثال استفاده

### ایجاد حساب مشتری
```json
POST /api/saraf-create-accounts/create/
{
    "full_name": "احمد محمدی",
    "account_type": "customer",
    "phone": "0701234567",
    "address": "کابل، افغانستان",
    "job": "معلم"
}
```

### واریز پول
```json
POST /api/saraf-create-accounts/123/deposit/
{
    "currency_code": "AFN",
    "amount": 1000,
    "description": "واریز اولیه"
}
```

### برداشت پول
```json
POST /api/saraf-create-accounts/123/withdraw/
{
    "currency_code": "AFN",
    "amount": 500,
    "description": "برداشت برای خرید"
}
```

### دادن پول به صراف دیگر
```json
POST /api/saraf-create-accounts/123/give-money/
{
    "currency_code": "AFN",
    "amount": 2000,
    "description": "پرداخت به صراف احمد"
}
```

### گرفتن پول از صراف دیگر
```json
POST /api/saraf-create-accounts/123/take-money/
{
    "currency_code": "AFN",
    "amount": 1500,
    "description": "دریافت از صراف علی"
}
```

### مشاهده خلاصه مبالغ برداشت شده
```json
GET /api/saraf-create-accounts/123/withdrawal-amounts/

Response:
{
    "message": "Withdrawal amounts retrieved successfully",
    "account_number": "0011234567",
    "customer_name": "احمد محمدی",
    "withdrawals": [
        {
            "currency__currency_code": "AFN",
            "currency__currency_name": "Afghan Afghani",
            "currency__symbol": "؋",
            "total_amount": 5000.00,
            "transaction_count": 3
        }
    ]
}
```

### مشاهده خلاصه مبالغ واریز شده
```json
GET /api/saraf-create-accounts/123/deposit-amounts/

Response:
{
    "message": "Deposit amounts retrieved successfully",
    "account_number": "0011234567",
    "customer_name": "احمد محمدی",
    "deposits": [
        {
            "currency__currency_code": "AFN",
            "currency__currency_name": "Afghan Afghani",
            "currency__symbol": "؋",
            "total_amount": 10000.00,
            "transaction_count": 5
        }
    ]
}
```

### مشاهده همه حساب‌ها و تراکنش‌ها در تمام صراف‌ها
```json
GET /api/saraf-create-accounts/public/all-accounts/0701234567/

Response:
{
    "message": "All accounts and transactions retrieved successfully",
    "phone": "0701234567",
    "total_accounts": 3,
    "total_transactions": 15,
    "accounts": [
        {
            "account_id": 123,
            "account_number": "0011234567",
            "account_type": "Customer",
            "account_type_code": "customer",
            "saraf_id": "001",
            "saraf_name": "صراف احمد",
            "saraf_phone": "0709876543",
            "customer_name": "احمد محمدی",
            "phone": "0701234567",
            "address": "کابل، افغانستان",
            "job": "معلم",
            "created_at": "2024-01-15T10:30:00Z",
            "transaction_count": 5,
            "transactions": [
                {
                    "transaction_id": 1001,
                    "transaction_type": "deposit",
                    "amount": "1000.00",
                    "currency": {
                        "currency_code": "AFN",
                        "currency_name": "Afghan Afghani",
                        "symbol": "؋"
                    },
                    "description": "واریز اولیه",
                    "balance_before": "0.00",
                    "balance_after": "1000.00",
                    "performer_full_name": "صراف احمد",
                    "created_at": "2024-01-15T10:35:00Z"
                }
            ],
            "balances": [
                {
                    "balance": "1000.00",
                    "currency": {
                        "currency_code": "AFN",
                        "currency_name": "Afghan Afghani",
                        "symbol": "؋"
                    },
                    "total_deposits": "1000.00",
                    "total_withdrawals": "0.00",
                    "transaction_count": 1
                }
            ]
        },
        {
            "account_id": 124,
            "account_number": "0021234567",
            "account_type": "Exchanger",
            "account_type_code": "exchanger",
            "saraf_id": "002",
            "saraf_name": "صراف علی",
            "saraf_phone": "0708765432",
            "customer_name": "احمد محمدی",
            "phone": "0701234567",
            "address": "کابل، افغانستان",
            "job": "معلم",
            "created_at": "2024-01-20T14:20:00Z",
            "transaction_count": 7,
            "transactions": [
                // تراکنش‌های حساب دوم
            ],
            "balances": [
                // موجودی‌های حساب دوم
            ]
        },
        {
            "account_id": 125,
            "account_number": "0031234567",
            "account_type": "Customer",
            "account_type_code": "customer",
            "saraf_id": "003",
            "saraf_name": "صراف حسن",
            "saraf_phone": "0707654321",
            "customer_name": "احمد محمدی",
            "phone": "0701234567",
            "address": "کابل، افغانستان",
            "job": "معلم",
            "created_at": "2024-01-25T09:15:00Z",
            "transaction_count": 3,
            "transactions": [
                // تراکنش‌های حساب سوم
            ],
            "balances": [
                // موجودی‌های حساب سوم
            ]
        }
    ]
}
```

### فیلترهای موجود برای endpoint جدید
- `transaction_type`: فیلتر بر اساس نوع تراکنش (deposit, withdrawal, take_money, give_money)
- `currency_id`: فیلتر بر اساس شناسه ارز
- `date_from`: فیلتر از تاریخ مشخص
- `date_to`: فیلتر تا تاریخ مشخص

مثال استفاده با فیلتر:
```
GET /api/saraf-create-accounts/public/all-accounts/0701234567/?transaction_type=deposit&date_from=2024-01-01
```

## سیستم مجوزها

- **ایجاد حساب**: مجوز `create_accounts`
- **واریز**: مجوز `deposit_to_customer`
- **برداشت**: مجوز `withdraw_to_customer`
- **دادن پول**: مجوز `give_money`
- **گرفتن پول**: مجوز `take_money`

## ویژگی‌های امنیتی

- **احراز هویت**: همه عملیات نیاز به JWT token دارند
- **مجوزها**: کارمندان باید مجوز مناسب داشته باشند
- **اعتبارسنجی**: شماره تلفن، مقدار پول و نوع ارز اعتبارسنجی می‌شوند

## مزایای این سیستم

1. **مدیریت آسان**: صراف‌ها می‌توانند مشتریان خود را به راحتی مدیریت کنند
2. **ردیابی کامل**: همه تراکنش‌ها با جزئیات کامل ثبت می‌شوند
3. **امنیت بالا**: سیستم مجوزها و احراز هویت قوی
4. **انعطاف‌پذیری**: پشتیبانی از چندین ارز
5. **دسترسی عمومی**: مشتریان می‌توانند تراکنش‌های خود را با شماره تلفن مشاهده کنند
6. **همگام‌سازی خودکار**: تمام تراکنش‌ها به طور خودکار با سیستم موجودی صراف همگام می‌شوند
