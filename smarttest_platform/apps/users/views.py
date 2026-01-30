"""
用户管理视图模块
"""
from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import pandas as pd
import io

from .models import Role, UserRole, Permission, UserLoginLog
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserPasswordChangeSerializer, UserPasswordResetSerializer,
    UserProfileSerializer, RoleSerializer, RoleCreateUpdateSerializer,
    UserRoleSerializer, PermissionSerializer, UserLoginLogSerializer,
    UserListSerializer, UserImportSerializer, UserExportSerializer
)
from apps.core.pagination import StandardResultsSetPagination

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    自定义登录视图
    返回前端期望的统一格式
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # 获取用户信息
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = response.data['access']
            token = AccessToken(access_token)
            user_id = token['user_id']
            user = User.objects.get(id=user_id)
            user_serializer = UserProfileSerializer(user)
            
            return Response({
                'code': 200,
                'message': '登录成功',
                'data': {
                    'access': access_token,
                    'refresh': response.data['refresh'],
                    'user': user_serializer.data
                }
            })
        
        return response


class LogoutView(generics.GenericAPIView):
    """
    登出视图
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({
                'code': 200,
                'message': '登出成功'
            })
        except Exception:
            return Response({
                'code': 200,
                'message': '登出成功'
            })


class CurrentUserView(generics.RetrieveAPIView):
    """
    获取当前登录用户信息
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })


