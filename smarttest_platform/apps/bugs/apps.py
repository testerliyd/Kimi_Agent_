"""
Bug管理应用配置
"""
from django.apps import AppConfig


class BugsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bugs'
    verbose_name = 'Bug管理'
