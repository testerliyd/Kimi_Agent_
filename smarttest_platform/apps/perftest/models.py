"""
性能测试模块
包含性能测试任务、测试结果等模型
"""
from django.db import models
from django.conf import settings

from apps.core.models import BaseModel

# User model reference: settings.AUTH_USER_MODEL


class PerfTestScenario(BaseModel):
    """
    性能测试场景模型
    """
    SCENARIO_TYPE_CHOICES = [
        ('load', '负载测试'),
        ('stress', '压力测试'),
        ('spike', '尖峰测试'),
        ('endurance', '耐力测试'),
        ('scalability', '可扩展性测试'),
    ]
    
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='perf_test_scenarios'
    )
    name = models.CharField('场景名称', max_length=200)
    description = models.TextField('场景描述', blank=True)
    scenario_type = models.CharField(
        '场景类型',
        max_length=20,
        choices=SCENARIO_TYPE_CHOICES,
        default='load'
    )
    
    # 测试配置
    target_url = models.URLField('目标URL')
    http_method = models.CharField('HTTP方法', max_length=10, default='GET')
    headers = models.JSONField('请求头', default=dict, blank=True)
    body = models.TextField('请求体', blank=True)
    
    # 负载配置
    concurrent_users = models.PositiveIntegerField('并发用户数', default=10)
    ramp_up_time = models.PositiveIntegerField('启动时间(秒)', default=60)
    test_duration = models.PositiveIntegerField('测试时长(秒)', default=300)
    
    # 断言配置
    success_criteria = models.JSONField('成功标准', default=dict, blank=True, help_text='如: {"avg_response_time": 1000, "error_rate": 0.01}')
    
    # 状态
    is_active = models.BooleanField('是否启用', default=True)
    
    class Meta:
        verbose_name = '性能测试场景'
        verbose_name_plural = '性能测试场景'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PerfTestJob(BaseModel):
    """
    性能测试任务模型
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
        ('ci', 'CI集成'),
    ]
    
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='perf_test_jobs'
    )
    scenario = models.ForeignKey(
        PerfTestScenario,
        verbose_name='测试场景',
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    
    name = models.CharField('任务名称', max_length=200)
    description = models.TextField('任务描述', blank=True)
    
    # 执行信息
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    trigger_type = models.CharField('触发方式', max_length=20, choices=TRIGGER_TYPE_CHOICES, default='manual')
    
    # 执行参数（覆盖场景配置）
    concurrent_users = models.PositiveIntegerField('并发用户数', null=True, blank=True)
    test_duration = models.PositiveIntegerField('测试时长(秒)', null=True, blank=True)
    
    # 时间
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    
    # 结果摘要
    total_requests = models.PositiveIntegerField('总请求数', null=True, blank=True)
    avg_response_time = models.FloatField('平均响应时间(ms)', null=True, blank=True)
    min_response_time = models.FloatField('最小响应时间(ms)', null=True, blank=True)
    max_response_time = models.FloatField('最大响应时间(ms)', null=True, blank=True)
    error_rate = models.FloatField('错误率', null=True, blank=True)
    requests_per_second = models.FloatField('每秒请求数', null=True, blank=True)
    
    # 结果判断
    passed_criteria = models.BooleanField('是否通过标准', null=True, blank=True)
    
    # 报告
    report_data = models.JSONField('报告数据', default=dict, blank=True)
    report_file = models.FileField('报告文件', upload_to='perf_reports/%Y/%m/', blank=True)
    
    # 执行人
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='执行人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perf_test_jobs'
    )
    
    class Meta:
        verbose_name = '性能测试任务'
        verbose_name_plural = '性能测试任务'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PerfTestMetrics(BaseModel):
    """
    性能测试指标模型
    存储详细的性能指标数据
    """
    job = models.ForeignKey(
        PerfTestJob,
        verbose_name='测试任务',
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    
    # 时间戳
    timestamp = models.DateTimeField('时间戳')
    
    # 请求统计
    total_requests = models.PositiveIntegerField('总请求数')
    failed_requests = models.PositiveIntegerField('失败请求数')
    
    # 响应时间统计
    avg_response_time = models.FloatField('平均响应时间(ms)')
    min_response_time = models.FloatField('最小响应时间(ms)')
    max_response_time = models.FloatField('最大响应时间(ms)')
    p50_response_time = models.FloatField('P50响应时间(ms)')
    p95_response_time = models.FloatField('P95响应时间(ms)')
    p99_response_time = models.FloatField('P99响应时间(ms)')
    
    # 吞吐量
    requests_per_second = models.FloatField('每秒请求数')
    bytes_per_second = models.FloatField('每秒字节数')
    
    # 并发
    current_users = models.PositiveIntegerField('当前用户数')
    
    class Meta:
        verbose_name = '性能测试指标'
        verbose_name_plural = '性能测试指标'
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.job.name} - {self.timestamp}"
