"""
报告管理后台配置
"""
from django.contrib import admin
from .models import ReportTemplate, Report


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_default', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_default', 'is_active']
    search_fields = ['name', 'description']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'project', 'status', 'format', 'created_at']
    list_filter = ['report_type', 'status', 'format', 'created_at']
    search_fields = ['name', 'description']
