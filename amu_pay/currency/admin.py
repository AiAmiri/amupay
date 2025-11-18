from django.contrib import admin
from .models import Currency, SarafSupportedCurrency


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['currency_code', 'currency_name', 'currency_name_local', 'symbol', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['currency_code', 'currency_name', 'currency_name_local']
    ordering = ['currency_code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('currency_code', 'currency_name', 'currency_name_local', 'symbol')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SarafSupportedCurrency)
class SarafSupportedCurrencyAdmin(admin.ModelAdmin):
    list_display = ['saraf_account', 'currency', 'is_active', 'added_at', 'get_added_by']
    list_filter = ['is_active', 'currency', 'added_at']
    search_fields = ['saraf_account__full_name', 'currency__currency_code', 'currency__currency_name']
    ordering = ['-added_at']
    readonly_fields = ['added_at']
    
    def get_added_by(self, obj):
        """Display who added the currency"""
        if obj.added_by_employee:
            return f"Employee: {obj.added_by_employee.full_name}"
        elif obj.added_by_saraf:
            return f"Exchange: {obj.added_by_saraf.full_name}"
        return "Unknown"
    get_added_by.short_description = "Added By"
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('saraf_account', 'currency', 'is_active')
        }),
        ('Added By Information', {
            'fields': ('added_by_saraf', 'added_by_employee'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('added_at',),
            'classes': ('collapse',)
        }),
    )