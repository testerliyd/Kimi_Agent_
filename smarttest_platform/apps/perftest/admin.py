"""
性能测试后台配置
"""
from django.contrib import admin
from .models import PerfTestScenario, PerfTestJob, PerfTestMetrics


@admin.register(PerfTestScenario)
class PerfTestScenarioAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'scenario_type', 'concurrent_users', 'is_active', 'created_at']
    list_filter = ['scenario_type', 'is_active', 'created_at']
    search_fields = ['name', 'target_url']


@admin.register(PerfTestJob)
class PerfTestJobAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'avg_response_time', 'error_rate', 'created_at']
    list_filter = ['status', 'trigger_type', 'created_at']
    search_fields = ['name']


@admin.register(PerfTestMetrics)
class PerfTestMetricsAdmin(admin.ModelAdmin):
    list_display = ['job', 'timestamp', 'avg_response_time', 'requests_per_second', 'current_users']
    list_filter = ['timestamp']
