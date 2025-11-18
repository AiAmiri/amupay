from django.contrib import admin
from .models import SarafLike, SarafComment, SarafSocialStats

@admin.register(SarafLike)
class SarafLikeAdmin(admin.ModelAdmin):
    list_display = ['like_id', 'saraf_account', 'normal_user', 'created_at']
    list_filter = ['created_at', 'saraf_account']
    search_fields = ['saraf_account__full_name', 'normal_user__full_name', 'normal_user__email']
    readonly_fields = ['like_id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Like Information', {
            'fields': ('like_id', 'saraf_account', 'normal_user', 'created_at')
        }),
    )

@admin.register(SarafComment)
class SarafCommentAdmin(admin.ModelAdmin):
    list_display = ['comment_id', 'saraf_account', 'normal_user', 'created_at']
    list_filter = ['created_at', 'saraf_account']
    search_fields = ['saraf_account__full_name', 'normal_user__full_name', 'normal_user__email', 'content']
    readonly_fields = ['comment_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('comment_id', 'saraf_account', 'normal_user', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SarafSocialStats)
class SarafSocialStatsAdmin(admin.ModelAdmin):
    list_display = ['stats_id', 'saraf_account', 'total_likes', 'total_comments', 'last_updated']
    list_filter = ['last_updated']
    search_fields = ['saraf_account__full_name', 'saraf_account__saraf_id']
    readonly_fields = ['stats_id', 'last_updated']
    ordering = ['-total_likes', '-total_comments']
    
    fieldsets = (
        ('Statistics', {
            'fields': ('stats_id', 'saraf_account', 'total_likes', 'total_comments')
        }),
        ('Timestamps', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['update_stats']
    
    def update_stats(self, request, queryset):
        """Update statistics for selected Saraf accounts"""
        updated = 0
        for stats in queryset:
            stats.update_stats()
            updated += 1
        self.message_user(request, f'Statistics updated for {updated} Saraf accounts.')
    update_stats.short_description = "Update statistics for selected accounts"