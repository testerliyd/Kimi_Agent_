"""
飞书机器人集成模块
包含飞书配置、消息模板等模型
"""
from django.db import models
from django.conf import settings

from apps.core.models import BaseModel

# User model reference: settings.AUTH_USER_MODEL


class FeishuConfig(BaseModel):
    """
    飞书配置模型
    """
    name = models.CharField('配置名称', max_length=200)
    
    # 应用凭证
    app_id = models.CharField('App ID', max_length=200)
    app_secret = models.CharField('App Secret', max_length=500)
    
    # 验证令牌
    verification_token = models.CharField('Verification Token', max_length=500, blank=True)
    # 签名校验密钥（用于Webhook方式）
    encrypt_key = models.CharField(
        'Encrypt Key',
        max_length=500,
        blank=True,
        help_text='群聊机器人安全设置中的签名校验密钥，用于生成请求签名'
    )
    
    # Webhook配置（群聊机器人Webhook地址，支持签名校验）
    webhook_url = models.URLField(
        'Webhook URL',
        blank=True,
        help_text='飞书群聊机器人的Webhook地址，格式: https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxx'
    )
    
    # 默认通知设置
    default_chat_id = models.CharField('默认群聊ID', max_length=200, blank=True)
    
    # 状态
    is_default = models.BooleanField('默认配置', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    
    class Meta:
        verbose_name = '飞书配置'
        verbose_name_plural = '飞书配置'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class FeishuMessageTemplate(BaseModel):
    """
    飞书消息模板模型
    """
    TEMPLATE_TYPE_CHOICES = [
        ('bug_created', 'Bug创建'),
        ('bug_assigned', 'Bug分配'),
        ('bug_resolved', 'Bug解决'),
        ('bug_closed', 'Bug关闭'),
        ('bug_reopened', 'Bug重新打开'),
        ('api_test_completed', 'API测试完成'),
        ('perf_test_completed', '性能测试完成'),
        ('custom', '自定义'),
    ]
    
    name = models.CharField('模板名称', max_length=200)
    template_type = models.CharField(
        '模板类型',
        max_length=50,
        choices=TEMPLATE_TYPE_CHOICES,
        default='custom'
    )
    description = models.TextField('模板描述', blank=True)
    
    # 模板内容（JSON格式，符合飞书消息卡片格式）
    template_content = models.JSONField('模板内容', default=dict)
    
    # 变量说明
    variables = models.JSONField('模板变量', default=dict, help_text='模板中使用的变量说明')
    
    # 状态
    is_default = models.BooleanField('默认模板', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    
    class Meta:
        verbose_name = '飞书消息模板'
        verbose_name_plural = '飞书消息模板'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class FeishuNotificationLog(BaseModel):
    """
    飞书通知日志模型
    """
    STATUS_CHOICES = [
        ('pending', '发送中'),
        ('success', '发送成功'),
        ('failed', '发送失败'),
    ]
    
    MESSAGE_TYPE_CHOICES = [
        ('text', '文本消息'),
        ('card', '卡片消息'),
        ('image', '图片消息'),
    ]
    
    config = models.ForeignKey(
        FeishuConfig,
        verbose_name='飞书配置',
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )
    
    # 消息信息
    message_type = models.CharField('消息类型', max_length=20, choices=MESSAGE_TYPE_CHOICES)
    chat_id = models.CharField('群聊ID', max_length=200, blank=True)
    user_id = models.CharField('用户ID', max_length=200, blank=True)
    
    # 消息内容
    content = models.JSONField('消息内容')
    template = models.ForeignKey(
        FeishuMessageTemplate,
        verbose_name='使用的模板',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # 关联对象
    related_object_type = models.CharField('关联对象类型', max_length=100, blank=True)
    related_object_id = models.CharField('关联对象ID', max_length=100, blank=True)
    
    # 发送状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    response_data = models.JSONField('响应数据', default=dict, blank=True)
    error_message = models.TextField('错误信息', blank=True)
    
    class Meta:
        verbose_name = '飞书通知日志'
        verbose_name_plural = '飞书通知日志'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_message_type_display()} - {self.get_status_display()}"


class FeishuChatBinding(BaseModel):
    """
    飞书群聊绑定模型
    绑定项目与飞书群聊
    """
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='项目',
        on_delete=models.CASCADE,
        related_name='feishu_bindings'
    )
    chat_id = models.CharField('飞书群聊ID', max_length=200)
    chat_name = models.CharField('群聊名称', max_length=200, blank=True)
    
    # 通知设置
    notify_bug_created = models.BooleanField('Bug创建通知', default=True)
    notify_bug_status_change = models.BooleanField('Bug状态变更通知', default=True)
    notify_test_completed = models.BooleanField('测试完成通知', default=True)
    
    # 配置
    config = models.ForeignKey(
        FeishuConfig,
        verbose_name='飞书配置',
        on_delete=models.CASCADE,
        related_name='chat_bindings'
    )
    
    class Meta:
        verbose_name = '飞书群聊绑定'
        verbose_name_plural = '飞书群聊绑定'
        unique_together = ['project', 'chat_id']

    def __str__(self):
        return f"{self.project.name} - {self.chat_name or self.chat_id}"
