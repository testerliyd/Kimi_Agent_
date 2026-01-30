"""
报告生成异步任务模块
"""
import os
import json
from celery import shared_task
from django.conf import settings
from django.template import Template, Context

from .models import Report
from .services import ReportService


@shared_task(bind=True, max_retries=3)
def generate_report_task(self, report_id, date_range_start=None, date_range_end=None):
    """
    异步生成报告
    """
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return {'error': 'Report not found'}
    
    try:
        # 根据报告类型生成数据
        if report.report_type == 'test_summary':
            report_data = ReportService.generate_test_summary_report(
                report.project,
                date_range_start,
                date_range_end
            )
        elif report.report_type == 'api_test':
            # API测试报告需要指定job
            from apps.apitest.models import ApiTestJob
            job = ApiTestJob.objects.filter(project=report.project).order_by('-created_at').first()
            if job:
                report_data = ReportService.generate_api_test_report(job)
            else:
                report_data = {'error': 'No API test job found'}
        elif report.report_type == 'perf_test':
            # 性能测试报告需要指定job
            from apps.perftest.models import PerfTestJob
            job = PerfTestJob.objects.filter(project=report.project).order_by('-created_at').first()
            if job:
                report_data = ReportService.generate_perf_test_report(job)
            else:
                report_data = {'error': 'No perf test job found'}
        elif report.report_type == 'bug_analysis':
            report_data = ReportService.generate_bug_analysis_report(
                report.project,
                date_range_start,
                date_range_end
            )
        else:
            report_data = {}
        
        # 保存报告数据
        report.report_data = report_data
        
        # 生成文件
        if report.format == 'html':
            file_path = generate_html_report_file(report, report_data)
        elif report.format == 'json':
            file_path = generate_json_report_file(report, report_data)
        else:
            file_path = None
        
        if file_path:
            report.file_path = file_path
            report.file_size = os.path.getsize(os.path.join(settings.MEDIA_ROOT, file_path.name))
        
        report.status = 'completed'
        report.save()
        
        return {
            'report_id': report_id,
            'status': 'completed',
            'file_path': str(file_path) if file_path else None
        }
        
    except Exception as e:
        report.status = 'failed'
        report.error_message = str(e)
        report.save()
        
        return {
            'report_id': report_id,
            'status': 'failed',
            'error': str(e)
        }


def generate_html_report_file(report, report_data):
    """
    生成HTML报告文件
    """
    # 获取模板
    if report.template:
        template_content = report.template.content_template
    else:
        # 使用默认模板
        template_content = get_default_html_template(report.report_type)
    
    # 渲染HTML
    template = Template(template_content)
    context = Context(report_data)
    html_content = template.render(context)
    
    # 保存文件
    filename = f'report_{report.id}_{report.created_at.strftime("%Y%m%d%H%M%S")}.html'
    filepath = os.path.join('reports', filename)
    full_path = os.path.join(settings.MEDIA_ROOT, filepath)
    
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filepath


def generate_json_report_file(report, report_data):
    """
    生成JSON报告文件
    """
    filename = f'report_{report.id}_{report.created_at.strftime("%Y%m%d%H%M%S")}.json'
    filepath = os.path.join('reports', filename)
    full_path = os.path.join(settings.MEDIA_ROOT, filepath)
    
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    return filepath


def get_default_html_template(report_type):
    """
    获取默认HTML模板
    """
    templates = {
        'test_summary': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>测试总结报告 - {{ project_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        h2 { color: #666; border-bottom: 1px solid #ddd; padding-bottom: 10px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; }
        .summary { background-color: #f9f9f9; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>测试总结报告</h1>
    <div class="summary">
        <p><strong>项目:</strong> {{ project_name }}</p>
        <p><strong>报告周期:</strong> {{ date_range.start }} 至 {{ date_range.end }}</p>
    </div>
    
    <h2>测试用例统计</h2>
    <p>总计: {{ test_cases.total }}</p>
    
    <h2>Bug统计</h2>
    <p>总计: {{ bugs.total }} | 未解决: {{ bugs.open }} | 已解决: {{ bugs.resolved }} | 已关闭: {{ bugs.closed }}</p>
    
    <h2>API测试统计</h2>
    <p>总计: {{ api_tests.total }} | 通过: {{ api_tests.passed }} | 失败: {{ api_tests.failed }}</p>
    
    <h2>性能测试统计</h2>
    <p>总计: {{ perf_tests.total }} | 通过: {{ perf_tests.passed }} | 失败: {{ perf_tests.failed }}</p>
</body>
</html>
''',
        'api_test': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>API测试报告 - {{ job_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .passed { color: green; }
        .failed { color: red; }
        .error { color: orange; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>API测试报告</h1>
    <p><strong>任务:</strong> {{ job_name }}</p>
    <p><strong>项目:</strong> {{ project_name }}</p>
    <p><strong>执行人:</strong> {{ executor }}</p>
    
    <h2>执行摘要</h2>
    <p>总计: {{ summary.total }} | 通过: <span class="passed">{{ summary.passed }}</span> | 
       失败: <span class="failed">{{ summary.failed }}</span> | 
       错误: <span class="error">{{ summary.error }}</span> | 
       通过率: {{ summary.pass_rate }}%</p>
    
    <h2>详细结果</h2>
    <table>
        <tr><th>用例</th><th>状态</th><th>响应状态码</th><th>响应时间</th></tr>
        {% for result in results %}
        <tr>
            <td>{{ result.test_case }}</td>
            <td class="{{ result.status }}">{{ result.status }}</td>
            <td>{{ result.response_status }}</td>
            <td>{{ result.response_time_ms }}ms</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
''',
        'perf_test': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>性能测试报告 - {{ job_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .metric { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .metric-value { font-size: 24px; font-weight: bold; color: #1890ff; }
    </style>
</head>
<body>
    <h1>性能测试报告</h1>
    <p><strong>任务:</strong> {{ job_name }}</p>
    <p><strong>场景:</strong> {{ scenario_name }}</p>
    <p><strong>项目:</strong> {{ project_name }}</p>
    
    <h2>性能指标</h2>
    <div class="metric">
        <p>平均响应时间</p>
        <p class="metric-value">{{ summary.avg_response_time }} ms</p>
    </div>
    <div class="metric">
        <p>每秒请求数</p>
        <p class="metric-value">{{ summary.requests_per_second }}</p>
    </div>
    <div class="metric">
        <p>错误率</p>
        <p class="metric-value">{{ summary.error_rate }}%</p>
    </div>
    <div class="metric">
        <p>总请求数</p>
        <p class="metric-value">{{ summary.total_requests }}</p>
    </div>
</body>
</html>
''',
    }
    
    return templates.get(report_type, templates['test_summary'])
