"""
接口测试视图模块
"""
import json
import time
import requests
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from .models import ApiDefinition, ApiTestCase, ApiTestJob, ApiTestResult
from .serializers import (
    ApiDefinitionSerializer, ApiTestCaseSerializer,
    ApiTestJobListSerializer, ApiTestJobDetailSerializer, ApiTestJobCreateSerializer,
    ApiTestResultSerializer, ApiExecuteSerializer
)
from apps.core.pagination import StandardResultsSetPagination
from apps.feishu.services import FeishuService


class ApiDefinitionViewSet(viewsets.ModelViewSet):
    """
    API定义视图集
    """
    queryset = ApiDefinition.objects.filter(is_deleted=False)
    serializer_class = ApiDefinitionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'environment', 'method', 'is_active']
    search_fields = ['name', 'path', 'description']
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

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """
        快速测试API
        """
        api = self.get_object()
        serializer = ApiExecuteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # 构建请求
        url = api.get_full_url()
        method = api.method
        headers = {**api.headers, **data.get('override_headers', {})}
        params = {**api.params, **data.get('override_params', {})}
        
        # 处理请求体
        body = api.body_raw if api.body_raw else json.dumps(api.body)
        if data.get('override_body'):
            body = json.dumps(data['override_body'])
        
        try:
            start_time = time.time()
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=body if method != 'GET' else None,
                timeout=30
            )
            
            duration = int((time.time() - start_time) * 1000)
            
            return Response({
                'success': True,
                'data': {
                    'request': {
                        'url': url,
                        'method': method,
                        'headers': headers,
                        'params': params,
                        'body': body
                    },
                    'response': {
                        'status_code': response.status_code,
                        'headers': dict(response.headers),
                        'body': response.text[:10000],  # 限制响应体大小
                        'time_ms': duration
                    }
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {'message': f'请求失败: {str(e)}'}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApiTestCaseViewSet(viewsets.ModelViewSet):
    """
    API测试用例视图集
    """
    queryset = ApiTestCase.objects.filter(is_deleted=False)
    serializer_class = ApiTestCaseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['api', 'api__project', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser:
            return queryset
        
        return queryset.filter(
            Q(api__project__project_members__user=user, api__project__project_members__is_active=True) |
            Q(api__project__owner=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ApiTestJobViewSet(viewsets.ModelViewSet):
    """
    API测试任务视图集
    """
    queryset = ApiTestJob.objects.filter(is_deleted=False)
    serializer_class = ApiTestJobDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'status', 'trigger_type', 'executor']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ApiTestJobListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ApiTestJobCreateSerializer
        return ApiTestJobDetailSerializer

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
        执行API测试任务
        """
        from .tasks import execute_api_test_job
        
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
        execute_api_test_job.delay(job.id)
        
        return Response({
            'success': True,
            'message': '测试任务已开始执行',
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
            'message': '测试任务已取消'
        })

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """
        获取测试结果
        """
        job = self.get_object()
        results = job.results.all()
        serializer = ApiTestResultSerializer(results, many=True)
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
        FeishuService.send_api_test_report(job, chat_id)
        
        return Response({
            'success': True,
            'message': '测试报告已发送到飞书'
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取测试统计
        """
        queryset = self.get_queryset()
        
        # 按状态统计
        status_stats = queryset.values('status').annotate(count=Q(status=models.Count('id')))
        
        # 按触发方式统计
        trigger_stats = queryset.values('trigger_type').annotate(count=Q(trigger_type=models.Count('id')))
        
        return Response({
            'success': True,
            'data': {
                'total': queryset.count(),
                'by_status': list(status_stats),
                'by_trigger': list(trigger_stats),
            }
        })


class ApiTestResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API测试结果视图集（只读）
    """
    queryset = ApiTestResult.objects.all()
    serializer_class = ApiTestResultSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['job', 'test_case', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.is_superuser:
            return queryset
        
        return queryset.filter(
            Q(job__project__project_members__user=user, job__project__project_members__is_active=True) |
            Q(job__project__owner=user)
        ).distinct()
