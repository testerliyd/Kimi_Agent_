"""
用户管理后台配置
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Role, UserRole, Permission, UserLoginLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    用户后台管理
    """
    list_display = [
        'username', 'email', 'nickname', 'user_type',
        'status', 'is_staff', 'is_active', 'date_joined'
    ]
    list_filter = ['user_type', 'status', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'nickname', 'phone', 'department']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {
            'fields': ('email', 'phone', 'nickname', 'avatar', 'department', 'position')
        }),
        (_('权限'), {
            'fields': ('user_type', 'status', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('飞书集成'), {
            'fields': ('feishu_user_id', 'feishu_open_id'),
            'classes': ('collapse',)
        }),
        (_('重要日期'), {
            'fields': ('last_login', 'date_joined', 'last_activity_at'),
            'classes': ('collapse',)
        }),
        (_('偏好设置'), {
            'fields': ('preferences',),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type'),
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    角色后台管理
    """
    list_display = ['name', 'code', 'role_type', 'is_default', 'get_user_count', 'created_at']
    list_filter = ['role_type', 'is_default']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_user_count(self, obj):
        """获取拥有该角色的用户数量"""
        return obj.role_users.count()
    get_user_count.short_description = '用户数量'


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    用户角色关联后台管理
    """
    list_display = ['user', 'role', 'project', 'assigned_at', 'assigned_by']
    list_filter = ['role', 'assigned_at']
    search_fields = ['user__username', 'role__name']
    readonly_fields = ['assigned_at']


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    权限后台管理
    """
    list_display = ['name', 'code', 'category', 'created_at']
    list_filter = ['category']
    search_fields = ['name', 'code', 'description']


@admin.register(UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    """
    用户登录日志后台管理
    """
    list_display = ['user', 'login_type', 'ip_address', 'status', 'created_at']
    list_filter = ['login_type', 'status', 'created_at']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = [
        'user', 'login_type', 'ip_address', 'user_agent',
        'status', 'fail_reason', 'created_at'
    ]
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
