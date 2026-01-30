"""
接口测试序列化器模块
"""
from rest_framework import serializers
from .models import ApiDefinition, ApiTestCase, ApiTestJob, ApiTestResult


class ApiDefinitionSerializer(serializers.ModelSerializer):
    """
    API定义序列化器
    """
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    full_url = serializers.CharField(source='get_full_url', read_only=True)
    
    class Meta:
        model = ApiDefinition
        fields = [
            'id', 'name', 'description', 'method', 'method_display',
            'path', 'full_url', 'headers', 'params', 'content_type',
            'content_type_display', 'body', 'body_raw',
            'auth_type', 'auth_config', 'is_active',
            'project', 'project_name', 'environment', 'environment_name',
            'created_at', 'updated_at'
        ]


class ApiTestCaseSerializer(serializers.ModelSerializer):
    """
    API测试用例序列化器
    """
    api_info = ApiDefinitionSerializer(source='api', read_only=True)
    
    class Meta:
        model = ApiTestCase
        fields = [
            'id', 'api', 'api_info', 'name', 'description',
            'override_headers', 'override_params', 'override_body',
            'expected_status', 'expected_headers', 'expected_body',
            'validation_rules', 'setup_script', 'teardown_script',
            'is_active', 'created_at', 'updated_at'
        ]


class ApiTestResultSerializer(serializers.ModelSerializer):
    """
    API测试结果序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    test_case_name = serializers.CharField(source='test_case.name', read_only=True)
    
    class Meta:
        model = ApiTestResult
        fields = [
            'id', 'test_case', 'test_case_name', 'status', 'status_display',
            'request_url', 'request_method', 'request_headers', 'request_body',
            'response_status', 'response_headers', 'response_body',
            'response_time_ms', 'validation_results', 'error_message',
            'started_at', 'completed_at', 'duration_ms'
        ]


class ApiTestJobListSerializer(serializers.ModelSerializer):
    """
    API测试任务列表序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    trigger_type_display = serializers.CharField(source='get_trigger_type_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    executor_name = serializers.CharField(source='executor.username', read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = ApiTestJob
        fields = [
            'id', 'name', 'status', 'status_display',
            'trigger_type', 'trigger_type_display',
            'project', 'project_name', 'executor', 'executor_name',
            'total_cases', 'passed_cases', 'failed_cases', 'progress',
            'started_at', 'completed_at', 'created_at'
        ]

    def get_progress(self, obj):
        if obj.total_cases == 0:
            return 0
        return round((obj.passed_cases / obj.total_cases) * 100, 2)


class ApiTestJobDetailSerializer(serializers.ModelSerializer):
    """
    API测试任务详情序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    trigger_type_display = serializers.CharField(source='get_trigger_type_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    executor = serializers.CharField(source='executor.username', read_only=True)
    test_cases = ApiTestCaseSerializer(many=True, read_only=True)
    results = ApiTestResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = ApiTestJob
        fields = [
            'id', 'name', 'description', 'status', 'status_display',
            'trigger_type', 'trigger_type_display',
            'project', 'project_name', 'environment', 'environment_name',
            'test_cases', 'results', 'total_cases', 'passed_cases',
            'failed_cases', 'error_cases', 'executor',
            'started_at', 'completed_at', 'duration',
            'result_summary', 'report_url', 'created_at'
        ]


class ApiTestJobCreateSerializer(serializers.ModelSerializer):
    """
    API测试任务创建序列化器
    """
    class Meta:
        model = ApiTestJob
        fields = [
            'project', 'name', 'description',
            'test_cases', 'environment', 'trigger_type'
        ]


class ApiExecuteSerializer(serializers.Serializer):
    """
    API执行序列化器
    """
    api_id = serializers.IntegerField(required=True)
    environment_id = serializers.IntegerField(required=False, allow_null=True)
    override_headers = serializers.JSONField(required=False, default=dict)
    override_params = serializers.JSONField(required=False, default=dict)
    override_body = serializers.JSONField(required=False, default=dict)
