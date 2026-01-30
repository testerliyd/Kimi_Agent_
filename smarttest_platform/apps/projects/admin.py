"""
项目管理后台配置
"""
from django.contrib import admin
from .models import Project, ProjectMember, ProjectVersion, ProjectMilestone, ProjectEnvironment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    项目后台管理
    """
    list_display = ['code', 'name', 'project_type', 'status', 'priority', 'owner', 'created_at']
    list_filter = ['project_type', 'status', 'priority', 'created_at']
    search_fields = ['code', 'name', 'description']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'name', 'description', 'project_type', 'priority', 'status')
        }),
        ('时间规划', {
            'fields': ('start_date', 'end_date')
        }),
        ('负责人', {
            'fields': ('owner',)
        }),
        ('配置', {
            'fields': ('config', 'jira_project_key', 'git_repository'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """
    项目成员后台管理
    """
    list_display = ['project', 'user', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['project__name', 'user__username']


@admin.register(ProjectVersion)
class ProjectVersionAdmin(admin.ModelAdmin):
    """
    项目版本后台管理
    """
    list_display = ['project', 'version', 'name', 'status', 'planned_start_date', 'planned_end_date']
    list_filter = ['status', 'created_at']
    search_fields = ['project__name', 'version', 'name']


@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    """
    项目里程碑后台管理
    """
    list_display = ['project', 'name', 'status', 'planned_date', 'actual_date']
    list_filter = ['status', 'planned_date']
    search_fields = ['project__name', 'name']


@admin.register(ProjectEnvironment)
class ProjectEnvironmentAdmin(admin.ModelAdmin):
    """
    项目环境后台管理
    """
    list_display = ['project', 'name', 'env_type', 'base_url', 'is_active']
    list_filter = ['env_type', 'is_active']
    search_fields = ['project__name', 'name', 'base_url']
