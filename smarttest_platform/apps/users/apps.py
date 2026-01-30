"""
用户应用配置
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    用户应用配置类
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = '用户管理'

    def ready(self):
        """
        应用就绪时执行的初始化操作
        """
        # 导入信号处理器
        pass