class ChangePasswordView(generics.GenericAPIView):
    """
    修改当前用户密码
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UserPasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'code': 200,
            'message': '密码修改成功'
        })


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集
    提供用户的CRUD操作
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_type', 'status', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'nickname', 'phone', 'department']
    ordering_fields = ['date_joined', 'last_login', 'username']
    ordering = ['-date_joined']
    lookup_field = 'pk'

    def get_serializer_class(self):
        """
        根据操作返回不同的序列化器
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'list':
            return UserListSerializer
        return UserSerializer

    def get_permissions(self):
        """
        根据操作设置不同的权限
        """
        if self.action in ['create', 'destroy', 'reset_password']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        根据用户权限过滤查询集
        """
        queryset = super().get_queryset()
        
        # 非管理员只能查看活跃用户
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        return queryset

    def perform_create(self, serializer):
        """
        创建用户时记录创建人
        """
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """
        更新用户时记录更新人
        """
        serializer.save(updated_by=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        获取当前登录用户信息
        """
        serializer = UserProfileSerializer(request.user)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        更新当前用户个人资料
        """
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        修改当前用户密码
        """
        serializer = UserPasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'success': True,
            'message': '密码修改成功'
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reset_password(self, request, pk=None):
        """
        重置用户密码（管理员功能）
        """
        user = self.get_object()
        serializer = UserPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'success': True,
            'message': f'用户 {user.username} 的密码已重置'
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_status(self, request, pk=None):
        """
        切换用户状态
        """
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        status_text = '激活' if user.is_active else '停用'
        return Response({
            'success': True,
            'message': f'用户 {user.username} 已{status_text}',
            'data': {'is_active': user.is_active}
        })

    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        """
        为用户分配角色
        """
        user = self.get_object()
        role_id = request.data.get('role_id')
        project_id = request.data.get('project_id')
        
        if not role_id:
            return Response({
                'success': False,
                'error': {'message': '请提供角色ID'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': '角色不存在'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 检查是否已分配
        if UserRole.objects.filter(
            user=user,
            role=role,
            project_id=project_id
        ).exists():
            return Response({
                'success': False,
                'error': {'message': '该角色已分配给用户'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user_role = UserRole.objects.create(
            user=user,
            role=role,
            project_id=project_id,
            assigned_by=request.user
        )
        
        serializer = UserRoleSerializer(user_role)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def remove_role(self, request, pk=None):
        """
        移除用户角色
        """
        user = self.get_object()
        role_id = request.data.get('role_id')
        project_id = request.data.get('project_id')
        
        try:
            user_role = UserRole.objects.get(
                user=user,
                role_id=role_id,
                project_id=project_id
            )
            user_role.delete()
            return Response({
                'success': True,
                'message': '角色已移除'
            })
        except UserRole.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': '用户没有该角色'}
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def import_users(self, request):
        """
        批量导入用户
        """
        serializer = UserImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file = serializer.validated_data['file']
        
        try:
            # 读取Excel文件
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            success_count = 0
            error_list = []
            
            for index, row in df.iterrows():
                try:
                    user_data = {
                        'username': str(row.get('用户名', '')).strip(),
                        'email': str(row.get('邮箱', '')).strip(),
                        'phone': str(row.get('手机号', '')).strip(),
                        'nickname': str(row.get('昵称', '')).strip(),
                        'department': str(row.get('部门', '')).strip(),
                        'position': str(row.get('职位', '')).strip(),
                        'user_type': str(row.get('用户类型', 'tester')).strip(),
                        'password': str(row.get('密码', 'SmartTest123!')),
                    }
                    
                    # 验证必填字段
                    if not user_data['username'] or not user_data['email']:
                        error_list.append({'row': index + 2, 'error': '用户名和邮箱不能为空'})
                        continue
                    
                    # 检查用户是否已存在
                    if User.objects.filter(username=user_data['username']).exists():
                        error_list.append({'row': index + 2, 'error': f'用户名 {user_data["username"]} 已存在'})
                        continue
                    
                    if User.objects.filter(email=user_data['email']).exists():
                        error_list.append({'row': index + 2, 'error': f'邮箱 {user_data["email"]} 已存在'})
                        continue
                    
                    # 创建用户
                    User.objects.create_user(**user_data)
                    success_count += 1
                    
                except Exception as e:
                    error_list.append({'row': index + 2, 'error': str(e)})
            
            return Response({
                'success': True,
                'data': {
                    'total': len(df),
                    'success_count': success_count,
                    'error_count': len(error_list),
                    'errors': error_list[:10]  # 只返回前10个错误
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {'message': f'文件解析失败: {str(e)}'}
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def export_users(self, request):
        """
        导出用户数据
        """
        serializer = UserExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        export_format = serializer.validated_data.get('format', 'xlsx')
        user_ids = serializer.validated_data.get('user_ids', [])
        
        # 构建查询集
        if user_ids:
            queryset = User.objects.filter(id__in=user_ids)
        else:
            queryset = User.objects.all()
        
        # 准备导出数据
        data = []
        for user in queryset:
            data.append({
                'ID': user.id,
                '用户名': user.username,
                '邮箱': user.email,
                '手机号': user.phone,
                '昵称': user.nickname,
                '部门': user.department,
                '职位': user.position,
                '用户类型': user.get_user_type_display(),
                '状态': user.get_status_display(),
                '注册时间': user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                '最后登录': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
            })
        
        df = pd.DataFrame(data)
        
        # 生成文件
        output = io.BytesIO()
        if export_format == 'xlsx':
            df.to_excel(output, index=False, engine='openpyxl')
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'users_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        elif export_format == 'csv':
            df.to_csv(output, index=False, encoding='utf-8-sig')
            content_type = 'text/csv'
            filename = f'users_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        else:  # json
            output.write(df.to_json(orient='records', force_ascii=False).encode('utf-8'))
            content_type = 'application/json'
            filename = f'users_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        output.seek(0)
        
        response = Response(
            output.getvalue(),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色管理视图集
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role_type', 'is_default']
    search_fields = ['name', 'code', 'description']

    def get_serializer_class(self):
        """
        根据操作返回不同的序列化器
        """
        if self.action in ['create', 'update', 'partial_update']:
            return RoleCreateUpdateSerializer
        return RoleSerializer

    def get_permissions(self):
        """
        角色管理需要管理员权限
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def set_default(self, request, pk=None):
        """
        设置默认角色
        """
        role = self.get_object()
        
        # 取消其他默认角色
        Role.objects.filter(is_default=True).update(is_default=False)
        
        role.is_default = True
        role.save()
        
        return Response({
            'success': True,
            'message': f'角色 {role.name} 已设置为默认角色'
        })


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    权限管理视图集（只读）
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'code', 'description']

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        按分类获取权限列表
        """
        categories = {}
        for category_code, category_name in Permission.PERMISSION_CATEGORIES:
            permissions = Permission.objects.filter(category=category_code)
            categories[category_code] = {
                'name': category_name,
                'permissions': PermissionSerializer(permissions, many=True).data
            }
        
        return Response({
            'success': True,
            'data': categories
        })


class UserLoginLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    用户登录日志视图集
    """
    queryset = UserLoginLog.objects.all()
    serializer_class = UserLoginLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['login_type', 'status', 'user']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        根据用户权限过滤日志
        """
        queryset = super().get_queryset()
        
        # 非管理员只能查看自己的登录日志
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取登录统计信息
        """
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = self.get_queryset().filter(created_at__gte=start_date)
        
        # 按状态统计
        status_stats = queryset.values('status').annotate(
            count=models.Count('id')
        )
        
        # 按登录类型统计
        type_stats = queryset.values('login_type').annotate(
            count=models.Count('id')
        )
        
        # 按日期统计
        daily_stats = queryset.extra(
            select={'date': "DATE(created_at)"}
        ).values('date').annotate(
            count=models.Count('id')
        ).order_by('date')
        
        return Response({
            'success': True,
            'data': {
                'status_statistics': list(status_stats),
                'type_statistics': list(type_stats),
                'daily_statistics': list(daily_stats),
                'total_count': queryset.count(),
            }
        })
