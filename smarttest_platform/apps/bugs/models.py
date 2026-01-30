"""
Bug管理模块
包含Bug、Bug评论、Bug历史等模型
"""
from django.db import models
from django.conf import settings

from apps.core.models import BaseModel, BaseStatusModel

# User model reference: settings.AUTH_USER_MODEL


class Bug(BaseStatusModel):
    """
    Bug模型
    """
    SEVERITY_CHOICES = [
        ('critical', '致命'),
        ('major', '严重'),
        ('minor', '一般'),
        ('trivial', '轻微'),
    ]
    
    PRIORITY_CHOICES = [
        ('urgent', '紧急'),
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    ]
    
    STATUS_CHOICES = [
        ('new', '新建'),
        ('confirmed', '已确认'),
        ('in_progress', '处理中'),
        ('resolved', '已解决'),
        ('rejected', '已拒绝'),
        ('closed', '已关闭'),
        ('reopened', '重新打开'),
    ]
    
    BUG_TYPE_CHOICES = [
        ('functional', '功能缺陷'),
        ('ui', '界面问题'),
        ('performance', '性能问题'),
        ('compatibility', '兼容性问题'),
        ('security', '安全问题'),
        ('data', '数据问题'),
        ('other', '其他'),
    ]
    
    # 基本信息
    bug_no = models.CharField('Bug编号', max_length=100, unique=True, db_index=True)
    title = models.CharField('标题', max_length=500)
    description = models.TextField('详细描述')
    bug_type = models.CharField(
        'Bug类型',
        max_length=20,
        choices=BUG_TYPE_CHOICES,
        default='functional'
    )
    severity = models.CharField(
        '严重程度',
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='minor'
    )
    priority = models.CharField(
        '优先级',
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    
    # 关联信息
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='bugs'
    )
    version = models.ForeignKey(
        'projects.ProjectVersion',
        verbose_name='发现版本',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bugs'
    )
    module = models.CharField('所属模块', max_length=200, blank=True)
    
    # 人员
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='报告人',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_bugs'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='处理人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_bugs'
    )
    
    # 环境信息
    environment = models.CharField('发现环境', max_length=500, blank=True)
    browser = models.CharField('浏览器', max_length=200, blank=True)
    
    # 复现信息
    steps_to_reproduce = models.TextField('复现步骤', blank=True)
    expected_result = models.TextField('预期结果', blank=True)
    actual_result = models.TextField('实际结果', blank=True)
    
    # 附件
    attachments = models.JSONField('附件', default=list, blank=True)
    
    # 关联用例
    related_test_case = models.ForeignKey(
        'testcases.TestCase',
        verbose_name='关联测试用例',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_bugs'
    )
    
    # 时间
    confirmed_at = models.DateTimeField('确认时间', null=True, blank=True)
    resolved_at = models.DateTimeField('解决时间', null=True, blank=True)
    closed_at = models.DateTimeField('关闭时间', null=True, blank=True)
    
    # 解决方案
    resolution = models.TextField('解决方案', blank=True)
    resolved_version = models.ForeignKey(
        'projects.ProjectVersion',
        verbose_name='解决版本',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_bugs'
    )
    
    # 标签
    tags = models.JSONField('标签', default=list, blank=True)
    
    class Meta:
        verbose_name = 'Bug'
        verbose_name_plural = 'Bug'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['severity', 'priority']),
            models.Index(fields=['assignee', 'status']),
        ]

    def __str__(self):
        return f"{self.bug_no} - {self.title}"

    def assign_to(self, user, assigned_by=None):
        """
        分配Bug给指定用户
        """
        from django.utils import timezone
        self.assignee = user
        if self.status == 'new':
            self.status = 'confirmed'
            self.confirmed_at = timezone.now()
        self.save()
        
        # 记录历史
        BugHistory.objects.create(
            bug=self,
            action='assign',
            old_value='',
            new_value=user.username if user else '',
            operator=assigned_by
        )

    def resolve(self, resolution, resolved_by=None):
        """
        解决Bug
        """
        from django.utils import timezone
        self.status = 'resolved'
        self.resolution = resolution
        self.resolved_at = timezone.now()
        self.save()
        
        # 记录历史
        BugHistory.objects.create(
            bug=self,
            action='resolve',
            old_value='',
            new_value=resolution,
            operator=resolved_by
        )

    def close(self, closed_by=None):
        """
        关闭Bug
        """
        from django.utils import timezone
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.save()
        
        # 记录历史
        BugHistory.objects.create(
            bug=self,
            action='close',
            old_value='',
            new_value='closed',
            operator=closed_by
        )

    def reopen(self, reason, reopened_by=None):
        """
        重新打开Bug
        """
        self.status = 'reopened'
        self.save()
        
        # 记录历史
        BugHistory.objects.create(
            bug=self,
            action='reopen',
            old_value='',
            new_value=reason,
            operator=reopened_by
        )


class BugComment(BaseModel):
    """
    Bug评论模型
    """
    bug = models.ForeignKey(
        Bug,
        verbose_name='Bug',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField('评论内容')
    is_internal = models.BooleanField('内部评论', default=False, help_text='仅内部人员可见')
    
    class Meta:
        verbose_name = 'Bug评论'
        verbose_name_plural = 'Bug评论'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.bug.bug_no} - {self.content[:50]}"


class BugHistory(BaseModel):
    """
    Bug历史记录模型
    """
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('assign', '分配'),
        ('resolve', '解决'),
        ('close', '关闭'),
        ('reopen', '重新打开'),
        ('comment', '评论'),
    ]
    
    bug = models.ForeignKey(
        Bug,
        verbose_name='Bug',
        on_delete=models.CASCADE,
        related_name='history'
    )
    action = models.CharField('操作', max_length=20, choices=ACTION_CHOICES)
    field = models.CharField('字段', max_length=100, blank=True)
    old_value = models.TextField('旧值', blank=True)
    new_value = models.TextField('新值', blank=True)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='操作人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Bug历史'
        verbose_name_plural = 'Bug历史'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bug.bug_no} - {self.get_action_display()}"


class BugTag(BaseModel):
    """
    Bug标签模型
    """
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='bug_tags'
    )
    name = models.CharField('标签名称', max_length=50)
    color = models.CharField('标签颜色', max_length=20, default='#ff4d4f')
    description = models.TextField('标签描述', blank=True)
    
    class Meta:
        verbose_name = 'Bug标签'
        verbose_name_plural = 'Bug标签'
        ordering = ['-created_at']
        unique_together = ['project', 'name']
    
    def __str__(self):
        return self.name


class BugCategory(BaseModel):
    """
    Bug分类模型
    """
    project = models.ForeignKey(
        'projects.Project',
        verbose_name='所属项目',
        on_delete=models.CASCADE,
        related_name='bug_categories'
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
        verbose_name = 'Bug分类'
        verbose_name_plural = 'Bug分类'
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return self.name
