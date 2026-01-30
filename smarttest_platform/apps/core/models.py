"""
核心模型模块
包含基础模型类和公共字段定义
"""
from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """
    基础模型类
    所有模型都应继承此类，包含通用的创建时间、更新时间、创建人、更新人字段
    """
    created_at = models.DateTimeField('创建时间', auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='创建人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='更新人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )
    is_deleted = models.BooleanField('是否删除', default=False, db_index=True)
    deleted_at = models.DateTimeField('删除时间', null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='删除人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self, user=None):
        """
        软删除方法
        不真正删除数据，而是标记为已删除
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

    def restore(self):
        """
        恢复软删除的数据
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])


class BaseStatusModel(BaseModel):
    """
    带状态的基础模型类
    适用于需要状态流转的业务对象
    """
    STATUS_CHOICES = []
    
    status = models.CharField(
        '状态',
        max_length=50,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    status_changed_at = models.DateTimeField('状态变更时间', null=True, blank=True)
    status_changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='状态变更人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_status_changed'
    )

    class Meta:
        abstract = True

    def change_status(self, new_status, user=None):
        """
        变更状态方法
        自动记录状态变更时间和操作人
        """
        from django.utils import timezone
        old_status = self.status
        self.status = new_status
        self.status_changed_at = timezone.now()
        if user:
            self.status_changed_by = user
        self.save(update_fields=['status', 'status_changed_at', 'status_changed_by'])
        return old_status, new_status


class AuditLog(models.Model):
    """
    审计日志模型
    记录所有重要操作的日志
    """
    ACTION_CHOICES = [
        ('CREATE', '创建'),
        ('UPDATE', '更新'),
        ('DELETE', '删除'),
        ('VIEW', '查看'),
        ('EXPORT', '导出'),
        ('IMPORT', '导入'),
        ('EXECUTE', '执行'),
        ('APPROVE', '审批'),
        ('REJECT', '驳回'),
        ('OTHER', '其他'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='操作用户',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField('操作类型', max_length=50, choices=ACTION_CHOICES)
    resource_type = models.CharField('资源类型', max_length=100)
    resource_id = models.CharField('资源ID', max_length=100)
    resource_name = models.CharField('资源名称', max_length=255, blank=True)
    old_data = models.JSONField('变更前数据', null=True, blank=True)
    new_data = models.JSONField('变更后数据', null=True, blank=True)
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('用户代理', blank=True)
    description = models.TextField('操作描述', blank=True)
    created_at = models.DateTimeField('操作时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.resource_type}"


class SystemConfig(models.Model):
    """
    系统配置模型
    用于存储系统级别的配置项
    """
    CONFIG_TYPES = [
        ('STRING', '字符串'),
        ('INTEGER', '整数'),
        ('FLOAT', '浮点数'),
        ('BOOLEAN', '布尔值'),
        ('JSON', 'JSON'),
        ('TEXT', '文本'),
    ]
    
    key = models.CharField('配置键', max_length=255, unique=True, db_index=True)
    value = models.TextField('配置值')
    config_type = models.CharField('配置类型', max_length=20, choices=CONFIG_TYPES, default='STRING')
    description = models.TextField('配置说明', blank=True)
    is_public = models.BooleanField('是否公开', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        ordering = ['key']

    def __str__(self):
        return self.key

    def get_typed_value(self):
        """
        根据配置类型返回正确类型的值
        """
        import json
        if self.config_type == 'INTEGER':
            return int(self.value)
        elif self.config_type == 'FLOAT':
            return float(self.value)
        elif self.config_type == 'BOOLEAN':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.config_type == 'JSON':
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return {}
        else:
            return self.value

    @classmethod
    def get_config(cls, key, default=None):
        """
        获取配置值的类方法
        """
        try:
            config = cls.objects.get(key=key)
            return config.get_typed_value()
        except cls.DoesNotExist:
            return default

    @classmethod
    def set_config(cls, key, value, config_type='STRING', description=''):
        """
        设置配置值的类方法
        """
        import json
        if config_type == 'JSON':
            value = json.dumps(value)
        else:
            value = str(value)
        
        config, created = cls.objects.update_or_create(
            key=key,
            defaults={
                'value': value,
                'config_type': config_type,
                'description': description,
            }
        )
        return config
