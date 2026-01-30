"""
飞书机器人后台管理
"""
from django.contrib import admin
from .models import FeishuConfig, FeishuMessageTemplate, FeishuNotificationLog, FeishuChatBinding


@admin.register(FeishuConfig)
class FeishuConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'app_id', 'is_default', 'is_active', 'created_at']
    list_filter = ['is_default', 'is_active', 'created_at']
    search_fields = ['name', 'app_id']


@admin.register(FeishuMessageTemplate)
class FeishuMessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_default', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_default', 'is_active']
    search_fields = ['name']


@admin.register(FeishuNotificationLog)
class FeishuNotificationLogAdmin(admin.ModelAdmin):
    list_display = ['config', 'message_type', 'chat_id', 'status', 'created_at']
    list_filter = ['message_type', 'status', 'created_at']
    search_fields = ['chat_id']


@admin.register(FeishuChatBinding)
class FeishuChatBindingAdmin(admin.ModelAdmin):
    list_display = ['project', 'chat_name', 'notify_bug_created', 'notify_test_completed', 'created_at']
    list_filter = ['notify_bug_created', 'notify_bug_status_change', 'notify_test_completed']
    search_fields = ['chat_name', 'chat_id']
