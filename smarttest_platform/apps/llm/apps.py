"""
大模型配置应用配置
"""
from django.apps import AppConfig


class LlmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.llm'
    verbose_name = '大模型配置'
