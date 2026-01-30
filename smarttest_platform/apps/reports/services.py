"""
报告生成服务模块
"""
import json
import os
from datetime import datetime, timedelta
from django.template import Template, Context
from django.conf import settings


class ReportService:
    """
    报告生成服务类
    """
    
    @staticmethod
    def generate_test_summary_report(project, date_range_start=None, date_range_end=None):
        """
        生成测试总结报告
        """
        from apps.testcases.models import TestCase
        from apps.bugs.models import Bug
        from apps.apitest.models import ApiTestJob
        from apps.perftest.models import PerfTestJob
        
        if not date_range_start:
            date_range_start = datetime.now() - timedelta(days=30)
        if not date_range_end:
            date_range_end = datetime.now()
        
        # 获取统计数据
        test_cases = TestCase.objects.filter(
            project=project,
            is_deleted=False,
            created_at__range=[date_range_start, date_range_end]
        )
        
        bugs = Bug.objects.filter(
            project=project,
            is_deleted=False,
            created_at__range=[date_range_start, date_range_end]
        )
        
        api_tests = ApiTestJob.objects.filter(
            project=project,
            created_at__range=[date_range_start, date_range_end]
        )
        
        perf_tests = PerfTestJob.objects.filter(
            project=project,
            created_at__range=[date_range_start, date_range_end]
        )
        
        report_data = {
            'project_name': project.name,
            'date_range': {
                'start': date_range_start.strftime('%Y-%m-%d'),
                'end': date_range_end.strftime('%Y-%m-%d'),
            },
            'test_cases': {
                'total': test_cases.count(),
                'by_status': list(test_cases.values('status').annotate(count=models.Count('id'))),
                'by_priority': list(test_cases.values('priority').annotate(count=models.Count('id'))),
            },
            'bugs': {
                'total': bugs.count(),
                'by_status': list(bugs.values('status').annotate(count=models.Count('id'))),
                'by_severity': list(bugs.values('severity').annotate(count=models.Count('id'))),
                'open_count': bugs.filter(status__in=['new', 'confirmed', 'in_progress']).count(),
                'resolved_count': bugs.filter(status='resolved').count(),
                'closed_count': bugs.filter(status='closed').count(),
            },
            'api_tests': {
                'total': api_tests.count(),
                'passed': api_tests.filter(status='passed').count(),
                'failed': api_tests.filter(status='failed').count(),
            },
            'perf_tests': {
                'total': perf_tests.count(),
                'passed': perf_tests.filter(status='passed').count(),
                'failed': perf_tests.filter(status='failed').count(),
            },
        }
        
        return report_data
    
    @staticmethod
    def generate_api_test_report(job):
        """
        生成API测试报告
        """
        results = job.results.all()
        
        report_data = {
            'job_name': job.name,
            'project_name': job.project.name,
            'executor': job.executor.username if job.executor else '系统',
            'started_at': job.started_at.strftime('%Y-%m-%d %H:%M:%S') if job.started_at else '',
            'completed_at': job.completed_at.strftime('%Y-%m-%d %H:%M:%S') if job.completed_at else '',
            'duration': job.duration,
            'summary': {
                'total': job.total_cases,
                'passed': job.passed_cases,
                'failed': job.failed_cases,
                'error': job.error_cases,
                'pass_rate': round(job.passed_cases / job.total_cases * 100, 2) if job.total_cases > 0 else 0,
            },
            'results': [
                {
                    'test_case': result.test_case.name,
                    'status': result.status,
                    'response_status': result.response_status,
                    'response_time_ms': result.response_time_ms,
                    'error_message': result.error_message,
                }
                for result in results
            ],
        }
        
        return report_data
    
    @staticmethod
    def generate_perf_test_report(job):
        """
        生成性能测试报告
        """
        metrics = job.metrics.all()
        
        report_data = {
            'job_name': job.name,
            'project_name': job.project.name,
            'scenario_name': job.scenario.name,
            'executor': job.executor.username if job.executor else '系统',
            'started_at': job.started_at.strftime('%Y-%m-%d %H:%M:%S') if job.started_at else '',
            'completed_at': job.completed_at.strftime('%Y-%m-%d %H:%M:%S') if job.completed_at else '',
            'test_config': {
                'concurrent_users': job.concurrent_users or job.scenario.concurrent_users,
                'test_duration': job.test_duration or job.scenario.test_duration,
            },
            'summary': {
                'total_requests': job.total_requests,
                'avg_response_time': job.avg_response_time,
                'min_response_time': job.min_response_time,
                'max_response_time': job.max_response_time,
                'error_rate': job.error_rate,
                'requests_per_second': job.requests_per_second,
                'passed_criteria': job.passed_criteria,
            },
            'metrics': [
                {
                    'timestamp': m.timestamp.strftime('%H:%M:%S'),
                    'avg_response_time': m.avg_response_time,
                    'requests_per_second': m.requests_per_second,
                    'current_users': m.current_users,
                }
                for m in metrics
            ],
        }
        
        return report_data
    
    @staticmethod
    def generate_bug_analysis_report(project, date_range_start=None, date_range_end=None):
        """
        生成Bug分析报告
        """
        from apps.bugs.models import Bug
        
        if not date_range_start:
            date_range_start = datetime.now() - timedelta(days=30)
        if not date_range_end:
            date_range_end = datetime.now()
        
        bugs = Bug.objects.filter(
            project=project,
            is_deleted=False,
            created_at__range=[date_range_start, date_range_end]
        )
        
        report_data = {
            'project_name': project.name,
            'date_range': {
                'start': date_range_start.strftime('%Y-%m-%d'),
                'end': date_range_end.strftime('%Y-%m-%d'),
            },
            'summary': {
                'total': bugs.count(),
                'open': bugs.filter(status__in=['new', 'confirmed', 'in_progress']).count(),
                'resolved': bugs.filter(status='resolved').count(),
                'closed': bugs.filter(status='closed').count(),
            },
            'by_severity': list(bugs.values('severity').annotate(count=models.Count('id'))),
            'by_priority': list(bugs.values('priority').annotate(count=models.Count('id'))),
            'by_status': list(bugs.values('status').annotate(count=models.Count('id'))),
            'by_type': list(bugs.values('bug_type').annotate(count=models.Count('id'))),
            'trend': list(
                bugs.extra(select={'date': "DATE(created_at)"})
                .values('date')
                .annotate(count=models.Count('id'))
                .order_by('date')
            ),
        }
        
        return report_data
    
    @staticmethod
    def render_html_report(report_data, template_content):
        """
        渲染HTML报告
        """
        template = Template(template_content)
        context = Context(report_data)
        return template.render(context)


# 导入django models
from django.db import models
