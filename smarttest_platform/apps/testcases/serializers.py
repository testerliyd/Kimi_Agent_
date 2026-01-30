"""
用例管理序列化器模块
"""
from rest_framework import serializers
from .models import TestCase, TestSuite, TestPlan, TestCaseTag, TestCaseCategory
from apps.users.serializers import UserListSerializer


class TestCaseListSerializer(serializers.ModelSerializer):
    """
    测试用例列表序列化器
    """
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    case_type_display = serializers.CharField(source='get_case_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    executor_name = serializers.CharField(source='executor.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = TestCase
        fields = [
            'id', 'case_no', 'name', 'case_type', 'case_type_display',
            'priority', 'priority_display', 'status', 'status_display',
            'module', 'executor', 'executor_name', 'project', 'project_name',
            'last_executed_at', 'created_at'
        ]


class TestCaseDetailSerializer(serializers.ModelSerializer):
    """
    测试用例详情序列化器
    """
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    case_type_display = serializers.CharField(source='get_case_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    executor = UserListSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    version_info = serializers.CharField(source='version.version', read_only=True)
    
    class Meta:
        model = TestCase
        fields = [
            'id', 'case_no', 'name', 'description',
            'case_type', 'case_type_display',
            'priority', 'priority_display',
            'status', 'status_display',
            'preconditions', 'steps', 'expected_result', 'actual_result',
            'module', 'tags', 'executor',
            'project', 'project_name', 'version', 'version_info',
            'last_executed_at', 'execution_count', 'pass_count', 'fail_count',
            'related_requirements', 'related_bugs',
            'created_at', 'updated_at'
        ]


class TestCaseCreateUpdateSerializer(serializers.ModelSerializer):
    """
    测试用例创建/更新序列化器
    """
    class Meta:
        model = TestCase
        fields = [
            'project', 'version', 'case_no', 'name', 'description',
            'case_type', 'priority', 'preconditions', 'steps',
            'expected_result', 'module', 'tags',
            'related_requirements', 'related_bugs'
        ]
        extra_kwargs = {
            'case_no': {'required': True},
            'name': {'required': True},
            'expected_result': {'required': True},
        }

    def validate_case_no(self, value):
        """
        验证用例编号
        """
        if not value.replace('-', '').replace('_', '').isalnum():
            raise serializers.ValidationError('用例编号只能包含字母、数字、下划线和连字符')
        return value.upper()

    def validate_steps(self, value):
        """
        验证测试步骤格式
        """
        if not isinstance(value, list):
            raise serializers.ValidationError('测试步骤必须是列表格式')
        
        for i, step in enumerate(value):
            if not isinstance(step, dict):
                raise serializers.ValidationError(f'步骤{i+1}格式错误')
            if 'action' not in step:
                raise serializers.ValidationError(f'步骤{i+1}缺少action字段')
        
        return value


class TestCaseExecuteSerializer(serializers.Serializer):
    """
    测试用例执行序列化器
    """
    RESULT_CHOICES = [
        ('passed', '通过'),
        ('failed', '失败'),
        ('blocked', '阻塞'),
        ('skipped', '跳过'),
    ]
    
    result = serializers.ChoiceField(choices=RESULT_CHOICES, required=True)
    actual_result = serializers.CharField(required=False, allow_blank=True)


class TestSuiteSerializer(serializers.ModelSerializer):
    """
    测试套件序列化器
    """
    case_count = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = TestSuite
        fields = ['id', 'name', 'description', 'project', 'project_name', 'case_count', 'created_at']

    def get_case_count(self, obj):
        return obj.get_case_count()


class TestSuiteDetailSerializer(serializers.ModelSerializer):
    """
    测试套件详情序列化器
    """
    test_cases = TestCaseListSerializer(many=True, read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = TestSuite
        fields = ['id', 'name', 'description', 'project', 'project_name', 'test_cases', 'created_at']


class TestPlanListSerializer(serializers.ModelSerializer):
    """
    测试计划列表序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = TestPlan
        fields = [
            'id', 'name', 'status', 'status_display',
            'manager', 'manager_name', 'project', 'project_name',
            'planned_start_date', 'planned_end_date',
            'total_cases', 'passed_cases', 'failed_cases',
            'progress', 'created_at'
        ]

    def get_progress(self, obj):
        if obj.total_cases == 0:
            return 0
        return round((obj.passed_cases / obj.total_cases) * 100, 2)


class TestPlanDetailSerializer(serializers.ModelSerializer):
    """
    测试计划详情序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    manager = UserListSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    version_info = serializers.CharField(source='version.version', read_only=True)
    test_suites = TestSuiteSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = TestPlan
        fields = [
            'id', 'name', 'description', 'status', 'status_display',
            'manager', 'project', 'project_name', 'version', 'version_info',
            'planned_start_date', 'planned_end_date',
            'actual_start_date', 'actual_end_date',
            'test_suites', 'total_cases', 'passed_cases',
            'failed_cases', 'blocked_cases', 'progress',
            'created_at', 'updated_at'
        ]

    def get_progress(self, obj):
        if obj.total_cases == 0:
            return 0
        return round((obj.passed_cases / obj.total_cases) * 100, 2)


class TestPlanCreateUpdateSerializer(serializers.ModelSerializer):
    """
    测试计划创建/更新序列化器
    """
    class Meta:
        model = TestPlan
        fields = [
            'project', 'version', 'name', 'description',
            'planned_start_date', 'planned_end_date',
            'manager', 'test_suites'
        ]


class TestCaseTagSerializer(serializers.ModelSerializer):
    """
    测试用例标签序列化器
    """
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = TestCaseTag
        fields = ['id', 'name', 'color', 'description', 'project', 'project_name', 'created_at']


class TestCaseCategorySerializer(serializers.ModelSerializer):
    """
    测试用例分类序列化器
    """
    project_name = serializers.CharField(source='project.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = TestCaseCategory
        fields = ['id', 'name', 'description', 'sort_order', 'project', 'project_name', 
                  'parent', 'parent_name', 'children', 'created_at']
    
    def get_children(self, obj):
        children = obj.children.filter(is_deleted=False)
        return TestCaseCategorySerializer(children, many=True).data
