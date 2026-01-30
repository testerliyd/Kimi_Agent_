"""
Bug管理序列化器模块
"""
from rest_framework import serializers
from .models import Bug, BugComment, BugHistory, BugTag, BugCategory
from apps.users.serializers import UserListSerializer


class BugListSerializer(serializers.ModelSerializer):
    """
    Bug列表序列化器
    """
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    bug_type_display = serializers.CharField(source='get_bug_type_display', read_only=True)
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Bug
        fields = [
            'id', 'bug_no', 'title', 'bug_type', 'bug_type_display',
            'severity', 'severity_display', 'priority', 'priority_display',
            'status', 'status_display', 'module', 'reporter', 'reporter_name',
            'assignee', 'assignee_name', 'project', 'project_name',
            'created_at', 'resolved_at'
        ]


class BugDetailSerializer(serializers.ModelSerializer):
    """
    Bug详情序列化器
    """
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    bug_type_display = serializers.CharField(source='get_bug_type_display', read_only=True)
    reporter = UserListSerializer(read_only=True)
    assignee = UserListSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    version_info = serializers.CharField(source='version.version', read_only=True)
    resolved_version_info = serializers.CharField(source='resolved_version.version', read_only=True)
    related_test_case_info = serializers.CharField(source='related_test_case.name', read_only=True)
    
    class Meta:
        model = Bug
        fields = [
            'id', 'bug_no', 'title', 'description',
            'bug_type', 'bug_type_display',
            'severity', 'severity_display',
            'priority', 'priority_display',
            'status', 'status_display',
            'project', 'project_name', 'version', 'version_info', 'module',
            'reporter', 'assignee', 'environment', 'browser',
            'steps_to_reproduce', 'expected_result', 'actual_result',
            'attachments', 'related_test_case', 'related_test_case_info',
            'confirmed_at', 'resolved_at', 'closed_at',
            'resolution', 'resolved_version', 'resolved_version_info',
            'tags', 'created_at', 'updated_at'
        ]


class BugCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Bug创建/更新序列化器
    """
    class Meta:
        model = Bug
        fields = [
            'project', 'version', 'title', 'description',
            'bug_type', 'severity', 'priority',
            'module', 'environment', 'browser',
            'steps_to_reproduce', 'expected_result', 'actual_result',
            'attachments', 'related_test_case', 'tags'
        ]
        extra_kwargs = {
            'title': {'required': True},
            'description': {'required': True},
        }


class BugAssignSerializer(serializers.Serializer):
    """
    Bug分配序列化器
    """
    assignee_id = serializers.IntegerField(required=True)


class BugResolveSerializer(serializers.Serializer):
    """
    Bug解决序列化器
    """
    resolution = serializers.CharField(required=True)
    resolved_version_id = serializers.IntegerField(required=False, allow_null=True)


class BugReopenSerializer(serializers.Serializer):
    """
    Bug重新打开序列化器
    """
    reason = serializers.CharField(required=True)


class BugCommentSerializer(serializers.ModelSerializer):
    """
    Bug评论序列化器
    """
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = BugComment
        fields = ['id', 'content', 'is_internal', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['created_at']
        extra_kwargs = {
            'content': {'required': True},
        }


class BugHistorySerializer(serializers.ModelSerializer):
    """
    Bug历史序列化器
    """
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    
    class Meta:
        model = BugHistory
        fields = ['id', 'action', 'action_display', 'field', 'old_value', 'new_value', 'operator', 'operator_name', 'created_at']


class BugStatsSerializer(serializers.Serializer):
    """
    Bug统计序列化器
    """
    total = serializers.IntegerField()
    by_status = serializers.ListField()
    by_severity = serializers.ListField()
    by_priority = serializers.ListField()
    by_type = serializers.ListField()


class BugTagSerializer(serializers.ModelSerializer):
    """
    Bug标签序列化器
    """
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = BugTag
        fields = ['id', 'name', 'color', 'description', 'project', 'project_name', 'created_at']


class BugCategorySerializer(serializers.ModelSerializer):
    """
    Bug分类序列化器
    """
    project_name = serializers.CharField(source='project.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = BugCategory
        fields = ['id', 'name', 'description', 'sort_order', 'project', 'project_name',
                  'parent', 'parent_name', 'children', 'created_at']
    
    def get_children(self, obj):
        children = obj.children.filter(is_deleted=False)
        return BugCategorySerializer(children, many=True).data
