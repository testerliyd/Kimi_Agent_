"""
核心应用视图模块
包含审计日志、系统配置、仪表盘等视图
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import AuditLog, SystemConfig
from .pagination import StandardResultsSetPagination
from .serializers import (
    AuditLogSerializer,
    AuditLogCreateSerializer,
    SystemConfigSerializer,
    DashboardStatsSerializer
)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    审计日志视图集
    提供审计日志的查询功能
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'resource_type', 'user']
    search_fields = ['resource_name', 'description']
    ordering_fields = ['created_at', 'action']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        根据用户权限过滤日志
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # 非管理员只能查看自己的操作日志
        if not user.is_staff:
            queryset = queryset.filter(user=user)
        
        return queryset

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取审计日志统计信息
        """
        # 时间范围过滤
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = self.get_queryset().filter(created_at__gte=start_date)
        
        # 按操作类型统计
        action_stats = queryset.values('action').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # 按资源类型统计
        resource_stats = queryset.values('resource_type').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # 按日期统计
        daily_stats = queryset.extra(
            select={'date': "DATE(created_at)"}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return Response({
            'success': True,
            'data': {
                'action_statistics': list(action_stats),
                'resource_statistics': list(resource_stats),
                'daily_statistics': list(daily_stats),
                'total_count': queryset.count(),
            }
        })


class SystemConfigViewSet(viewsets.ModelViewSet):
    """
    系统配置视图集
    管理系统级别的配置项
    """
    queryset = SystemConfig.objects.all()
    serializer_class = SystemConfigSerializer
    permission_classes = [IsAdminUser]  # 只有管理员可以管理配置
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['config_type', 'is_public']
    search_fields = ['key', 'description']
    lookup_field = 'key'

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def public(self, request):
        """
        获取公开配置（所有用户可访问）
        """
        configs = SystemConfig.objects.filter(is_public=True)
        serializer = self.get_serializer(configs, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def get_value(self, request):
        """
        根据key获取配置值
        """
        key = request.query_params.get('key')
        if not key:
            return Response({
                'success': False,
                'error': {'message': '请提供配置键名'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        value = SystemConfig.get_config(key)
        if value is None:
            return Response({
                'success': False,
                'error': {'message': '配置不存在'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'data': {'key': key, 'value': value}
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def batch_update(self, request):
        """
        批量更新配置
        """
        configs = request.data.get('configs', [])
        if not isinstance(configs, list):
            return Response({
                'success': False,
                'error': {'message': 'configs必须是列表'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        updated = []
        errors = []
        
        for config_data in configs:
            key = config_data.get('key')
            if not key:
                errors.append({'data': config_data, 'error': '缺少key'})
                continue
            
            try:
                config = SystemConfig.set_config(
                    key=key,
                    value=config_data.get('value'),
                    config_type=config_data.get('config_type', 'STRING'),
                    description=config_data.get('description', '')
                )
                updated.append(config.key)
            except Exception as e:
                errors.append({'key': key, 'error': str(e)})
        
        return Response({
            'success': True,
            'data': {
                'updated': updated,
                'errors': errors,
                'total': len(configs),
                'success_count': len(updated),
                'error_count': len(errors),
            }
        })


class DashboardViewSet(viewsets.ViewSet):
    """
    仪表盘视图集
    提供系统概览和统计数据
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        获取仪表盘概览数据
        """
        from apps.projects.models import Project
        from apps.testcases.models import TestCase
        from apps.bugs.models import Bug
        from apps.apitest.models import ApiTestJob
        from apps.perftest.models import PerfTestJob
        
        # 获取时间范围
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        # 统计数据
        stats = {
            'projects': {
                'total': Project.objects.filter(is_deleted=False).count(),
                'active': Project.objects.filter(
                    is_deleted=False,
                    status='active'
                ).count(),
            },
            'testcases': {
                'total': TestCase.objects.filter(is_deleted=False).count(),
                'executed_this_week': TestCase.objects.filter(
                    is_deleted=False,
                    last_executed_at__gte=start_date
                ).count(),
            },
            'bugs': {
                'total': Bug.objects.filter(is_deleted=False).count(),
                'open': Bug.objects.filter(
                    is_deleted=False,
                    status__in=['new', 'confirmed', 'in_progress']
                ).count(),
                'resolved_this_week': Bug.objects.filter(
                    is_deleted=False,
                    status='resolved',
                    resolved_at__gte=start_date
                ).count(),
            },
            'api_tests': {
                'total_jobs': ApiTestJob.objects.count(),
                'success_rate': self._calculate_api_success_rate(start_date),
                'executed_this_week': ApiTestJob.objects.filter(
                    created_at__gte=start_date
                ).count(),
            },
            'perf_tests': {
                'total_jobs': PerfTestJob.objects.count(),
                'executed_this_week': PerfTestJob.objects.filter(
                    created_at__gte=start_date
                ).count(),
            },
        }
        
        return Response({
            'success': True,
            'data': stats
        })

    def _calculate_api_success_rate(self, start_date):
        """
        计算API测试成功率
        """
        from apps.apitest.models import ApiTestJob
        jobs = ApiTestJob.objects.filter(created_at__gte=start_date)
        total = jobs.count()
        if total == 0:
            return 0
        passed = jobs.filter(status='passed').count()
        return round(passed / total * 100, 2)

    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        """
        获取最近活动
        """
        limit = int(request.query_params.get('limit', 10))
        
        # 获取最近的操作日志
        logs = AuditLog.objects.select_related('user').order_by('-created_at')[:limit]
        
        activities = []
        for log in logs:
            activities.append({
                'id': log.id,
                'user': log.user.username if log.user else '系统',
                'action': log.get_action_display(),
                'resource_type': log.resource_type,
                'resource_name': log.resource_name,
                'created_at': log.created_at,
            })
        
        return Response({
            'success': True,
            'data': activities
        })

    @action(detail=False, methods=['get'])
    def recent_bugs(self, request):
        """
        获取最近Bug
        """
        from apps.bugs.models import Bug
        limit = int(request.query_params.get('limit', 10))
        
        bugs = Bug.objects.filter(is_deleted=False).select_related('project').order_by('-created_at')[:limit]
        
        data = []
        for bug in bugs:
            data.append({
                'id': bug.id,
                'title': bug.title,
                'severity': bug.severity,
                'status': bug.status,
                'created_at': bug.created_at,
            })
        
        return Response({
            'success': True,
            'data': data
        })

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """
        获取当前用户的待办任务
        """
        from apps.bugs.models import Bug
        from apps.testcases.models import TestCase
        
        user = request.user
        
        # 分配给用户的Bug
        assigned_bugs = Bug.objects.filter(
            is_deleted=False,
            assignee=user,
            status__in=['new', 'confirmed', 'in_progress']
        ).order_by('-priority', 'created_at')[:5]
        
        # 用户需要执行的测试用例
        pending_cases = TestCase.objects.filter(
            is_deleted=False,
            executor=user,
            status='pending'
        ).order_by('-priority', 'created_at')[:5]
        
        return Response({
            'success': True,
            'data': {
                'bugs': [
                    {
                        'id': bug.id,
                        'title': bug.title,
                        'priority': bug.priority,
                        'status': bug.status,
                        'project_name': bug.project.name,
                    }
                    for bug in assigned_bugs
                ],
                'testcases': [
                    {
                        'id': case.id,
                        'name': case.name,
                        'priority': case.priority,
                        'project_name': case.project.name,
                    }
                    for case in pending_cases
                ],
            }
        })


class HealthCheckView(APIView):
    """
    健康检查视图
    用于监控系统健康状态
    """
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        """
        执行健康检查
        """
        from django.db import connection
        from django.core.cache import cache
        import redis
        from django.conf import settings
        
        checks = {
            'database': self._check_database(),
            'cache': self._check_cache(),
            'celery': self._check_celery(),
        }
        
        all_healthy = all(check['status'] == 'ok' for check in checks.values())
        
        status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response({
            'success': all_healthy,
            'data': {
                'status': 'healthy' if all_healthy else 'unhealthy',
                'timestamp': timezone.now().isoformat(),
                'checks': checks,
            }
        }, status=status_code)

    def _check_database(self):
        """
        检查数据库连接
        """
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return {'status': 'ok', 'message': '数据库连接正常'}
        except Exception as e:
            return {'status': 'error', 'message': f'数据库连接失败: {str(e)}'}

    def _check_cache(self):
        """
        检查缓存连接
        """
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 10)
            value = cache.get('health_check')
            if value == 'ok':
                return {'status': 'ok', 'message': '缓存连接正常'}
            return {'status': 'warning', 'message': '缓存读取异常'}
        except Exception as e:
            return {'status': 'error', 'message': f'缓存连接失败: {str(e)}'}

    def _check_celery(self):
        """
        检查Celery状态
        """
        try:
            from smarttest.celery import app
            inspector = app.control.inspect()
            stats = inspector.stats()
            if stats:
                return {'status': 'ok', 'message': 'Celery运行正常', 'workers': len(stats)}
            return {'status': 'warning', 'message': 'Celery无活跃工作者'}
        except Exception as e:
            return {'status': 'error', 'message': f'Celery检查失败: {str(e)}'}


class SystemStatsView(APIView):
    """
    系统统计视图
    提供系统运行统计数据
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        """
        获取系统统计信息
        """
        import psutil
        import os
        
        # 系统资源使用
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        stats = {
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100,
                },
            },
            'application': self._get_app_stats(),
        }
        
        return Response({
            'success': True,
            'data': stats
        })

    def _get_app_stats(self):
        """
        获取应用统计信息
        """
        from apps.users.models import User
        from apps.projects.models import Project
        from apps.testcases.models import TestCase
        from apps.bugs.models import Bug
        
        return {
            'total_users': User.objects.filter(is_active=True).count(),
            'total_projects': Project.objects.filter(is_deleted=False).count(),
            'total_testcases': TestCase.objects.filter(is_deleted=False).count(),
            'total_bugs': Bug.objects.filter(is_deleted=False).count(),
        }
