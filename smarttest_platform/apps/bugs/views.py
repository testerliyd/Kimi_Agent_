"""
Bug管理视图模块
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone

from .models import Bug, BugComment, BugHistory, BugTag, BugCategory
from .serializers import (
    BugListSerializer, BugDetailSerializer, BugCreateUpdateSerializer,
    BugAssignSerializer, BugResolveSerializer, BugReopenSerializer,
    BugCommentSerializer, BugHistorySerializer, BugTagSerializer, BugCategorySerializer
)
from apps.core.pagination import StandardResultsSetPagination
from apps.feishu.services import FeishuService


class BugViewSet(viewsets.ModelViewSet):
    """
    Bug管理视图集
    """
    queryset = Bug.objects.filter(is_deleted=False)
    serializer_class = BugDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'project', 'version', 'bug_type', 'severity',
        'priority', 'status', 'module', 'reporter', 'assignee'
    ]
    search_fields = ['bug_no', 'title', 'description']
    ordering_fields = ['created_at', 'priority', 'severity', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return BugListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BugCreateUpdateSerializer
        return BugDetailSerializer

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
        """
        创建Bug时自动生成编号
        """
        from django.utils import timezone
        import time
        
        # 生成Bug编号: BUG + 年月日 + 时间戳后6位
        bug_no = f"BUG{timezone.now().strftime('%Y%m%d')}{str(int(time.time()))[-6:]}"
        
        bug = serializer.save(
            created_by=self.request.user,
            reporter=self.request.user,
            bug_no=bug_no
        )
        
        # 发送飞书通知
        FeishuService.send_bug_notification(bug, 'created')

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        分配Bug
        """
        bug = self.get_object()
        serializer = BugAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            assignee = User.objects.get(id=serializer.validated_data['assignee_id'])
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': '用户不存在'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        bug.assign_to(assignee, request.user)
        
        # 发送飞书通知
        FeishuService.send_bug_notification(bug, 'assigned')
        
        return Response({
            'success': True,
            'message': f'Bug已分配给 {assignee.username}',
            'data': {'assignee': assignee.username}
        })

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        解决Bug
        """
        bug = self.get_object()
        serializer = BugResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        resolution = serializer.validated_data['resolution']
        resolved_version_id = serializer.validated_data.get('resolved_version_id')
        
        bug.resolution = resolution
        if resolved_version_id:
            bug.resolved_version_id = resolved_version_id
        
        bug.resolve(resolution, request.user)
        
        # 发送飞书通知
        FeishuService.send_bug_notification(bug, 'resolved')
        
        return Response({
            'success': True,
            'message': 'Bug已解决',
            'data': {'status': bug.status}
        })

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        关闭Bug
        """
        bug = self.get_object()
        bug.close(request.user)
        
        # 发送飞书通知
        FeishuService.send_bug_notification(bug, 'closed')
        
        return Response({
            'success': True,
            'message': 'Bug已关闭',
            'data': {'status': bug.status}
        })

    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """
        重新打开Bug
        """
        bug = self.get_object()
        serializer = BugReopenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reason = serializer.validated_data['reason']
        bug.reopen(reason, request.user)
        
        # 发送飞书通知
        FeishuService.send_bug_notification(bug, 'reopened')
        
        return Response({
            'success': True,
            'message': 'Bug已重新打开',
            'data': {'status': bug.status}
        })

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """
        添加评论
        """
        bug = self.get_object()
        serializer = BugCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        comment = BugComment.objects.create(
            bug=bug,
            created_by=request.user,
            **serializer.validated_data
        )
        
        return Response({
            'success': True,
            'data': BugCommentSerializer(comment).data
        })

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        获取Bug评论列表
        """
        bug = self.get_object()
        comments = bug.comments.filter(is_deleted=False)
        
        # 非项目成员只能看到非内部评论
        user = request.user
        if not user.is_superuser:
            try:
                member = bug.project.project_members.get(user=user, is_active=True)
            except:
                comments = comments.filter(is_internal=False)
        
        serializer = BugCommentSerializer(comments, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        获取Bug历史记录
        """
        bug = self.get_object()
        history = bug.history.all()
        serializer = BugHistorySerializer(history, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取Bug统计信息
        """
        queryset = self.get_queryset()
        
        # 按状态统计
        status_stats = queryset.values('status').annotate(count=Count('id'))
        
        # 按严重程度统计
        severity_stats = queryset.values('severity').annotate(count=Count('id'))
        
        # 按优先级统计
        priority_stats = queryset.values('priority').annotate(count=Count('id'))
        
        # 按类型统计
        type_stats = queryset.values('bug_type').annotate(count=Count('id'))
        
        return Response({
            'success': True,
            'data': {
                'total': queryset.count(),
                'by_status': list(status_stats),
                'by_severity': list(severity_stats),
                'by_priority': list(priority_stats),
                'by_type': list(type_stats),
            }
        })

    @action(detail=False, methods=['get'])
    def my_bugs(self, request):
        """
        获取分配给我的Bug
        """
        bugs = self.get_queryset().filter(
            assignee=request.user,
            status__in=['new', 'confirmed', 'in_progress', 'reopened']
        ).order_by('-priority', 'created_at')
        
        serializer = BugListSerializer(bugs, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def reported_by_me(self, request):
        """
        获取我报告的Bug
        """
        bugs = self.get_queryset().filter(
            reporter=request.user
        ).order_by('-created_at')
        
        serializer = BugListSerializer(bugs, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })


class BugCommentViewSet(viewsets.ModelViewSet):
    """
    Bug评论视图集
    """
    queryset = BugComment.objects.filter(is_deleted=False)
    serializer_class = BugCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['bug']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BugHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Bug历史记录视图集（只读）
    """
    queryset = BugHistory.objects.all()
    serializer_class = BugHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['bug']
    ordering = ['-created_at']


class BugTagViewSet(viewsets.ModelViewSet):
    """
    Bug标签视图集
    """
    queryset = BugTag.objects.all()
    serializer_class = BugTagSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name']


class BugCategoryViewSet(viewsets.ModelViewSet):
    """
    Bug分类视图集
    """
    queryset = BugCategory.objects.filter(is_deleted=False)
    serializer_class = BugCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'parent']
    search_fields = ['name']
