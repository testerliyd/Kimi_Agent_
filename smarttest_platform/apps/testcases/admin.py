"""
用例管理后台配置
"""
from django.contrib import admin
from .models import TestCase, TestSuite, TestPlan


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['case_no', 'name', 'project', 'case_type', 'priority', 'status', 'created_at']
    list_filter = ['case_type', 'priority', 'status', 'created_at']
    search_fields = ['case_no', 'name', 'description']
    date_hierarchy = 'created_at'


@admin.register(TestSuite)
class TestSuiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'created_at']
    search_fields = ['name', 'description']


@admin.register(TestPlan)
class TestPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'status', 'manager', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
