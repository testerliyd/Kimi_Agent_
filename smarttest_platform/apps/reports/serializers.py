"""
报告管理序列化器模块
"""
from rest_framework import serializers
from .models import ReportTemplate, Report


class ReportTemplateSerializer(serializers.ModelSerializer):
    """
    报告模板序列化器
    """
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'template_type', 'template_type_display',
            'description', 'content_template', 'style_css',
            'is_default', 'is_active', 'created_at'
        ]


class ReportListSerializer(serializers.ModelSerializer):
    """
    报告列表序列化器
    """
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type', 'report_type_display',
            'status', 'status_display', 'format', 'format_display',
            'project', 'project_name', 'file_size',
            'view_count', 'download_count', 'created_at'
        ]


class ReportDetailSerializer(serializers.ModelSerializer):
    """
    报告详情序列化器
    """
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'description', 'report_type', 'report_type_display',
            'status', 'status_display', 'format', 'format_display',
            'project', 'project_name', 'template', 'template_name',
            'report_data', 'file_path', 'file_size',
            'view_count', 'download_count', 'error_message',
            'created_at', 'updated_at'
        ]


class ReportCreateSerializer(serializers.ModelSerializer):
    """
    报告创建序列化器
    """
    class Meta:
        model = Report
        fields = [
            'name', 'description', 'report_type',
            'project', 'template', 'format'
        ]


class ReportGenerateSerializer(serializers.Serializer):
    """
    报告生成序列化器
    """
    REPORT_TYPE_CHOICES = [
        ('test_summary', '测试总结报告'),
        ('api_test', 'API测试报告'),
        ('perf_test', '性能测试报告'),
        ('bug_analysis', 'Bug分析报告'),
    ]
    
    name = serializers.CharField(required=True)
    report_type = serializers.ChoiceField(choices=REPORT_TYPE_CHOICES, required=True)
    project_id = serializers.IntegerField(required=True)
    template_id = serializers.IntegerField(required=False, allow_null=True)
    format = serializers.ChoiceField(choices=['html', 'pdf', 'excel'], default='html')
    date_range_start = serializers.DateField(required=False, allow_null=True)
    date_range_end = serializers.DateField(required=False, allow_null=True)
