"""
性能测试视图模块
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from django.utils import timezone

from .models import PerfTestScenario, PerfTestJob, PerfTestMetrics
from .serializers import (
    PerfTestScenarioSerializer,
    PerfTestJobListSerializer, PerfTestJobDetailSerializer, PerfTestJobCreateSerializer,
    PerfTestMetricsSerializer, PerfTestStatsSerializer
)
from apps.core.pagination import StandardResultsSetPagination
from apps.feishu.services import FeishuService


class PerfTestScenarioViewSet(viewsets.ModelViewSet):
    """
    性能测试场景视图集
    """
    queryset = PerfTestScenario.objects.filter(is_deleted=False)
    serializer_class = PerfTestScenarioSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'scenario_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser:
            return queryset
        
        return queryset.filter(
            Q(project__project_members__user=user, project__project_members__is_active=True) |
            Q(project__owner=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PerfTestJobViewSet(viewsets.ModelViewSet):
    """
    性能测试任务视图集
    """
    queryset = PerfTestJob.objects.filter(is_deleted=False)
    serializer_class = PerfTestJobDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'scenario', 'status', 'trigger_type']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PerfTestJobListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PerfTestJobCreateSerializer
        return PerfTestJobDetailSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser:
            return queryset
        
        return queryset.filter(
            Q(project__project_members__user=user, project__project_members__is_active=True) |
            Q(project__owner=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, executor=self.request.user)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """
        执行性能测试任务
        """
        from .tasks import execute_perf_test_job
        
        job = self.get_object()
        
        if job.status == 'running':
            return Response({
                'success': False,
                'error': {'message': '任务正在执行中'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新任务状态
        job.status = 'running'
        job.started_at = timezone.now()
        job.executor = request.user
        job.save()
        
        # 异步执行任务
        execute_perf_test_job.delay(job.id)
        
        return Response({
            'success': True,
            'message': '性能测试任务已开始执行',
            'data': {'job_id': job.id, 'status': job.status}
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        取消测试任务
        """
        job = self.get_object()
        
        if job.status != 'running':
            return Response({
                'success': False,
                'error': {'message': '只有运行中的任务可以取消'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        job.status = 'cancelled'
        job.completed_at = timezone.now()
        job.save()
        
        return Response({
            'success': True,
            'message': '性能测试任务已取消'
        })

    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        """
        获取测试指标
        """
        job = self.get_object()
        metrics = job.metrics.all()
        serializer = PerfTestMetricsSerializer(metrics, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def send_report(self, request, pk=None):
        """
        发送测试报告到飞书
        """
        job = self.get_object()
        chat_id = request.data.get('chat_id')
        
        if not chat_id:
            return Response({
                'success': False,
                'error': {'message': '请提供飞书群聊ID'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 发送报告
        FeishuService.send_perf_test_report(job, chat_id)
        
        return Response({
            'success': True,
            'message': '性能测试报告已发送到飞书'
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取测试统计
        """
        queryset = self.get_queryset()
        
        # 按状态统计
        status_stats = queryset.values('status').annotate(count=Q(status=models.Count('id')))
        
        # 平均响应时间和错误率
        avg_stats = queryset.filter(status__in=['passed', 'failed']).aggregate(
            avg_response_time=Avg('avg_response_time'),
            avg_error_rate=Avg('error_rate')
        )
        
        return Response({
            'success': True,
            'data': {
                'total_jobs': queryset.count(),
                'by_status': list(status_stats),
                'avg_response_time': avg_stats['avg_response_time'] or 0,
                'avg_error_rate': avg_stats['avg_error_rate'] or 0,
            }
        })


class PerfTestMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    性能测试指标视图集（只读）
    """
    queryset = PerfTestMetrics.objects.all()
    serializer_class = PerfTestMetricsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['job']
    ordering = ['timestamp']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser:
            return queryset
        
        return queryset.filter(
            Q(job__project__project_members__user=user, job__project__project_members__is_active=True) |
            Q(job__project__owner=user)
        ).distinct()
