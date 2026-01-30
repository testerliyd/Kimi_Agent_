"""
大模型配置后台管理
"""
from django.contrib import admin
from .models import LLMProvider, LLMConfig, LLMConversation, LLMMessage, LLMTestGeneration


@admin.register(LLMProvider)
class LLMProviderAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'api_key_required', 'is_active']
    list_filter = ['api_key_required', 'is_active']
    search_fields = ['code', 'name']


@admin.register(LLMConfig)
class LLMConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'default_model', 'is_default', 'is_active', 'usage_count']
    list_filter = ['is_default', 'is_active']
    search_fields = ['name']


@admin.register(LLMConversation)
class LLMConversationAdmin(admin.ModelAdmin):
    list_display = ['title', 'config', 'message_count', 'token_usage', 'created_at']
    search_fields = ['title']


@admin.register(LLMMessage)
class LLMMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'content_preview', 'total_tokens', 'created_at']
    list_filter = ['role', 'created_at']
    
    def content_preview(self, obj):
        return obj.content[:50]
    content_preview.short_description = '内容预览'


@admin.register(LLMTestGeneration)
class LLMTestGenerationAdmin(admin.ModelAdmin):
    list_display = ['generation_type', 'config', 'project', 'total_tokens', 'rating', 'created_at']
    list_filter = ['generation_type', 'created_at']
