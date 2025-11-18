from django.contrib import admin
from .models import SarafPost


@admin.register(SarafPost)
class SarafPostAdmin(admin.ModelAdmin):
    """
    Admin interface for SarafPost model
    """
    list_display = [
        'id',
        'title',
        'saraf_account',
        'created_at',
        'published_at'
    ]
    
    list_filter = [
        'saraf_account',
        'created_at',
        'published_at'
    ]
    
    search_fields = [
        'title',
        'content',
        'saraf_account__full_name',
        'created_by_saraf__full_name',
        'created_by_employee__full_name'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'word_count',
        'character_count'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'content',
                'photo'
            )
        }),
        ('Account Information', {
            'fields': (
                'saraf_account',
                'created_by_saraf',
                'created_by_employee'
            )
        }),
        ('Post Settings', {
            'fields': (
                'published_at',
            )
        }),
        ('Statistics', {
            'fields': (
                'word_count',
                'character_count'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-published_at', '-created_at']
    
    def get_queryset(self, request):
        """Optimize queryset for admin"""
        return super().get_queryset(request).select_related(
            'saraf_account',
            'created_by_saraf',
            'created_by_employee'
        )
    
    def has_add_permission(self, request):
        """Allow adding new posts"""
        return True
    
    def has_change_permission(self, request, obj=None):
        """Allow changing posts"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting posts"""
        return True