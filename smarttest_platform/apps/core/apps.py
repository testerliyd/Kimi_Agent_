"""
核心应用配置
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """
    核心应用配置类
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = '核心模块'

    def ready(self):
        """
        应用就绪时执行的初始化操作
        """
        # 导入信号处理器
        pass
