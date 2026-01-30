"""
报告管理视图模块
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.http import FileResponse

from .models import ReportTemplate, Report
from .serializers import (
    ReportTemplateSerializer, ReportListSerializer, ReportDetailSerializer,
    ReportCreateSerializer, ReportGenerateSerializer
)
from .services import ReportService
from apps.core.pagination import StandardResultsSetPagination


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """
    报告模板视图集
    """
    queryset = ReportTemplate.objects.filter(is_deleted=False)
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['template_type', 'is_default', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        按类型获取模板
        """
        template_type = request.query_params.get('type')
        if template_type:
            templates = self.get_queryset().filter(template_type=template_type, is_active=True)
        else:
            templates = self.get_queryset().filter(is_active=True)
        
        serializer = self.get_serializer(templates, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })


class ReportViewSet(viewsets.ModelViewSet):
    """
    报告视图集
    """
    serializer_class = ReportDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['report_type', 'status', 'format', 'project']
    search_fields = ['name', 'description']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Report.objects.filter(is_deleted=False)
        
        if user.is_superuser:
            return queryset
        
        return queryset.filter(
            Q(project__project_members__user=user, project__project_members__is_active=True) |
            Q(project__owner=user) |
            Q(created_by=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return ReportListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ReportCreateSerializer
        return ReportDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        下载报告
        """
        report = self.get_object()
        
        if not report.file_path:
            return Response({
                'success': False,
                'error': {'message': '报告文件不存在'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        report.increment_download_count()
        
        return FileResponse(
            report.file_path.open(),
            as_attachment=True,
            filename=report.file_path.name.split('/')[-1]
        )

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        预览报告
        """
        report = self.get_object()
        
        if report.format == 'html' and report.file_path:
            from django.http import HttpResponse
            with report.file_path.open() as f:
                content = f.read()
            return HttpResponse(content, content_type='text/html')
        
        # 非HTML格式返回报告数据
        report.increment_view_count()
        
        serializer = self.get_serializer(report)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        生成报告
        """
        from .tasks import generate_report_task
        
        serializer = ReportGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # 创建报告记录
        report = Report.objects.create(
            name=data['name'],
            report_type=data['report_type'],
            project_id=data['project_id'],
            template_id=data.get('template_id'),
            format=data['format'],
            status='generating',
            created_by=request.user
        )
        
        # 异步生成报告
        generate_report_task.delay(
            report_id=report.id,
            date_range_start=data.get('date_range_start'),
            date_range_end=data.get('date_range_end')
        )
        
        return Response({
            'success': True,
            'message': '报告生成任务已提交',
            'data': {'report_id': report.id, 'status': report.status}
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取报告统计
        """
        queryset = self.get_queryset()
        
        # 按类型统计
        type_stats = queryset.values('report_type').annotate(count=Q(report_type=models.Count('id')))
        
        # 按状态统计
        status_stats = queryset.values('status').annotate(count=Q(status=models.Count('id')))
        
        return Response({
            'success': True,
            'data': {
                'total': queryset.count(),
                'by_type': list(type_stats),
                'by_status': list(status_stats),
            }
        })
