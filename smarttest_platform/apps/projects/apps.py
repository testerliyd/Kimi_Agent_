"""
项目管理应用配置
"""
from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    """
    项目管理应用配置类
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.projects'
    verbose_name = '项目管理'

    def ready(self):
        """
        应用就绪时执行的初始化操作
        """
        pass
