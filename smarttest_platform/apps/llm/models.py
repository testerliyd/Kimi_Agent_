"""
大模型API配置管理模块
支持多厂商大模型API配置
"""
from django.db import models
from django.conf import settings

from apps.core.models import BaseModel

# User model reference: settings.AUTH_USER_MODEL


class LLMProvider(BaseModel):
    """
    大模型提供商模型
    """
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic Claude'),
        ('google', 'Google Gemini'),
        ('baidu', '百度文心一言'),
        ('alibaba', '阿里通义千问'),
        ('xunfei', '讯飞星火'),
        ('zhipu', '智谱AI'),
        ('moonshot', '月之暗面Kimi'),
        ('deepseek', 'DeepSeek'),
        ('minimax', 'MiniMax'),
        ('zeroone', '零一万物'),
        ('custom', '自定义'),
    ]
    
    code = models.CharField('提供商代码', max_length=50, unique=True, choices=PROVIDER_CHOICES)
    name = models.CharField('提供商名称', max_length=100)
    description = models.TextField('描述', blank=True)
    
    # API配置
    base_url = models.URLField('基础URL', blank=True)
    api_key_required = models.BooleanField('需要API Key', default=True)
    api_secret_required = models.BooleanField('需要API Secret', default=False)
    
    # 支持的模型
    supported_models = models.JSONField('支持的模型', default=list, help_text='支持的模型列表')
    
    # 状态
    is_active = models.BooleanField('是否启用', default=True)
    
    class Meta:
        verbose_name = '大模型提供商'
        verbose_name_plural = '大模型提供商'
        ordering = ['name']

    def __str__(self):
        return self.name


class LLMConfig(BaseModel):
    """
    大模型配置模型
    用户的大模型API配置
    """
    name = models.CharField('配置名称', max_length=200)
    provider = models.ForeignKey(
        LLMProvider,
        verbose_name='提供商',
        on_delete=models.CASCADE,
        related_name='configs'
    )
    
    # 认证信息（加密存储）
    api_key = models.CharField('API Key', max_length=500, blank=True)
    api_secret = models.CharField('API Secret', max_length=500, blank=True)
    
    # 自定义配置
    custom_base_url = models.URLField('自定义基础URL', blank=True)
    default_model = models.CharField('默认模型', max_length=100, blank=True)
    
    # 参数配置
    max_tokens = models.PositiveIntegerField('最大Token数', default=2048)
    temperature = models.FloatField('Temperature', default=0.7)
    top_p = models.FloatField('Top P', default=1.0)
    
    # 状态
    is_default = models.BooleanField('默认配置', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    
    # 使用统计
    usage_count = models.PositiveIntegerField('使用次数', default=0)
    last_used_at = models.DateTimeField('最后使用时间', null=True, blank=True)
    
    class Meta:
        verbose_name = '大模型配置'
        verbose_name_plural = '大模型配置'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.provider.name})"

    def get_api_key_display(self):
        """
        脱敏显示API Key
        """
        if not self.api_key:
            return ''
        if len(self.api_key) <= 8:
            return '*' * len(self.api_key)
        return self.api_key[:4] + '*' * (len(self.api_key) - 8) + self.api_key[-4:]

    def increment_usage(self):
        """
        增加使用计数
        """
        from django.utils import timezone
        self.usage_count += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['usage_count', 'last_used_at'])


class LLMConversation(BaseModel):
    """
    大模型对话模型
    """
    config = models.ForeignKey(
        LLMConfig,
        verbose_name='大模型配置',
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    title = models.CharField('对话标题', max_length=200, blank=True)
    
    # 关联信息
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='关联项目',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='llm_conversations'
    )
    
    # 上下文
    context = models.JSONField('对话上下文', default=list, blank=True)
    
    # 统计
    message_count = models.PositiveIntegerField('消息数', default=0)
    token_usage = models.PositiveIntegerField('Token使用量', default=0)
    
    class Meta:
        verbose_name = '大模型对话'
        verbose_name_plural = '大模型对话'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title or f'对话 #{self.id}'


class LLMMessage(BaseModel):
    """
    大模型消息模型
    """
    ROLE_CHOICES = [
        ('system', '系统'),
        ('user', '用户'),
        ('assistant', '助手'),
    ]
    
    conversation = models.ForeignKey(
        LLMConversation,
        verbose_name='对话',
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES)
    content = models.TextField('内容')
    
    # Token使用量
    prompt_tokens = models.PositiveIntegerField('Prompt Tokens', default=0)
    completion_tokens = models.PositiveIntegerField('Completion Tokens', default=0)
    total_tokens = models.PositiveIntegerField('Total Tokens', default=0)
    
    # 性能
    response_time_ms = models.PositiveIntegerField('响应时间(ms)', null=True, blank=True)
    
    class Meta:
        verbose_name = '大模型消息'
        verbose_name_plural = '大模型消息'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:50]}"


class LLMTestGeneration(BaseModel):
    """
    AI生成测试用例记录
    """
    GENERATION_TYPE_CHOICES = [
        ('testcase', '测试用例'),
        ('api_test', 'API测试'),
        ('bug_analysis', 'Bug分析'),
        ('code_review', '代码审查'),
    ]
    
    config = models.ForeignKey(
        LLMConfig,
        verbose_name='使用的配置',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generations'
    )
    
    generation_type = models.CharField('生成类型', max_length=20, choices=GENERATION_TYPE_CHOICES)
    
    # 输入
    prompt = models.TextField('提示词')
    context = models.JSONField('上下文', default=dict, blank=True)
    
    # 输出
    result = models.TextField('生成结果')
    
    # 关联
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='关联项目',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='llm_generations'
    )
    
    # 使用统计
    prompt_tokens = models.PositiveIntegerField('Prompt Tokens', default=0)
    completion_tokens = models.PositiveIntegerField('Completion Tokens', default=0)
    total_tokens = models.PositiveIntegerField('Total Tokens', default=0)
    response_time_ms = models.PositiveIntegerField('响应时间(ms)', null=True, blank=True)
    
    # 评价
    rating = models.PositiveSmallIntegerField('评分', null=True, blank=True)
    feedback = models.TextField('反馈', blank=True)
    
    class Meta:
        verbose_name = 'AI生成记录'
        verbose_name_plural = 'AI生成记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_generation_type_display()} - {self.created_at}"
