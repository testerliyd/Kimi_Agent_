"""
性能测试应用配置
"""
from django.apps import AppConfig


class PerftestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.perftest'
    verbose_name = '性能测试'
