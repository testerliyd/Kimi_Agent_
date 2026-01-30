"""
性能测试序列化器模块
"""
from rest_framework import serializers
from .models import PerfTestScenario, PerfTestJob, PerfTestMetrics


class PerfTestScenarioSerializer(serializers.ModelSerializer):
    """
    性能测试场景序列化器
    """
    scenario_type_display = serializers.CharField(source='get_scenario_type_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = PerfTestScenario
        fields = [
            'id', 'name', 'description', 'scenario_type', 'scenario_type_display',
            'target_url', 'http_method', 'headers', 'body',
            'concurrent_users', 'ramp_up_time', 'test_duration',
            'success_criteria', 'is_active',
            'project', 'project_name',
            'created_at', 'updated_at'
        ]


class PerfTestJobListSerializer(serializers.ModelSerializer):
    """
    性能测试任务列表序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    trigger_type_display = serializers.CharField(source='get_trigger_type_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    scenario_name = serializers.CharField(source='scenario.name', read_only=True)
    executor_name = serializers.CharField(source='executor.username', read_only=True)
    
    class Meta:
        model = PerfTestJob
        fields = [
            'id', 'name', 'status', 'status_display',
            'trigger_type', 'trigger_type_display',
            'project', 'project_name', 'scenario', 'scenario_name',
            'executor', 'executor_name',
            'concurrent_users', 'test_duration',
            'avg_response_time', 'error_rate',
            'started_at', 'completed_at', 'created_at'
        ]


class PerfTestJobDetailSerializer(serializers.ModelSerializer):
    """
    性能测试任务详情序列化器
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    trigger_type_display = serializers.CharField(source='get_trigger_type_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    scenario = PerfTestScenarioSerializer(read_only=True)
    executor_name = serializers.CharField(source='executor.username', read_only=True)
    
    class Meta:
        model = PerfTestJob
        fields = [
            'id', 'name', 'description', 'status', 'status_display',
            'trigger_type', 'trigger_type_display',
            'project', 'project_name', 'scenario',
            'concurrent_users', 'test_duration',
            'total_requests', 'avg_response_time',
            'min_response_time', 'max_response_time',
            'error_rate', 'requests_per_second',
            'passed_criteria', 'report_data', 'report_file',
            'executor', 'executor_name',
            'started_at', 'completed_at', 'created_at'
        ]


class PerfTestJobCreateSerializer(serializers.ModelSerializer):
    """
    性能测试任务创建序列化器
    """
    class Meta:
        model = PerfTestJob
        fields = [
            'project', 'scenario', 'name', 'description',
            'concurrent_users', 'test_duration', 'trigger_type'
        ]


class PerfTestMetricsSerializer(serializers.ModelSerializer):
    """
    性能测试指标序列化器
    """
    class Meta:
        model = PerfTestMetrics
        fields = [
            'timestamp', 'total_requests', 'failed_requests',
            'avg_response_time', 'min_response_time', 'max_response_time',
            'p50_response_time', 'p95_response_time', 'p99_response_time',
            'requests_per_second', 'bytes_per_second', 'current_users'
        ]


class PerfTestStatsSerializer(serializers.Serializer):
    """
    性能测试统计序列化器
    """
    total_jobs = serializers.IntegerField()
    by_status = serializers.ListField()
    avg_response_time = serializers.FloatField()
    avg_error_rate = serializers.FloatField()
