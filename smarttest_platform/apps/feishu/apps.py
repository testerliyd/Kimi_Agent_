"""
飞书机器人应用配置
"""
from django.apps import AppConfig


class FeishuConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.feishu'
    verbose_name = '飞书集成'
