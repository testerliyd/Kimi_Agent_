"""
核心应用序列化器模块
"""
from rest_framework import serializers
from .models import AuditLog, SystemConfig


class AuditLogSerializer(serializers.ModelSerializer):
    """
    审计日志序列化器
    """
    user_name = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'action_display',
            'resource_type', 'resource_id', 'resource_name',
            'old_data', 'new_data', 'ip_address', 'description',
            'created_at'
        ]
        read_only_fields = ['created_at']


class AuditLogCreateSerializer(serializers.ModelSerializer):
    """
    审计日志创建序列化器
    """
    class Meta:
        model = AuditLog
        fields = [
            'user', 'action', 'resource_type', 'resource_id',
            'resource_name', 'old_data', 'new_data',
            'ip_address', 'user_agent', 'description'
        ]


class SystemConfigSerializer(serializers.ModelSerializer):
    """
    系统配置序列化器
    """
    typed_value = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemConfig
        fields = [
            'id', 'key', 'value', 'config_type', 'typed_value',
            'description', 'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'key': {'required': True},
            'value': {'required': True},
        }

    def get_typed_value(self, obj):
        """
        获取正确类型的配置值
        """
        return obj.get_typed_value()

    def validate_key(self, value):
        """
        验证配置键名
        """
        if not value:
            raise serializers.ValidationError('配置键名不能为空')
        if not value.replace('_', '').replace('.', '').isalnum():
            raise serializers.ValidationError('配置键名只能包含字母、数字、下划线和点')
        return value


class DashboardStatsSerializer(serializers.Serializer):
    """
    仪表盘统计数据序列化器
    """
    projects = serializers.DictField()
    testcases = serializers.DictField()
    bugs = serializers.DictField()
    api_tests = serializers.DictField()
    perf_tests = serializers.DictField()


class ActivitySerializer(serializers.Serializer):
    """
    活动记录序列化器
    """
    id = serializers.IntegerField()
    user = serializers.CharField()
    action = serializers.CharField()
    resource_type = serializers.CharField()
    resource_name = serializers.CharField()
    created_at = serializers.DateTimeField()


class TaskSerializer(serializers.Serializer):
    """
    任务序列化器
    """
    id = serializers.IntegerField()
    title = serializers.CharField()
    priority = serializers.CharField()
    status = serializers.CharField()
    project_name = serializers.CharField()
