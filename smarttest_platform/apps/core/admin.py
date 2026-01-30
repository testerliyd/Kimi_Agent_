"""
核心应用后台管理配置
"""
from django.contrib import admin
from .models import AuditLog, SystemConfig


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    审计日志后台管理
    """
    list_display = [
        'id', 'user', 'action', 'resource_type',
        'resource_name', 'ip_address', 'created_at'
    ]
    list_filter = ['action', 'resource_type', 'created_at']
    search_fields = ['resource_name', 'description', 'user__username']
    readonly_fields = [
        'user', 'action', 'resource_type', 'resource_id',
        'resource_name', 'old_data', 'new_data',
        'ip_address', 'user_agent', 'description', 'created_at'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        """禁止手动添加审计日志"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改审计日志"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """只允许超级管理员删除审计日志"""
        return request.user.is_superuser


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    """
    系统配置后台管理
    """
    list_display = ['key', 'config_type', 'is_public', 'updated_at']
    list_filter = ['config_type', 'is_public', 'created_at']
    search_fields = ['key', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('基本信息', {
            'fields': ('key', 'value', 'config_type', 'description')
        }),
        ('权限设置', {
            'fields': ('is_public',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
