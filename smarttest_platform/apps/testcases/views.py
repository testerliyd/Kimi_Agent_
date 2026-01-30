"""
用例管理视图模块
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count

from .models import TestCase, TestSuite, TestPlan, TestCaseTag, TestCaseCategory
from .serializers import (
    TestCaseListSerializer, TestCaseDetailSerializer, TestCaseCreateUpdateSerializer,
    TestCaseExecuteSerializer, TestSuiteSerializer, TestSuiteDetailSerializer,
    TestPlanListSerializer, TestPlanDetailSerializer, TestPlanCreateUpdateSerializer,
    TestCaseTagSerializer, TestCaseCategorySerializer
)
from apps.core.pagination import StandardResultsSetPagination


class TestCaseViewSet(viewsets.ModelViewSet):
    """
    测试用例视图集
    """
    queryset = TestCase.objects.filter(is_deleted=False)
    serializer_class = TestCaseDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'version', 'case_type', 'priority', 'status', 'module']
    search_fields = ['case_no', 'name', 'description']
    ordering_fields = ['created_at', 'priority', 'last_executed_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return TestCaseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TestCaseCreateUpdateSerializer
        return TestCaseDetailSerializer

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

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """
        执行测试用例
        """
        test_case = self.get_object()
        serializer = TestCaseExecuteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        result = serializer.validated_data['result']
        actual_result = serializer.validated_data.get('actual_result', '')
        
        test_case.execute(result, request.user, actual_result)
        
        return Response({
            'success': True,
            'message': f'用例执行完成，结果: {result}',
            'data': {
                'status': test_case.status,
                'execution_count': test_case.execution_count,
                'last_executed_at': test_case.last_executed_at
            }
        })

    @action(detail=False, methods=['post'])
    def batch_execute(self, request):
        """
        批量执行测试用例
        """
        case_ids = request.data.get('case_ids', [])
        result = request.data.get('result')
        
        if not case_ids or not result:
            return Response({
                'success': False,
                'error': {'message': '请提供用例ID列表和执行结果'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cases = self.get_queryset().filter(id__in=case_ids)
        executed_count = 0
        
        for case in cases:
            case.execute(result, request.user)
            executed_count += 1
        
        return Response({
            'success': True,
            'message': f'成功执行 {executed_count} 个用例',
            'data': {'executed_count': executed_count}
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取用例统计信息
        """
        queryset = self.get_queryset()
        
        # 按状态统计
        status_stats = queryset.values('status').annotate(
            count=Count('id')
        )
        
        # 按优先级统计
        priority_stats = queryset.values('priority').annotate(
            count=Count('id')
        )
        
        # 按类型统计
        type_stats = queryset.values('case_type').annotate(
            count=Count('id')
        )
        
        return Response({
            'success': True,
            'data': {
                'total': queryset.count(),
                'status_statistics': list(status_stats),
                'priority_statistics': list(priority_stats),
                'type_statistics': list(type_stats),
            }
        })


class TestSuiteViewSet(viewsets.ModelViewSet):
    """
    测试套件视图集
    """
    queryset = TestSuite.objects.filter(is_deleted=False)
    serializer_class = TestSuiteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project']
    search_fields = ['name', 'description']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TestSuiteDetailSerializer
        return TestSuiteSerializer

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
    def add_cases(self, request, pk=None):
        """
        添加用例到套件
        """
        suite = self.get_object()
        case_ids = request.data.get('case_ids', [])
        
        if not case_ids:
            return Response({
                'success': False,
                'error': {'message': '请提供用例ID列表'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cases = TestCase.objects.filter(id__in=case_ids, is_deleted=False)
        suite.test_cases.add(*cases)
        
        return Response({
            'success': True,
            'message': f'成功添加 {cases.count()} 个用例',
            'data': {'case_count': suite.get_case_count()}
        })

    @action(detail=True, methods=['post'])
    def remove_cases(self, request, pk=None):
        """
        从套件移除用例
        """
        suite = self.get_object()
        case_ids = request.data.get('case_ids', [])
        
        if not case_ids:
            return Response({
                'success': False,
                'error': {'message': '请提供用例ID列表'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cases = TestCase.objects.filter(id__in=case_ids)
        suite.test_cases.remove(*cases)
        
        return Response({
            'success': True,
            'message': '用例已移除',
            'data': {'case_count': suite.get_case_count()}
        })


class TestPlanViewSet(viewsets.ModelViewSet):
    """
    测试计划视图集
    """
    queryset = TestPlan.objects.filter(is_deleted=False)
    serializer_class = TestPlanDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'version', 'status', 'manager']
    search_fields = ['name', 'description']

    def get_serializer_class(self):
        if self.action == 'list':
            return TestPlanListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TestPlanCreateUpdateSerializer
        return TestPlanDetailSerializer

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
    def start(self, request, pk=None):
        """
        开始执行测试计划
        """
        plan = self.get_object()
        
        if plan.status != 'pending':
            return Response({
                'success': False,
                'error': {'message': '只有待执行的计划可以开始'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from django.utils import timezone
        plan.status = 'running'
        plan.actual_start_date = timezone.now()
        plan.save()
        
        return Response({
            'success': True,
            'message': '测试计划已开始执行',
            'data': {'status': plan.status}
        })

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        完成测试计划
        """
        plan = self.get_object()
        
        if plan.status != 'running':
            return Response({
                'success': False,
                'error': {'message': '只有执行中的计划可以完成'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from django.utils import timezone
        plan.status = 'completed'
        plan.actual_end_date = timezone.now()
        plan.update_statistics()
        plan.save()
        
        return Response({
            'success': True,
            'message': '测试计划已完成',
            'data': {'status': plan.status}
        })

    @action(detail=True, methods=['post'])
    def update_stats(self, request, pk=None):
        """
        更新计划统计信息
        """
        plan = self.get_object()
        plan.update_statistics()
        
        return Response({
            'success': True,
            'data': {
                'total_cases': plan.total_cases,
                'passed_cases': plan.passed_cases,
                'failed_cases': plan.failed_cases,
                'blocked_cases': plan.blocked_cases,
            }
        })

    @action(detail=False, methods=['get'])
    def my_plans(self, request):
        """
        获取我负责的测试计划
        """
        plans = self.get_queryset().filter(manager=request.user)
        serializer = TestPlanListSerializer(plans, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })


class TestCaseTagViewSet(viewsets.ModelViewSet):
    """
    测试用例标签视图集
    """
    queryset = TestCaseTag.objects.all()
    serializer_class = TestCaseTagSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']


class TestCaseCategoryViewSet(viewsets.ModelViewSet):
    """
    测试用例分类视图集
    """
    queryset = TestCaseCategory.objects.filter(is_deleted=False)
    serializer_class = TestCaseCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'parent']
    search_fields = ['name']
