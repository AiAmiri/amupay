from django.contrib import admin
from .models import SarafCustomerAccount, CustomerTransaction, CustomerBalance


@admin.register(SarafCustomerAccount)
class SarafCustomerAccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'full_name', 'account_type', 'phone', 'saraf_account', 'is_active', 'created_at']
    list_filter = ['account_type', 'is_active', 'saraf_account', 'created_at']
    search_fields = ['account_number', 'full_name', 'phone', 'saraf_account__full_name']
    readonly_fields = ['account_number', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(CustomerTransaction)
class CustomerTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'customer_account', 'transaction_type', 'amount', 'currency', 'created_at']
    list_filter = ['transaction_type', 'currency', 'performer_user_type', 'created_at']
    search_fields = ['customer_account__account_number', 'customer_account__full_name', 'description']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(CustomerBalance)
class CustomerBalanceAdmin(admin.ModelAdmin):
    list_display = ['customer_account', 'currency', 'balance', 'updated_at']
    list_filter = ['currency', 'customer_account__saraf_account']
    search_fields = ['customer_account__account_number', 'customer_account__full_name']
    readonly_fields = ['balance_id', 'created_at', 'updated_at']
    ordering = ['customer_account', 'currency']