"""
接口自动化测试模块
包含API定义、测试用例、测试任务等模型
"""
import json
from django.db import models
from django.conf import settings

from apps.core.models import BaseModel

# User model reference: settings.AUTH_USER_MODEL


class ApiDefinition(BaseModel):
    """
    API定义模型
    """
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
        ('HEAD', 'HEAD'),
        ('OPTIONS', 'OPTIONS'),
    ]
    
    CONTENT_TYPE_CHOICES = [
        ('application/json', 'application/json'),
        ('application/x-www-form-urlencoded', 'application/x-www-form-urlencoded'),
        ('multipart/form-data', 'multipart/form-data'),
        ('text/plain', 'text/plain'),
        ('text/html', 'text/html'),
        ('application/xml', 'application/xml'),
    ]
    
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='api_definitions'
    )
    environment = models.ForeignKey(
        'projects.ProjectEnvironment',
        verbose_name='所属环境',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_definitions'
    )
    
    # API基本信息
    name = models.CharField('API名称', max_length=200)
    description = models.TextField('API描述', blank=True)
    method = models.CharField('请求方法', max_length=10, choices=METHOD_CHOICES, default='GET')
    path = models.CharField('请求路径', max_length=1000)
    
    # 请求配置
    headers = models.JSONField('请求头', default=dict, blank=True)
    params = models.JSONField('URL参数', default=dict, blank=True)
    content_type = models.CharField(
        'Content-Type',
        max_length=100,
        choices=CONTENT_TYPE_CHOICES,
        default='application/json'
    )
    body = models.JSONField('请求体', default=dict, blank=True)
    body_raw = models.TextField('原始请求体', blank=True)
    
    # 认证配置
    auth_type = models.CharField('认证类型', max_length=50, blank=True)
    auth_config = models.JSONField('认证配置', default=dict, blank=True)
    
    # 状态
    is_active = models.BooleanField('是否启用', default=True)
    
    class Meta:
        verbose_name = 'API定义'
        verbose_name_plural = 'API定义'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.method} {self.name}"

    def get_full_url(self):
        """
        获取完整URL
        """
        if self.environment:
            base_url = self.environment.base_url.rstrip('/')
            path = self.path.lstrip('/')
            return f"{base_url}/{path}"
        return self.path


class ApiTestCase(BaseModel):
    """
    API测试用例模型
    """
    api = models.ForeignKey(
        ApiDefinition,
        verbose_name='API定义',
        on_delete=models.CASCADE,
        related_name='test_cases'
    )
    name = models.CharField('用例名称', max_length=200)
    description = models.TextField('用例描述', blank=True)
    
    # 请求覆盖
    override_headers = models.JSONField('覆盖请求头', default=dict, blank=True)
    override_params = models.JSONField('覆盖URL参数', default=dict, blank=True)
    override_body = models.JSONField('覆盖请求体', default=dict, blank=True)
    
    # 验证规则
    expected_status = models.IntegerField('预期状态码', default=200)
    expected_headers = models.JSONField('预期响应头', default=dict, blank=True)
    expected_body = models.JSONField('预期响应体', default=dict, blank=True)
    validation_rules = models.JSONField('验证规则', default=list, blank=True, help_text='JSON Schema验证规则')
    
    # 前置/后置处理
    setup_script = models.TextField('前置脚本', blank=True, help_text='执行请求前的Python脚本')
    teardown_script = models.TextField('后置脚本', blank=True, help_text='执行请求后的Python脚本')
    
    # 状态
    is_active = models.BooleanField('是否启用', default=True)
    
    class Meta:
        verbose_name = 'API测试用例'
        verbose_name_plural = 'API测试用例'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ApiTestJob(BaseModel):
    """
    API测试任务模型
    """
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '执行中'),
        ('passed', '已通过'),
        ('failed', '已失败'),
        ('error', '执行错误'),
        ('cancelled', '已取消'),
    ]
    
    TRIGGER_TYPE_CHOICES = [
        ('manual', '手动触发'),
        ('scheduled', '定时触发'),
        ('webhook', 'Webhook触发'),
        ('ci', 'CI集成'),
    ]
    
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='api_test_jobs'
    )
    name = models.CharField('任务名称', max_length=200)
    description = models.TextField('任务描述', blank=True)
    
    # 测试配置
    test_cases = models.ManyToManyField(
        ApiTestCase,
        verbose_name='测试用例',
        related_name='jobs',
        blank=True
    )
    environment = models.ForeignKey(
        'projects.ProjectEnvironment',
        verbose_name='执行环境',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # 执行信息
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    trigger_type = models.CharField('触发方式', max_length=20, choices=TRIGGER_TYPE_CHOICES, default='manual')
    
    # 统计
    total_cases = models.PositiveIntegerField('总用例数', default=0)
    passed_cases = models.PositiveIntegerField('通过数', default=0)
    failed_cases = models.PositiveIntegerField('失败数', default=0)
    error_cases = models.PositiveIntegerField('错误数', default=0)
    
    # 时间
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    duration = models.PositiveIntegerField('执行时长(秒)', null=True, blank=True)
    
    # 结果
    result_summary = models.JSONField('结果摘要', default=dict, blank=True)
    report_url = models.URLField('报告链接', blank=True)
    
    # 执行人
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='执行人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_test_jobs'
    )
    
    class Meta:
        verbose_name = 'API测试任务'
        verbose_name_plural = 'API测试任务'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def update_statistics(self):
        """
        更新任务统计
        """
        results = self.results.all()
        self.total_cases = results.count()
        self.passed_cases = results.filter(status='passed').count()
        self.failed_cases = results.filter(status='failed').count()
        self.error_cases = results.filter(status='error').count()
        self.save()


class ApiTestResult(BaseModel):
    """
    API测试结果模型
    """
    STATUS_CHOICES = [
        ('passed', '通过'),
        ('failed', '失败'),
        ('error', '错误'),
        ('skipped', '跳过'),
    ]
    
    job = models.ForeignKey(
        ApiTestJob,
        verbose_name='测试任务',
        on_delete=models.CASCADE,
        related_name='results'
    )
    test_case = models.ForeignKey(
        ApiTestCase,
        verbose_name='测试用例',
        on_delete=models.CASCADE,
        related_name='results'
    )
    
    # 执行状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES)
    
    # 请求信息
    request_url = models.URLField('请求URL')
    request_method = models.CharField('请求方法', max_length=10)
    request_headers = models.JSONField('请求头', default=dict)
    request_body = models.TextField('请求体', blank=True)
    
    # 响应信息
    response_status = models.IntegerField('响应状态码')
    response_headers = models.JSONField('响应头', default=dict)
    response_body = models.TextField('响应体', blank=True)
    response_time_ms = models.PositiveIntegerField('响应时间(ms)')
    
    # 验证结果
    validation_results = models.JSONField('验证结果', default=list)
    error_message = models.TextField('错误信息', blank=True)
    
    # 执行时间
    started_at = models.DateTimeField('开始时间')
    completed_at = models.DateTimeField('完成时间')
    duration_ms = models.PositiveIntegerField('执行时长(ms)')
    
    class Meta:
        verbose_name = 'API测试结果'
        verbose_name_plural = 'API测试结果'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.test_case.name} - {self.get_status_display()}"
