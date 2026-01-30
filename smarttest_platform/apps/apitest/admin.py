"""
接口测试后台配置
"""
from django.contrib import admin
from .models import ApiDefinition, ApiTestCase, ApiTestJob, ApiTestResult


@admin.register(ApiDefinition)
class ApiDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'method', 'path', 'project', 'is_active', 'created_at']
    list_filter = ['method', 'is_active', 'created_at']
    search_fields = ['name', 'path']


@admin.register(ApiTestCase)
class ApiTestCaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'api', 'expected_status', 'is_active', 'created_at']
    search_fields = ['name']


@admin.register(ApiTestJob)
class ApiTestJobAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'executor', 'created_at']
    list_filter = ['status', 'trigger_type', 'created_at']
    search_fields = ['name']


@admin.register(ApiTestResult)
class ApiTestResultAdmin(admin.ModelAdmin):
    list_display = ['test_case', 'status', 'response_status', 'response_time_ms', 'created_at']
    list_filter = ['status', 'created_at']
