"""
用户管理器模块
自定义用户管理器
"""
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    自定义用户管理器
    """
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        创建用户的内部方法
        """
        if not username:
            raise ValueError('用户名不能为空')
        if not email:
            raise ValueError('邮箱不能为空')
        
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        """
        创建普通用户
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        创建超级管理员
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        extra_fields.setdefault('status', 'active')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级管理员必须设置is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级管理员必须设置is_superuser=True')

        return self._create_user(username, email, password, **extra_fields)

    def get_active_users(self):
        """
        获取所有活跃用户
        """
        return self.filter(is_active=True, status='active')

    def get_online_users(self):
        """
        获取在线用户（5分钟内有活动）
        """
        from django.utils import timezone
        from datetime import timedelta
        
        return self.filter(
            is_active=True,
            last_activity_at__gte=timezone.now() - timedelta(minutes=5)
        )

    def get_by_feishu_id(self, feishu_user_id):
        """
        通过飞书用户ID获取用户
        """
        try:
            return self.get(feishu_user_id=feishu_user_id, is_active=True)
        except self.model.DoesNotExist:
            return None

    def search_users(self, keyword):
        """
        搜索用户
        """
        return self.filter(
            models.Q(username__icontains=keyword) |
            models.Q(email__icontains=keyword) |
            models.Q(nickname__icontains=keyword) |
            models.Q(phone__icontains=keyword)
        )
