from django.contrib import admin
from .models import ExchangeTransaction


@admin.register(ExchangeTransaction)
class ExchangeTransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for ExchangeTransaction model
    """
    list_display = [
        'id',
        'name',
        'transaction_type',
        'sell_currency',
        'sell_amount',
        'buy_currency',
        'buy_amount',
        'rate',
        'saraf_account',
        'transaction_date',
        'created_at'
    ]
    
    list_filter = [
        'transaction_type',
        'sell_currency',
        'buy_currency',
        'saraf_account',
        'transaction_date',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'saraf_account__full_name',
        'performed_by_saraf__full_name',
        'performed_by_employee__full_name',
        'notes'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'transaction_type',
                'notes'
            )
        }),
        ('Currency Exchange', {
            'fields': (
                'sell_currency',
                'sell_amount',
                'buy_currency',
                'buy_amount',
                'rate'
            )
        }),
        ('Account Information', {
            'fields': (
                'saraf_account',
                'performed_by_saraf',
                'performed_by_employee'
            )
        }),
        ('Timestamps', {
            'fields': (
                'transaction_date',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-transaction_date', '-created_at']
    
    def get_queryset(self, request):
        """Optimize queryset for admin"""
        return super().get_queryset(request).select_related(
            'saraf_account',
            'performed_by_saraf',
            'performed_by_employee'
        )
    
    def has_add_permission(self, request):
        """Allow adding new exchange transactions"""
        return True
    
    def has_change_permission(self, request, obj=None):
        """Allow changing exchange transactions"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting exchange transactions"""
        return True
