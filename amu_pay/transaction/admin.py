from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Transaction management panel"""
    
    list_display = [
        'transaction_id',
        'saraf_account',
        'currency',
        'transaction_type',
        'amount',
        'performer_full_name',
        'balance_after',
        'created_at'
    ]
    
    list_filter = [
        'transaction_type',
        'currency',
        'created_at',
        'performer_user_type'
    ]
    
    search_fields = [
        'saraf_account__full_name',
        'performer_full_name',
        'performer_employee_name',
        'description'
    ]
    
    readonly_fields = [
        'transaction_id',
        'balance_before',
        'balance_after',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'saraf_account',
                'currency',
                'transaction_type',
                'amount',
                'description'
            )
        }),
        ('Performer Information', {
            'fields': (
                'performer_user_id',
                'performer_user_type',
                'performer_full_name',
                'performer_employee_id',
                'performer_employee_name'
            )
        }),
        ('Balance Information', {
            'fields': (
                'balance_before',
                'balance_after'
            )
        }),
        ('Date and Time', {
            'fields': (
                'created_at',
                'updated_at'
            )
        })
    )
    
    ordering = ['-created_at']
    
    def delete_model(self, request, obj):
        """Delete transaction and update balance"""
        from saraf_balance.models import SarafBalance
        from django.db import transaction
        
        with transaction.atomic():
            # Restore balance
            balance = SarafBalance.objects.get(
                saraf_account=obj.saraf_account,
                currency=obj.currency
            )
            
            # Reverse transaction
            if obj.transaction_type == 'deposit':
                # Check if reversing deposit would create negative balance
                if balance.balance < obj.amount:
                    from django.contrib import messages
                    messages.error(request, 
                        f'Cannot delete deposit transaction. '
                        f'Current balance ({balance.balance} {obj.currency.currency_code}) '
                        f'is less than deposit amount ({obj.amount} {obj.currency.currency_code}). '
                        f'This would result in negative balance.'
                    )
                    return
                balance.balance -= obj.amount
                balance.total_deposits -= obj.amount
            elif obj.transaction_type == 'withdrawal':
                balance.balance += obj.amount
                balance.total_withdrawals -= obj.amount
            
            balance.transaction_count -= 1
            balance.save()
            
            # Delete transaction
            super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Delete multiple transactions"""
        from saraf_balance.models import SarafBalance
        from django.db import transaction
        
        with transaction.atomic():
            for obj in queryset:
                # Restore balance
                balance = SarafBalance.objects.get(
                    saraf_account=obj.saraf_account,
                    currency=obj.currency
                )
                
                # Reverse transaction
                if obj.transaction_type == 'deposit':
                    # Check if reversing deposit would create negative balance
                    if balance.balance < obj.amount:
                        from django.contrib import messages
                        messages.error(request, 
                            f'Cannot delete deposit transaction ID {obj.transaction_id}. '
                            f'Current balance ({balance.balance} {obj.currency.currency_code}) '
                            f'is less than deposit amount ({obj.amount} {obj.currency.currency_code}). '
                            f'This would result in negative balance. Bulk deletion cancelled.'
                        )
                        return
                    balance.balance -= obj.amount
                    balance.total_deposits -= obj.amount
                elif obj.transaction_type == 'withdrawal':
                    balance.balance += obj.amount
                    balance.total_withdrawals -= obj.amount
                
                balance.transaction_count -= 1
                balance.save()
            
            # Delete transactions
            queryset.delete()
    
    def has_delete_permission(self, request, obj=None):
        """Permission to delete transactions for superuser"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Restrict editing of transactions"""
        return request.user.is_superuser