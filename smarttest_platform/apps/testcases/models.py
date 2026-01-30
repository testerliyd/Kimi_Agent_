"""
用例管理模块
包含测试用例、测试套件、测试计划等模型
"""
from django.db import models
from django.conf import settings

from apps.core.models import BaseModel, BaseStatusModel

# User model reference: settings.AUTH_USER_MODEL


class TestCase(BaseStatusModel):
    """
    测试用例模型
    """
    PRIORITY_CHOICES = [
        ('p0', 'P0-最高'),
        ('p1', 'P1-高'),
        ('p2', 'P2-中'),
        ('p3', 'P3-低'),
    ]
    
    CASE_TYPE_CHOICES = [
        ('functional', '功能测试'),
        ('performance', '性能测试'),
        ('security', '安全测试'),
        ('compatibility', '兼容性测试'),
        ('usability', '易用性测试'),
        ('api', '接口测试'),
        ('ui', 'UI测试'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending', '待执行'),
        ('running', '执行中'),
        ('passed', '已通过'),
        ('failed', '已失败'),
        ('blocked', '已阻塞'),
        ('skipped', '已跳过'),
    ]
    
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='test_cases'
    )
    version = models.ForeignKey(
        'projects.ProjectVersion',
        verbose_name='关联版本',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='test_cases'
    )
    
    # 用例基本信息
    case_no = models.CharField('用例编号', max_length=100, db_index=True)
    name = models.CharField('用例名称', max_length=500)
    description = models.TextField('用例描述', blank=True)
    case_type = models.CharField(
        '用例类型',
        max_length=20,
        choices=CASE_TYPE_CHOICES,
        default='functional'
    )
    priority = models.CharField(
        '优先级',
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='p2'
    )
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # 用例内容
    preconditions = models.TextField('前置条件', blank=True)
    steps = models.JSONField('测试步骤', default=list, help_text='JSON格式测试步骤')
    expected_result = models.TextField('预期结果')
    actual_result = models.TextField('实际结果', blank=True)
    
    # 关联信息
    module = models.CharField('所属模块', max_length=200, blank=True)
    tags = models.JSONField('标签', default=list, blank=True)
    
    # 执行信息
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='执行人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executed_cases'
    )
    last_executed_at = models.DateTimeField('最后执行时间', null=True, blank=True)
    execution_count = models.PositiveIntegerField('执行次数', default=0)
    pass_count = models.PositiveIntegerField('通过次数', default=0)
    fail_count = models.PositiveIntegerField('失败次数', default=0)
    
    # 关联需求/Bug
    related_requirements = models.JSONField('关联需求', default=list, blank=True)
    related_bugs = models.JSONField('关联Bug', default=list, blank=True)
    
    class Meta:
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例'
        ordering = ['-created_at']
        unique_together = ['project', 'case_no']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['priority', 'status']),
        ]

    def __str__(self):
        return f"{self.case_no} - {self.name}"

    def execute(self, result, executor=None, actual_result=''):
        """
        执行用例并记录结果
        """
        from django.utils import timezone
        
        self.execution_count += 1
        self.last_executed_at = timezone.now()
        
        if result == 'passed':
            self.pass_count += 1
            self.status = 'passed'
        elif result == 'failed':
            self.fail_count += 1
            self.status = 'failed'
        elif result == 'blocked':
            self.status = 'blocked'
        elif result == 'skipped':
            self.status = 'skipped'
        
        if executor:
            self.executor = executor
        if actual_result:
            self.actual_result = actual_result
        
        self.save()


class TestSuite(BaseModel):
    """
    测试套件模型
    用于组织多个测试用例
    """
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='test_suites'
    )
    name = models.CharField('套件名称', max_length=200)
    description = models.TextField('套件描述', blank=True)
    test_cases = models.ManyToManyField(
        TestCase,
        verbose_name='包含用例',
        related_name='suites',
        blank=True
    )
    
    class Meta:
        verbose_name = '测试套件'
        verbose_name_plural = '测试套件'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_case_count(self):
        return self.test_cases.filter(is_deleted=False).count()


class TestPlan(BaseModel):
    """
    测试计划模型
    """
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending', '待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='test_plans'
    )
    version = models.ForeignKey(
        'projects.ProjectVersion',
        verbose_name='关联版本',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='test_plans'
    )
    
    name = models.CharField('计划名称', max_length=200)
    description = models.TextField('计划描述', blank=True)
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # 时间规划
    planned_start_date = models.DateTimeField('计划开始时间', null=True, blank=True)
    planned_end_date = models.DateTimeField('计划结束时间', null=True, blank=True)
    actual_start_date = models.DateTimeField('实际开始时间', null=True, blank=True)
    actual_end_date = models.DateTimeField('实际结束时间', null=True, blank=True)
    
    # 负责人
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='负责人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_plans'
    )
    
    # 关联套件
    test_suites = models.ManyToManyField(
        TestSuite,
        verbose_name='包含套件',
        related_name='plans',
        blank=True
    )
    
    # 统计
    total_cases = models.PositiveIntegerField('总用例数', default=0)
    passed_cases = models.PositiveIntegerField('通过数', default=0)
    failed_cases = models.PositiveIntegerField('失败数', default=0)
    blocked_cases = models.PositiveIntegerField('阻塞数', default=0)
    
    class Meta:
        verbose_name = '测试计划'
        verbose_name_plural = '测试计划'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def update_statistics(self):
        """
        更新计划统计信息
        """
        cases = TestCase.objects.filter(suites__in=self.test_suites.all())
        self.total_cases = cases.count()
        self.passed_cases = cases.filter(status='passed').count()
        self.failed_cases = cases.filter(status='failed').count()
        self.blocked_cases = cases.filter(status='blocked').count()
        self.save()


class TestCaseTag(BaseModel):
    """
    测试用例标签模型
    """
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='test_case_tags'
    )
    name = models.CharField('标签名称', max_length=50)
    color = models.CharField('标签颜色', max_length=20, default='#1890ff')
    description = models.TextField('标签描述', blank=True)
    
    class Meta:
        verbose_name = '测试用例标签'
        verbose_name_plural = '测试用例标签'
        ordering = ['-created_at']
        unique_together = ['project', 'name']
    
    def __str__(self):
        return self.name


class TestCaseCategory(BaseModel):
    """
    测试用例分类模型
    """
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='test_case_categories'
    )
    parent = models.ForeignKey(
        'self',
        verbose_name='父分类',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    name = models.CharField('分类名称', max_length=100)
    description = models.TextField('分类描述', blank=True)
    sort_order = models.PositiveIntegerField('排序', default=0)
    
    class Meta:
        verbose_name = '测试用例分类'
        verbose_name_plural = '测试用例分类'
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return self.name
