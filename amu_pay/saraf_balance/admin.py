from django.contrib import admin
from .models import SarafBalance


@admin.register(SarafBalance)
class SarafBalanceAdmin(admin.ModelAdmin):
    list_display = [
        'saraf_account', 
        'currency', 
        'balance', 
        'total_deposits', 
        'total_withdrawals',
        'transaction_count',
        'last_updated'
    ]
    list_filter = [
        'currency', 
        'saraf_account', 
        'last_updated',
        'created_at'
    ]
    search_fields = [
        'saraf_account__full_name', 
        'currency__currency_code',
        'currency__currency_name'
    ]
    ordering = ['-last_updated']
    readonly_fields = [
        'balance_id',
        'last_updated', 
        'created_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('saraf_account', 'currency')
        }),
        ('Balance', {
            'fields': ('balance', 'total_deposits', 'total_withdrawals', 'transaction_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Read-only fields"""
        readonly = list(self.readonly_fields)
        
        # If balance exists, cannot change exchange and currency
        if obj:
            readonly.extend(['saraf_account', 'currency'])
            
        return readonly
    
    def has_delete_permission(self, request, obj=None):
        """Allow balance deletion for superuser only"""
        return request.user.is_superuser
    
    def delete_model(self, request, obj):
        """Delete balance with related transactions check"""
        from transaction.models import Transaction
        
        # Check for related transactions
        transaction_count = Transaction.objects.filter(
            saraf_account=obj.saraf_account,
            currency=obj.currency
        ).count()
        
        if transaction_count > 0:
            from django.contrib import messages
            messages.error(
                request, 
                f'Cannot delete balance {obj.currency.currency_code} because {transaction_count} related transactions exist.'
            )
            return
        
        super().delete_model(request, obj)
    
    def delete_queryset(self, request, queryset):
        """Delete multiple balances"""
        from transaction.models import Transaction
        from django.contrib import messages
        
        errors = []
        for obj in queryset:
            transaction_count = Transaction.objects.filter(
                saraf_account=obj.saraf_account,
                currency=obj.currency
            ).count()
            
            if transaction_count > 0:
                errors.append(f'{obj.saraf_account.full_name} - {obj.currency.currency_code} ({transaction_count} transactions)')
        
        if errors:
            messages.error(
                request,
                f'Cannot delete the following balances because they have related transactions: {", ".join(errors)}'
            )
            return
        
        queryset.delete()