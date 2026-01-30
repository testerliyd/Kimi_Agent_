"""
用户管理序列化器模块
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Role, UserRole, Permission, UserLoginLog

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    用于用户信息的序列化和反序列化
    """
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_online = serializers.BooleanField(read_only=True)
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'nickname', 'avatar',
            'department', 'position', 'user_type', 'user_type_display',
            'status', 'status_display', 'is_staff', 'is_active',
            'date_joined', 'last_login', 'last_activity_at', 'is_online',
            'feishu_user_id', 'preferences', 'roles'
        ]
        read_only_fields = ['date_joined', 'last_login', 'last_activity_at']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_roles(self, obj):
        """
        获取用户角色列表
        """
        roles = []
        for user_role in obj.user_roles.select_related('role').all():
            roles.append({
                'id': user_role.role.id,
                'name': user_role.role.name,
                'code': user_role.role.code,
                'project': user_role.project.name if user_role.project else None,
            })
        return roles

    def get_is_online(self, obj):
        """
        判断用户是否在线
        """
        return obj.is_online()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    用户创建序列化器
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone', 'password', 'password_confirm',
            'nickname', 'department', 'position', 'user_type'
        ]

    def validate(self, attrs):
        """
        验证密码是否一致
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '两次输入的密码不一致'})
        return attrs

    def create(self, validated_data):
        """
        创建用户
        """
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户更新序列化器
    """
    class Meta:
        model = User
        fields = [
            'email', 'phone', 'nickname', 'avatar',
            'department', 'position', 'user_type', 'status',
            'preferences'
        ]


class UserPasswordChangeSerializer(serializers.Serializer):
    """
    密码修改序列化器
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """
        验证新密码
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': '两次输入的新密码不一致'})
        
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        
        return attrs

    def validate_old_password(self, value):
        """
        验证旧密码
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('旧密码不正确')
        return value


class UserPasswordResetSerializer(serializers.Serializer):
    """
    密码重置序列化器
    """
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """
        验证新密码
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': '两次输入的新密码不一致'})
        
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户个人资料序列化器
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'nickname', 'avatar',
            'department', 'position', 'user_type', 'date_joined',
            'preferences'
        ]
        read_only_fields = ['id', 'username', 'email', 'date_joined', 'user_type']


class RoleSerializer(serializers.ModelSerializer):
    """
    角色序列化器
    """
    role_type_display = serializers.CharField(source='get_role_type_display', read_only=True)
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'code', 'description', 'role_type',
            'role_type_display', 'permissions', 'is_default',
            'user_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_user_count(self, obj):
        """
        获取拥有该角色的用户数量
        """
        return obj.role_users.count()


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    """
    角色创建/更新序列化器
    """
    class Meta:
        model = Role
        fields = ['name', 'code', 'description', 'role_type', 'permissions', 'is_default']
        extra_kwargs = {
            'code': {'required': True},
            'name': {'required': True},
        }

    def validate_code(self, value):
        """
        验证角色编码
        """
        if not value.replace('_', '').isalnum():
            raise serializers.ValidationError('角色编码只能包含字母、数字和下划线')
        return value.upper()


class UserRoleSerializer(serializers.ModelSerializer):
    """
    用户角色关联序列化器
    """
    user_name = serializers.CharField(source='user.username', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_name', 'role', 'role_name',
            'project', 'project_name', 'assigned_at', 'assigned_by', 'assigned_by_name'
        ]
        read_only_fields = ['assigned_at']


class PermissionSerializer(serializers.ModelSerializer):
    """
    权限序列化器
    """
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'category', 'category_display', 'description', 'created_at']


class UserLoginLogSerializer(serializers.ModelSerializer):
    """
    用户登录日志序列化器
    """
    user_name = serializers.CharField(source='user.username', read_only=True)
    login_type_display = serializers.CharField(source='get_login_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = UserLoginLog
        fields = [
            'id', 'user', 'user_name', 'login_type', 'login_type_display',
            'ip_address', 'status', 'status_display', 'fail_reason', 'created_at'
        ]
        read_only_fields = ['created_at']


class UserListSerializer(serializers.ModelSerializer):
    """
    用户列表序列化器（简化版）
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'email', 'user_type', 'status', 'is_active']


class UserImportSerializer(serializers.Serializer):
    """
    用户导入序列化器
    """
    file = serializers.FileField(required=True, help_text='Excel文件')
    
    def validate_file(self, value):
        """
        验证文件类型
        """
        if not value.name.endswith(('.xlsx', '.xls', '.csv')):
            raise serializers.ValidationError('只支持Excel或CSV文件')
        return value


class UserExportSerializer(serializers.Serializer):
    """
    用户导出序列化器
    """
    format = serializers.ChoiceField(
        choices=['xlsx', 'csv', 'json'],
        default='xlsx'
    )
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='指定导出的用户ID列表，为空则导出所有'
    )
