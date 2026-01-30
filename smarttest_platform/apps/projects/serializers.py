"""
项目管理序列化器模块
"""
from rest_framework import serializers
from .models import Project, ProjectMember, ProjectVersion, ProjectMilestone, ProjectEnvironment
from apps.users.serializers import UserListSerializer


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    项目成员序列化器
    """
    user = UserListSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    added_by_name = serializers.CharField(source='added_by.username', read_only=True)
    
    class Meta:
        model = ProjectMember
        fields = [
            'id', 'user', 'user_id', 'role', 'role_display',
            'is_active', 'joined_at', 'added_by', 'added_by_name'
        ]
        read_only_fields = ['joined_at']


class ProjectVersionSerializer(serializers.ModelSerializer):
    """
    项目版本序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    test_case_count = serializers.SerializerMethodField()
    bug_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectVersion
        fields = [
            'id', 'version', 'name', 'description', 'status', 'status_display',
            'planned_start_date', 'planned_end_date',
            'actual_start_date', 'actual_end_date',
            'manager', 'manager_name', 'scope',
            'test_case_count', 'bug_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_test_case_count(self, obj):
        return obj.get_test_case_count()

    def get_bug_count(self, obj):
        return obj.get_bug_count()


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    """
    项目里程碑序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    version_info = ProjectVersionSerializer(source='version', read_only=True)
    
    class Meta:
        model = ProjectMilestone
        fields = [
            'id', 'name', 'description', 'status', 'status_display',
            'planned_date', 'actual_date', 'version', 'version_info',
            'created_at', 'updated_at'
        ]


class ProjectEnvironmentSerializer(serializers.ModelSerializer):
    """
    项目环境序列化器
    """
    env_type_display = serializers.CharField(source='get_env_type_display', read_only=True)
    
    class Meta:
        model = ProjectEnvironment
        fields = [
            'id', 'name', 'env_type', 'env_type_display',
            'base_url', 'description', 'variables', 'is_active',
            'created_at', 'updated_at'
        ]


class ProjectListSerializer(serializers.ModelSerializer):
    """
    项目列表序列化器（简化版）
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'code', 'name', 'project_type',
            'status', 'status_display',
            'priority', 'priority_display',
            'owner', 'owner_name', 'member_count',
            'start_date', 'end_date', 'created_at'
        ]

    def get_member_count(self, obj):
        return obj.get_member_count()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    项目详情序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    project_type_display = serializers.CharField(source='get_project_type_display', read_only=True)
    owner = UserListSerializer(read_only=True)
    owner_id = serializers.IntegerField(write_only=True, required=False)
    members = ProjectMemberSerializer(source='project_members', many=True, read_only=True)
    versions = ProjectVersionSerializer(many=True, read_only=True)
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)
    environments = ProjectEnvironmentSerializer(many=True, read_only=True)
    
    # 统计信息
    member_count = serializers.SerializerMethodField()
    test_case_count = serializers.SerializerMethodField()
    bug_count = serializers.SerializerMethodField()
    open_bug_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'code', 'name', 'description',
            'project_type', 'project_type_display',
            'priority', 'priority_display',
            'status', 'status_display',
            'start_date', 'end_date',
            'owner', 'owner_id', 'config',
            'jira_project_key', 'git_repository',
            'members', 'member_count',
            'versions', 'milestones', 'environments',
            'test_case_count', 'bug_count', 'open_bug_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_member_count(self, obj):
        return obj.get_member_count()

    def get_test_case_count(self, obj):
        return obj.get_test_case_count()

    def get_bug_count(self, obj):
        return obj.get_bug_count()

    def get_open_bug_count(self, obj):
        return obj.get_bug_count(status__in=['new', 'confirmed', 'in_progress'])


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """
    项目创建/更新序列化器
    """
    class Meta:
        model = Project
        fields = [
            'code', 'name', 'description', 'project_type',
            'priority', 'status', 'start_date', 'end_date',
            'owner', 'config', 'jira_project_key', 'git_repository'
        ]
        extra_kwargs = {
            'code': {'required': True},
            'name': {'required': True},
        }

    def validate_code(self, value):
        """
        验证项目编码
        """
        if not value.replace('-', '').replace('_', '').isalnum():
            raise serializers.ValidationError('项目编码只能包含字母、数字、下划线和连字符')
        return value.upper()

    def validate(self, attrs):
        """
        验证日期范围
        """
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                'end_date': '结束日期不能早于开始日期'
            })
        
        return attrs


class ProjectStatsSerializer(serializers.Serializer):
    """
    项目统计序列化器
    """
    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    my_projects = serializers.IntegerField()
    recent_projects = serializers.ListField()
