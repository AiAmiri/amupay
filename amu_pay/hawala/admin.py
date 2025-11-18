from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import HawalaTransaction, HawalaReceipt


@admin.register(HawalaTransaction)
class HawalaTransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for HawalaTransaction model
    """
    list_display = [
        'hawala_number', 'sender_name', 'receiver_name', 'amount', 
        'currency', 'status', 'mode', 'created_at', 'sender_exchange_link',
        'destination_exchange_display'
    ]
    list_filter = [
        'status', 'mode', 'currency', 'destination_saraf_uses_app',
        'created_at', 'sender_exchange'
    ]
    search_fields = [
        'hawala_number', 'sender_name', 'receiver_name', 
        'sender_phone', 'receiver_phone', 'sender_exchange_name',
        'destination_exchange_name'
    ]
    readonly_fields = [
        'hawala_number', 'created_at', 'sent_at',
        'received_at', 'completed_at', 'updated_at'
    ]
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'hawala_number', 'status', 'mode',
                'destination_saraf_uses_app'
            )
        }),
        ('Sender Information', {
            'fields': (
                'sender_name', 'sender_phone', 'sender_exchange',
                'sender_exchange_name'
            )
        }),
        ('Receiver Information', {
            'fields': (
                'receiver_name', 'receiver_phone', 'receiver_photo'
            )
        }),
        ('Transaction Details', {
            'fields': (
                'amount', 'currency', 'transfer_fee', 'notes'
            )
        }),
        ('Destination Exchange', {
            'fields': (
                'destination_exchange_id', 'destination_exchange_name',
                'destination_exchange_address'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'sent_at', 'received_at', 'completed_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
        ('Employee Tracking', {
            'fields': (
                'created_by_employee', 'received_by_employee'
            ),
            'classes': ('collapse',)
        })
    )
    
    def sender_exchange_link(self, obj):
        """Create a link to the sender exchange admin page"""
        if obj.sender_exchange:
            url = reverse('admin:saraf_account_sarafaccount_change', args=[obj.sender_exchange.pk])
            return format_html('<a href="{}">{}</a>', url, obj.sender_exchange.full_name)
        return '-'
    sender_exchange_link.short_description = 'Sender Exchange'
    sender_exchange_link.admin_order_field = 'sender_exchange__full_name'
    
    def destination_exchange_display(self, obj):
        """Display destination exchange information"""
        if obj.destination_exchange_id:
            try:
                from saraf_account.models import SarafAccount
                destination = SarafAccount.objects.get(saraf_id=obj.destination_exchange_id)
                url = reverse('admin:saraf_account_sarafaccount_change', args=[destination.pk])
                return format_html('<a href="{}">{}</a>', url, destination.full_name)
            except SarafAccount.DoesNotExist:
                return f"ID: {obj.destination_exchange_id} (Not Found)"
        return obj.destination_exchange_name or '-'
    destination_exchange_display.short_description = 'Destination Exchange'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'currency', 'sender_exchange', 'created_by_employee', 'received_by_employee'
        )
    
    def has_add_permission(self, request):
        """Allow adding hawala transactions"""
        return True
    
    def has_change_permission(self, request, obj=None):
        """Allow changing hawala transactions"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting hawala transactions"""
        return True
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly based on status"""
        readonly_fields = list(self.readonly_fields)
        
        if obj and obj.status in ['completed', 'cancelled']:
            # Make most fields readonly for completed/cancelled transactions
            readonly_fields.extend([
                'sender_name', 'sender_phone', 'receiver_name', 'receiver_phone',
                'amount', 'currency', 'transfer_fee', 'sender_exchange',
                'destination_exchange_id', 'destination_exchange_name',
                'destination_exchange_address', 'mode', 'destination_saraf_uses_app'
            ])
        
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        """Custom save logic"""
        if not change:  # Creating new object
            # Set created_by_employee if not set
            if not obj.created_by_employee and hasattr(request.user, 'saraf_account'):
                try:
                    from saraf_account.models import SarafEmployee
                    employee = SarafEmployee.objects.get(
                        saraf_account=request.user.saraf_account,
                        username=request.user.username
                    )
                    obj.created_by_employee = employee
                except SarafEmployee.DoesNotExist:
                    pass
        
        super().save_model(request, obj, form, change)
    
    actions = ['mark_as_sent', 'mark_as_received', 'mark_as_completed', 'cancel_transaction']
    
    def mark_as_sent(self, request, queryset):
        """Mark selected transactions as sent"""
        count = 0
        for hawala in queryset.filter(status='pending'):
            hawala.mark_as_sent()
            count += 1
        
        self.message_user(request, f'{count} transactions marked as sent.')
    mark_as_sent.short_description = "Mark selected transactions as sent"
    
    def mark_as_received(self, request, queryset):
        """Mark selected transactions as received"""
        count = 0
        for hawala in queryset.filter(status__in=['pending', 'sent']):
            hawala.mark_as_received()
            count += 1
        
        self.message_user(request, f'{count} transactions marked as received.')
    mark_as_received.short_description = "Mark selected transactions as received"
    
    def mark_as_completed(self, request, queryset):
        """Mark selected transactions as completed"""
        count = 0
        for hawala in queryset.filter(status='received'):
            hawala.mark_as_completed()
            count += 1
        
        self.message_user(request, f'{count} transactions marked as completed.')
    mark_as_completed.short_description = "Mark selected transactions as completed"
    
    def cancel_transaction(self, request, queryset):
        """Cancel selected transactions"""
        count = 0
        for hawala in queryset.filter(status__in=['pending', 'sent']):
            hawala.cancel_transaction()
            count += 1
        
        self.message_user(request, f'{count} transactions cancelled.')
    cancel_transaction.short_description = "Cancel selected transactions"


@admin.register(HawalaReceipt)
class HawalaReceiptAdmin(admin.ModelAdmin):
    """
    Admin interface for HawalaReceipt model
    """
    list_display = [
        'receipt_id', 'hawala_transaction_link', 'generated_at',
        'generated_by_employee_link', 'is_active'
    ]
    list_filter = [
        'is_active', 'generated_at', 'generated_by_employee'
    ]
    search_fields = [
        'receipt_id', 'hawala_transaction__hawala_number',
        'generated_by_employee__full_name'
    ]
    readonly_fields = [
        'receipt_id', 'generated_at', 'receipt_data'
    ]
    fieldsets = (
        ('Receipt Information', {
            'fields': (
                'receipt_id', 'hawala_transaction', 'generated_at',
                'generated_by_employee', 'is_active'
            )
        }),
        ('Receipt Data', {
            'fields': ('receipt_data',),
            'classes': ('collapse',)
        })
    )
    
    def hawala_transaction_link(self, obj):
        """Create a link to the hawala transaction admin page"""
        if obj.hawala_transaction:
            url = reverse('admin:hawala_hawalatransaction_change', args=[obj.hawala_transaction.pk])
            return format_html('<a href="{}">{}</a>', url, obj.hawala_transaction.hawala_number)
        return '-'
    hawala_transaction_link.short_description = 'Hawala Transaction'
    hawala_transaction_link.admin_order_field = 'hawala_transaction__hawala_number'
    
    def generated_by_employee_link(self, obj):
        """Create a link to the employee admin page"""
        if obj.generated_by_employee:
            url = reverse('admin:saraf_account_sarafemployee_change', args=[obj.generated_by_employee.pk])
            return format_html('<a href="{}">{}</a>', url, obj.generated_by_employee.full_name)
        return '-'
    generated_by_employee_link.short_description = 'Generated By'
    generated_by_employee_link.admin_order_field = 'generated_by_employee__full_name'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'hawala_transaction', 'generated_by_employee'
        )
    
    def has_add_permission(self, request):
        """Prevent manual addition of receipts"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow viewing but not changing receipts"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of receipts"""
        return False
