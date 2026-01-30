"""
用户管理模块
包含用户模型、角色权限、用户组等
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    自定义用户模型
    扩展Django默认用户模型，添加更多字段
    """
    # 用户类型
    USER_TYPE_CHOICES = [
        ('admin', '管理员'),
        ('tester', '测试工程师'),
        ('developer', '开发工程师'),
        ('pm', '产品经理'),
        ('viewer', '访客'),
    ]
    
    # 用户状态
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('inactive', '未激活'),
        ('suspended', '已停用'),
    ]
    
    username = models.CharField(
        _('用户名'),
        max_length=150,
        unique=True,
        help_text=_('必填。150个字符以内。只能包含字母、数字和@/./+/-/_')
    )
    email = models.EmailField(
        _('邮箱'),
        unique=True,
        validators=[EmailValidator()],
        help_text=_('用于登录和接收通知')
    )
    phone = models.CharField(
        _('手机号'),
        max_length=20,
        blank=True,
        help_text=_('用于接收短信通知')
    )
    
    # 个人信息
    nickname = models.CharField(_('昵称'), max_length=50, blank=True)
    avatar = models.ImageField(
        _('头像'),
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True
    )
    department = models.CharField(_('部门'), max_length=100, blank=True)
    position = models.CharField(_('职位'), max_length=100, blank=True)
    
    # 用户类型和状态
    user_type = models.CharField(
        _('用户类型'),
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='tester'
    )
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # 权限相关
    is_staff = models.BooleanField(
        _('管理员状态'),
        default=False,
        help_text=_('决定用户是否可以登录管理后台')
    )
    is_active = models.BooleanField(
        _('激活状态'),
        default=True,
        help_text=_('决定用户是否可以登录系统')
    )
    
    # 时间相关
    date_joined = models.DateTimeField(_('注册时间'), default=timezone.now)
    last_login_ip = models.GenericIPAddressField(
        _('最后登录IP'),
        null=True,
        blank=True
    )
    last_activity_at = models.DateTimeField(
        _('最后活动时间'),
        null=True,
        blank=True
    )
    
    # 飞书集成
    feishu_user_id = models.CharField(
        _('飞书用户ID'),
        max_length=100,
        blank=True,
        db_index=True
    )
    feishu_open_id = models.CharField(
        _('飞书OpenID'),
        max_length=100,
        blank=True
    )
    
    # 偏好设置
    preferences = models.JSONField(
        _('偏好设置'),
        default=dict,
        blank=True,
        help_text=_('用户个性化设置，如主题、语言、通知偏好等')
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username', 'is_active']),
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['user_type', 'status']),
        ]

    def __str__(self):
        return f"{self.username} ({self.nickname or self.email})"

    def get_full_name(self):
        """
        返回用户全名
        """
        return self.nickname or self.username

    def get_short_name(self):
        """
        返回用户简称
        """
        return self.nickname or self.username

    def update_last_activity(self, ip=None):
        """
        更新最后活动时间
        """
        self.last_activity_at = timezone.now()
        if ip:
            self.last_login_ip = ip
        self.save(update_fields=['last_activity_at', 'last_login_ip'])

    def is_online(self):
        """
        判断用户是否在线（5分钟内有活动）
        """
        if not self.last_activity_at:
            return False
        return (timezone.now() - self.last_activity_at).seconds < 300

    def get_preferences(self, key=None, default=None):
        """
        获取用户偏好设置
        """
        if key:
            return self.preferences.get(key, default)
        return self.preferences

    def set_preferences(self, key, value):
        """
        设置用户偏好设置
        """
        self.preferences[key] = value
        self.save(update_fields=['preferences'])

    def has_project_permission(self, project, permission):
        """
        检查用户是否有指定项目的权限
        """
        # 超级管理员拥有所有权限
        if self.is_superuser:
            return True
        
        # 检查项目成员权限
        try:
            member = ProjectMember.objects.get(project=project, user=self)
            return member.has_permission(permission)
        except ProjectMember.DoesNotExist:
            return False


class Role(models.Model):
    """
    角色模型
    用于定义用户角色和权限
    """
    ROLE_TYPE_CHOICES = [
        ('system', '系统角色'),
        ('custom', '自定义角色'),
    ]
    
    name = models.CharField(_('角色名称'), max_length=100, unique=True)
    code = models.CharField(_('角色编码'), max_length=100, unique=True)
    description = models.TextField(_('角色描述'), blank=True)
    role_type = models.CharField(
        _('角色类型'),
        max_length=20,
        choices=ROLE_TYPE_CHOICES,
        default='custom'
    )
    permissions = models.JSONField(
        _('权限列表'),
        default=list,
        help_text=_('角色拥有的权限代码列表')
    )
    is_default = models.BooleanField(_('默认角色'), default=False)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('角色')
        verbose_name_plural = _('角色')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def has_permission(self, permission_code):
        """
        检查角色是否有指定权限
        """
        return permission_code in self.permissions


class UserRole(models.Model):
    """
    用户角色关联模型
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('用户'),
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        verbose_name=_('角色'),
        on_delete=models.CASCADE,
        related_name='role_users'
    )
    project = models.ForeignKey(
        'projects.Project',
        verbose_name=_('项目'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='project_user_roles'
    )
    assigned_at = models.DateTimeField(_('分配时间'), auto_now_add=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('分配人'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles'
    )
    
    class Meta:
        verbose_name = _('用户角色')
        verbose_name_plural = _('用户角色')
        unique_together = ['user', 'role', 'project']
        ordering = ['-assigned_at']

    def __str__(self):
        project_info = f" - {self.project.name}" if self.project else ""
        return f"{self.user.username} - {self.role.name}{project_info}"


class Permission(models.Model):
    """
    权限模型
    定义系统中的所有权限
    """
    PERMISSION_CATEGORIES = [
        ('user', '用户管理'),
        ('project', '项目管理'),
        ('testcase', '用例管理'),
        ('bug', 'Bug管理'),
        ('apitest', '接口测试'),
        ('perftest', '性能测试'),
        ('report', '报告管理'),
        ('system', '系统设置'),
    ]
    
    name = models.CharField(_('权限名称'), max_length=100)
    code = models.CharField(_('权限编码'), max_length=100, unique=True)
    category = models.CharField(
        _('权限分类'),
        max_length=20,
        choices=PERMISSION_CATEGORIES
    )
    description = models.TextField(_('权限描述'), blank=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('权限')
        verbose_name_plural = _('权限')
        ordering = ['category', 'code']

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"


class UserLoginLog(models.Model):
    """
    用户登录日志
    记录用户的登录历史
    """
    LOGIN_TYPE_CHOICES = [
        ('password', '密码登录'),
        ('sso', '单点登录'),
        ('feishu', '飞书登录'),
        ('ldap', 'LDAP登录'),
    ]
    
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
        ('locked', '账户锁定'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('用户'),
        on_delete=models.CASCADE,
        related_name='login_logs'
    )
    login_type = models.CharField(
        _('登录方式'),
        max_length=20,
        choices=LOGIN_TYPE_CHOICES,
        default='password'
    )
    ip_address = models.GenericIPAddressField(_('IP地址'))
    user_agent = models.TextField(_('用户代理'), blank=True)
    status = models.CharField(
        _('登录状态'),
        max_length=20,
        choices=STATUS_CHOICES
    )
    fail_reason = models.CharField(_('失败原因'), max_length=255, blank=True)
    created_at = models.DateTimeField(_('登录时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('登录日志')
        verbose_name_plural = _('登录日志')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()} - {self.created_at}"


# 导入ProjectMember避免循环引用
from apps.projects.models import ProjectMember
