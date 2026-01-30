"""
项目管理模块
包含项目、项目成员、项目版本等模型
"""
from django.db import models
from django.conf import settings
from django.utils import timezone

from apps.core.models import BaseModel, BaseStatusModel

# User model reference: settings.AUTH_USER_MODEL


class Project(BaseStatusModel):
    """
    项目模型
    管理测试项目的基本信息
    """
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '进行中'),
        ('paused', '已暂停'),
        ('completed', '已完成'),
        ('archived', '已归档'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急'),
    ]
    
    PROJECT_TYPE_CHOICES = [
        ('web', 'Web应用'),
        ('mobile', '移动应用'),
        ('desktop', '桌面应用'),
        ('api', 'API服务'),
        ('embedded', '嵌入式系统'),
        ('other', '其他'),
    ]
    
    name = models.CharField('项目名称', max_length=200)
    code = models.CharField('项目编码', max_length=100, unique=True, db_index=True)
    description = models.TextField('项目描述', blank=True)
    project_type = models.CharField(
        '项目类型',
        max_length=20,
        choices=PROJECT_TYPE_CHOICES,
        default='web'
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
        default='draft'
    )
    
    # 时间规划
    start_date = models.DateField('开始日期', null=True, blank=True)
    end_date = models.DateField('结束日期', null=True, blank=True)
    
    # 负责人
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='项目负责人',
        on_delete=models.SET_NULL,
        null=True,
        related_name='owned_projects'
    )
    
    # 项目配置
    config = models.JSONField(
        '项目配置',
        default=dict,
        blank=True,
        help_text='项目级别的配置，如测试环境、通知设置等'
    )
    
    # 关联信息
    jira_project_key = models.CharField('JIRA项目Key', max_length=50, blank=True)
    git_repository = models.URLField('Git仓库地址', blank=True)
    
    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['owner', 'status']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_members(self):
        """
        获取项目所有成员
        """
        return User.objects.filter(
            project_members__project=self,
            project_members__is_active=True
        )

    def get_member_count(self):
        """
        获取项目成员数量
        """
        return self.project_members.filter(is_active=True).count()

    def add_member(self, user, role='member', added_by=None):
        """
        添加项目成员
        """
        member, created = ProjectMember.objects.get_or_create(
            project=self,
            user=user,
            defaults={
                'role': role,
                'added_by': added_by
            }
        )
        if not created:
            member.role = role
            member.is_active = True
            member.save()
        return member

    def remove_member(self, user):
        """
        移除项目成员
        """
        ProjectMember.objects.filter(project=self, user=user).update(is_active=False)

    def get_test_case_count(self):
        """
        获取项目测试用例数量
        """
        return self.test_cases.filter(is_deleted=False).count()

    def get_bug_count(self, status=None):
        """
        获取项目Bug数量
        """
        queryset = self.bugs.filter(is_deleted=False)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.count()


class ProjectMember(models.Model):
    """
    项目成员模型
    管理项目与用户的关联关系
    """
    ROLE_CHOICES = [
        ('owner', '所有者'),
        ('manager', '管理员'),
        ('tester', '测试工程师'),
        ('developer', '开发工程师'),
        ('viewer', '访客'),
    ]
    
    project = models.ForeignKey(
        Project,
        verbose_name='项目',
        on_delete=models.CASCADE,
        related_name='project_members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='用户',
        on_delete=models.CASCADE,
        related_name='project_members'
    )
    role = models.CharField(
        '角色',
        max_length=20,
        choices=ROLE_CHOICES,
        default='tester'
    )
    permissions = models.JSONField(
        '权限列表',
        default=list,
        blank=True,
        help_text='成员在项目中的具体权限'
    )
    is_active = models.BooleanField('是否有效', default=True)
    joined_at = models.DateTimeField('加入时间', auto_now_add=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='添加人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_members'
    )
    
    class Meta:
        verbose_name = '项目成员'
        verbose_name_plural = '项目成员'
        unique_together = ['project', 'user']
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.project.name} - {self.user.username} ({self.get_role_display()})"

    def has_permission(self, permission_code):
        """
        检查成员是否有指定权限
        """
        # 所有者拥有所有权限
        if self.role == 'owner':
            return True
        
        # 检查具体权限
        return permission_code in self.permissions


