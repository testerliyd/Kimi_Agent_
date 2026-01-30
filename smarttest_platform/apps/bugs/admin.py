"""
Bug管理后台配置
"""
from django.contrib import admin
from .models import Bug, BugComment, BugHistory


@admin.register(Bug)
class BugAdmin(admin.ModelAdmin):
    list_display = ['bug_no', 'title', 'project', 'severity', 'priority', 'status', 'assignee', 'created_at']
    list_filter = ['bug_type', 'severity', 'priority', 'status', 'created_at']
    search_fields = ['bug_no', 'title', 'description']
    date_hierarchy = 'created_at'


@admin.register(BugComment)
class BugCommentAdmin(admin.ModelAdmin):
    list_display = ['bug', 'content', 'created_by', 'created_at']
    search_fields = ['content']


@admin.register(BugHistory)
class BugHistoryAdmin(admin.ModelAdmin):
    list_display = ['bug', 'action', 'field', 'operator', 'created_at']
    list_filter = ['action', 'created_at']
