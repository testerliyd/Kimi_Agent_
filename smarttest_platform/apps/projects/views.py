"""
项目管理视图模块
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .models import Project, ProjectMember, ProjectVersion, ProjectMilestone, ProjectEnvironment
from .serializers import (
    ProjectListSerializer, ProjectDetailSerializer, ProjectCreateUpdateSerializer,
    ProjectMemberSerializer, ProjectVersionSerializer, ProjectMilestoneSerializer,
    ProjectEnvironmentSerializer, ProjectStatsSerializer
)
from apps.core.pagination import StandardResultsSetPagination


class ProjectViewSet(viewsets.ModelViewSet):
    """
    项目管理视图集
    提供项目的CRUD操作
    """
    queryset = Project.objects.filter(is_deleted=False)
    serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project_type', 'owner']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """
        根据操作返回不同的序列化器
        """
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer

    def get_queryset(self):
        """
        根据用户权限过滤项目
        """
        user = self.request.user
        queryset = super().get_queryset()
        
        # 超级管理员可以看到所有项目
        if user.is_superuser:
            return queryset
        
        # 普通用户只能看到自己是成员的项目或自己创建的项目
        return queryset.filter(
            Q(project_members__user=user, project_members__is_active=True) |
            Q(owner=user) |
            Q(created_by=user)
        ).distinct()

    def perform_create(self, serializer):
        """
        创建项目时记录创建人，并自动添加为项目所有者
        """
        project = serializer.save(created_by=self.request.user)
        
        # 自动添加创建者为项目成员（所有者角色）
        ProjectMember.objects.create(
            project=project,
            user=self.request.user,
            role='owner',
            added_by=self.request.user
        )

    def perform_update(self, serializer):
        """
        更新项目时记录更新人
        """
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def my_projects(self, request):
        """
        获取当前用户的项目列表
        """
        user = request.user
        projects = Project.objects.filter(
            is_deleted=False,
            project_members__user=user,
            project_members__is_active=True
        )
        
        serializer = ProjectListSerializer(projects, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取项目统计信息
        """
        user = request.user
        
        # 基础统计
        total = self.get_queryset().count()
        active = self.get_queryset().filter(status='active').count()
        completed = self.get_queryset().filter(status='completed').count()
        
        # 我的项目
        my_count = Project.objects.filter(
            is_deleted=False,
            project_members__user=user,
            project_members__is_active=True
        ).count()
        
        # 最近项目
        recent = Project.objects.filter(
            is_deleted=False,
            project_members__user=user,
            project_members__is_active=True
        ).order_by('-updated_at')[:5]
        
        data = {
            'total_projects': total,
            'active_projects': active,
            'completed_projects': completed,
            'my_projects': my_count,
            'recent_projects': ProjectListSerializer(recent, many=True).data
        }
        
        return Response({
            'success': True,
            'data': data
        })

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """
        添加项目成员
        """
        project = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'tester')
        
        if not user_id:
            return Response({
                'success': False,
                'error': {'message': '请提供用户ID'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': '用户不存在'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 检查是否已是成员
        if ProjectMember.objects.filter(project=project, user=user, is_active=True).exists():
            return Response({
                'success': False,
                'error': {'message': '该用户已是项目成员'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        member = project.add_member(user, role, request.user)
        
        serializer = ProjectMemberSerializer(member)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """
        移除项目成员
        """
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({
                'success': False,
                'error': {'message': '请提供用户ID'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            member = ProjectMember.objects.get(
                project=project,
                user_id=user_id,
                is_active=True
            )
            member.is_active = False
            member.save()
            
            return Response({
                'success': True,
                'message': '成员已移除'
            })
        except ProjectMember.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': '该用户不是项目成员'}
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def update_member_role(self, request, pk=None):
        """
        更新成员角色
        """
        project = self.get_object()
        user_id = request.data.get('user_id')
        new_role = request.data.get('role')
        
        if not user_id or not new_role:
            return Response({
                'success': False,
                'error': {'message': '请提供用户ID和新角色'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            member = ProjectMember.objects.get(
                project=project,
                user_id=user_id,
                is_active=True
            )
            old_role = member.role
            member.role = new_role
            member.save()
            
            return Response({
                'success': True,
                'message': f'角色已从 {old_role} 更新为 {new_role}',
                'data': {'old_role': old_role, 'new_role': new_role}
            })
        except ProjectMember.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': '该用户不是项目成员'}
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """
        变更项目状态
        """
        project = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({
                'success': False,
                'error': {'message': '请提供新状态'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = project.status
        project.change_status(new_status, request.user)
        
        return Response({
            'success': True,
            'message': f'项目状态已从 {old_status} 变更为 {new_status}',
            'data': {'old_status': old_status, 'new_status': new_status}
        })


class ProjectVersionViewSet(viewsets.ModelViewSet):
    """
    项目版本视图集
    """
    serializer_class = ProjectVersionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'project']
    ordering_fields = ['version', 'created_at', 'planned_start_date']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        根据用户权限过滤版本
        """
        user = self.request.user
        queryset = ProjectVersion.objects.filter(is_deleted=False)
        
        # 超级管理员可以看到所有版本
        if user.is_superuser:
            return queryset
        
        # 普通用户只能看到自己有权限的项目的版本
        return queryset.filter(
            project__project_members__user=user,
            project__project_members__is_active=True
        )

    def perform_create(self, serializer):
        """
        创建版本时记录创建人
        """
        serializer.save(created_by=self.request.user)


class ProjectMilestoneViewSet(viewsets.ModelViewSet):
    """
    项目里程碑视图集
    """
    serializer_class = ProjectMilestoneSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'project', 'version']
    ordering_fields = ['planned_date', 'created_at']
    ordering = ['planned_date']

    def get_queryset(self):
        """
        根据用户权限过滤里程碑
        """
        user = self.request.user
        queryset = ProjectMilestone.objects.filter(is_deleted=False)
        
        if user.is_superuser:
            return queryset
        
        return queryset.filter(
            project__project_members__user=user,
            project__project_members__is_active=True
        )

    def perform_create(self, serializer):
        """
        创建里程碑时记录创建人
        """
        serializer.save(created_by=self.request.user)


class ProjectEnvironmentViewSet(viewsets.ModelViewSet):
    """
    项目环境视图集
    """
    serializer_class = ProjectEnvironmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['env_type', 'project', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['env_type', 'name']

    def get_queryset(self):
        """
        根据用户权限过滤环境
        """
        user = self.request.user
        queryset = ProjectEnvironment.objects.filter(is_deleted=False)
        
        if user.is_superuser:
            return queryset
        
        return queryset.filter(
            project__project_members__user=user,
            project__project_members__is_active=True
        )

    def perform_create(self, serializer):
        """
        创建环境时记录创建人
        """
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        切换环境启用状态
        """
        environment = self.get_object()
        environment.is_active = not environment.is_active
        environment.save()
        
        status_text = '启用' if environment.is_active else '禁用'
        return Response({
            'success': True,
            'message': f'环境已{status_text}',
            'data': {'is_active': environment.is_active}
        })


class ProjectMemberViewSet(viewsets.ModelViewSet):
    """
    项目成员视图集
    """
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['project', 'role', 'is_active']
    ordering_fields = ['created_at', 'role']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        根据用户权限过滤成员
        """
        user = self.request.user
        queryset = ProjectMember.objects.filter(is_active=True)
        
        if user.is_superuser:
            return queryset
        
        # 普通用户只能看到自己有权限的项目的成员
        return queryset.filter(
            project__project_members__user=user,
            project__project_members__is_active=True
        )

    def perform_create(self, serializer):
        """
        添加成员时记录操作人
        """
        serializer.save(added_by=self.request.user)