class ProjectVersion(BaseModel):
    """
    项目版本模型
    管理项目的版本信息
    """
    STATUS_CHOICES = [
        ('planning', '规划中'),
        ('developing', '开发中'),
        ('testing', '测试中'),
        ('released', '已发布'),
        ('archived', '已归档'),
    ]
    
    project = models.ForeignKey(
        Project,
        verbose_name='项目',
        on_delete=models.CASCADE,
        related_name='versions'
    )
    version = models.CharField('版本号', max_length=50)
    name = models.CharField('版本名称', max_length=200, blank=True)
    description = models.TextField('版本描述', blank=True)
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning'
    )
    
    # 时间规划
    planned_start_date = models.DateField('计划开始日期', null=True, blank=True)
    planned_end_date = models.DateField('计划结束日期', null=True, blank=True)
    actual_start_date = models.DateField('实际开始日期', null=True, blank=True)
    actual_end_date = models.DateField('实际结束日期', null=True, blank=True)
    
    # 版本负责人
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='版本负责人',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_versions'
    )
    
    # 版本范围
    scope = models.TextField('版本范围', blank=True, help_text='该版本包含的功能范围')
    
    class Meta:
        verbose_name = '项目版本'
        verbose_name_plural = '项目版本'
        ordering = ['-created_at']
        unique_together = ['project', 'version']

    def __str__(self):
        return f"{self.project.name} - v{self.version}"

    def get_test_case_count(self):
        """
        获取版本关联的测试用例数量
        """
        return self.test_cases.filter(is_deleted=False).count()

    def get_bug_count(self):
        """
        获取版本关联的Bug数量
        """
        return self.bugs.filter(is_deleted=False).count()


class ProjectMilestone(BaseModel):
    """
    项目里程碑模型
    管理项目的重要节点
    """
    STATUS_CHOICES = [
        ('pending', '待开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('delayed', '已延期'),
    ]
    
    project = models.ForeignKey(
        Project,
        verbose_name='项目',
        on_delete=models.CASCADE,
        related_name='milestones'
    )
    name = models.CharField('里程碑名称', max_length=200)
    description = models.TextField('里程碑描述', blank=True)
    status = models.CharField(
        '状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # 时间
    planned_date = models.DateField('计划日期', null=True, blank=True)
    actual_date = models.DateField('实际日期', null=True, blank=True)
    
    # 关联版本
    version = models.ForeignKey(
        ProjectVersion,
        verbose_name='关联版本',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='milestones'
    )
    
    class Meta:
        verbose_name = '项目里程碑'
        verbose_name_plural = '项目里程碑'
        ordering = ['planned_date', 'created_at']

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class ProjectEnvironment(BaseModel):
    """
    项目环境配置模型
    管理项目的测试环境信息
    """
    ENV_TYPE_CHOICES = [
        ('dev', '开发环境'),
        ('test', '测试环境'),
        ('staging', '预发布环境'),
        ('prod', '生产环境'),
    ]
    
    project = models.ForeignKey(
        Project,
        verbose_name='项目',
        on_delete=models.CASCADE,
        related_name='environments'
    )
    name = models.CharField('环境名称', max_length=100)
    env_type = models.CharField(
        '环境类型',
        max_length=20,
        choices=ENV_TYPE_CHOICES,
        default='test'
    )
    base_url = models.URLField('基础URL')
    description = models.TextField('环境描述', blank=True)
    
    # 环境变量
    variables = models.JSONField(
        '环境变量',
        default=dict,
        blank=True,
        help_text='环境特定的变量，如数据库连接、API密钥等'
    )
    
    # 状态
    is_active = models.BooleanField('是否启用', default=True)
    
    class Meta:
        verbose_name = '项目环境'
        verbose_name_plural = '项目环境'
        ordering = ['env_type', 'name']
        unique_together = ['project', 'name']

    def __str__(self):
        return f"{self.project.name} - {self.name} ({self.get_env_type_display()})"
