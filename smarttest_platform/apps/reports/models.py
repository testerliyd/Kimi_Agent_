"""
报告管理模块
包含测试报告、报告模板等模型
"""
from django.db import models
from django.conf import settings

from apps.core.models import BaseModel

# User model reference: settings.AUTH_USER_MODEL


class ReportTemplate(BaseModel):
    """
    报告模板模型
    """
    TEMPLATE_TYPE_CHOICES = [
        ('test_summary', '测试总结报告'),
        ('api_test', 'API测试报告'),
        ('perf_test', '性能测试报告'),
        ('bug_analysis', 'Bug分析报告'),
        ('custom', '自定义报告'),
    ]
    
    name = models.CharField('模板名称', max_length=200)
    template_type = models.CharField(
        '模板类型',
        max_length=50,
        choices=TEMPLATE_TYPE_CHOICES,
        default='custom'
    )
    description = models.TextField('模板描述', blank=True)
    
    # 模板内容
    content_template = models.TextField('内容模板', help_text='支持Jinja2模板语法')
    style_css = models.TextField('样式CSS', blank=True)
    
    # 默认配置
    is_default = models.BooleanField('默认模板', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    
    class Meta:
        verbose_name = '报告模板'
        verbose_name_plural = '报告模板'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Report(BaseModel):
    """
    报告模型
    """
    REPORT_TYPE_CHOICES = [
        ('test_summary', '测试总结报告'),
        ('api_test', 'API测试报告'),
        ('perf_test', '性能测试报告'),
        ('bug_analysis', 'Bug分析报告'),
        ('custom', '自定义报告'),
    ]
    
    STATUS_CHOICES = [
        ('generating', '生成中'),
        ('completed', '已完成'),
        ('failed', '生成失败'),
    ]
    
    FORMAT_CHOICES = [
        ('html', 'HTML'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
    ]
    
    name = models.CharField('报告名称', max_length=200)
    report_type = models.CharField(
        '报告类型',
        max_length=50,
        choices=REPORT_TYPE_CHOICES,
        default='custom'
    )
    description = models.TextField('报告描述', blank=True)
    
    # 关联信息
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True
    )
    template = models.ForeignKey(
        ReportTemplate,
        verbose_name='使用模板',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # 报告数据
    report_data = models.JSONField('报告数据', default=dict, blank=True)
    
    # 文件
    file_path = models.FileField('报告文件', upload_to='reports/%Y/%m/', blank=True)
    file_size = models.PositiveIntegerField('文件大小(字节)', null=True, blank=True)
    
    # 格式
    format = models.CharField('报告格式', max_length=20, choices=FORMAT_CHOICES, default='html')
    
    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='generating')
    error_message = models.TextField('错误信息', blank=True)
    
    # 统计
    view_count = models.PositiveIntegerField('查看次数', default=0)
    download_count = models.PositiveIntegerField('下载次数', default=0)
    
    class Meta:
        verbose_name = '报告'
        verbose_name_plural = '报告'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def increment_view_count(self):
        """
        增加查看次数
        """
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def increment_download_count(self):
        """
        增加下载次数
        """
        self.download_count += 1
        self.save(update_fields=['download_count'])
