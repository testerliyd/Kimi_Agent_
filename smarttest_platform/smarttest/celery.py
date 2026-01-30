"""
Celery配置模块
用于异步任务处理和定时任务调度
"""

import os
from celery import Celery

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarttest.settings')

# 创建Celery应用实例
app = Celery('smarttest')

# 从Django设置中加载配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    调试任务，用于验证Celery是否正常工作
    """
    print(f'Request: {self.request!r}')
