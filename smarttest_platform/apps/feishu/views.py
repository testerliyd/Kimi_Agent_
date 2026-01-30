"""
飞书机器人视图模块
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import FeishuConfig, FeishuMessageTemplate, FeishuNotificationLog, FeishuChatBinding
from .serializers import (
    FeishuConfigListSerializer, FeishuConfigDetailSerializer, FeishuConfigCreateUpdateSerializer,
    FeishuMessageTemplateSerializer, FeishuNotificationLogSerializer,
    FeishuChatBindingSerializer, FeishuSendMessageSerializer, FeishuWebhookSerializer
)
from .services import FeishuService
from apps.core.pagination import StandardResultsSetPagination


class FeishuConfigViewSet(viewsets.ModelViewSet):
    """
    飞书配置视图集
    """
    serializer_class = FeishuConfigDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_default', 'is_active']
    search_fields = ['name', 'app_id']
    ordering = ['-created_at']

    def get_queryset(self):
        return FeishuConfig.objects.filter(
            is_deleted=False,
            created_by=self.request.user
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return FeishuConfigListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return FeishuConfigCreateUpdateSerializer
        return FeishuConfigDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        设置为默认配置
        """
        config = self.get_object()
        
        FeishuConfig.objects.filter(created_by=request.user, is_default=True).update(is_default=False)
        
        config.is_default = True
        config.save()
        
        return Response({
            'success': True,
            'message': f'配置 {config.name} 已设置为默认'
        })

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """
        测试配置
        支持Webhook方式和App API方式
        """
        config = self.get_object()
        
        try:
            service = FeishuService(config)
            result = service.test_connection()
            
            if result['success']:
                return Response({
                    'success': True,
                    'message': result['message'],
                    'data': result.get('data')
                })
            else:
                return Response({
                    'success': False,
                    'error': {'message': result['message']}
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': {'message': f'配置测试失败: {str(e)}'}
            }, status=status.HTTP_400_BAD_REQUEST)


class FeishuMessageTemplateViewSet(viewsets.ModelViewSet):
    """
    飞书消息模板视图集
    """
    queryset = FeishuMessageTemplate.objects.filter(is_deleted=False)
    serializer_class = FeishuMessageTemplateSerializer
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


class FeishuNotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    飞书通知日志视图集（只读）
    """
    serializer_class = FeishuNotificationLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'message_type', 'config']
    ordering = ['-created_at']

    def get_queryset(self):
        return FeishuNotificationLog.objects.filter(
            is_deleted=False,
            created_by=self.request.user
        )


class FeishuChatBindingViewSet(viewsets.ModelViewSet):
    """
    飞书群聊绑定视图集
    """
    serializer_class = FeishuChatBindingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'config']
    ordering = ['-created_at']

    def get_queryset(self):
        return FeishuChatBinding.objects.filter(
            is_deleted=False,
            created_by=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class FeishuWebhookViewSet(viewsets.ViewSet):
    """
    飞书Webhook视图集
    处理飞书机器人回调
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @action(detail=False, methods=['post'])
    def callback(self, request):
        """
        处理飞书回调
        """
        serializer = FeishuWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # 处理URL验证
        if data.get('type') == 'url_verification':
            return Response({
                'challenge': data.get('challenge')
            })
        
        # 处理事件
        event = data.get('event', {})
        event_type = event.get('type')
        
        # 处理消息事件
        if event_type == 'message':
            self._handle_message_event(event)
        
        return Response({'success': True})

    def _handle_message_event(self, event):
        """
        处理消息事件
        """
        message_type = event.get('msg_type')
        content = event.get('text', '')
        chat_id = event.get('open_chat_id')
        
        # 简单的命令处理
        if content.startswith('/test'):
            service = FeishuService()
            service.send_text_message(chat_id, '测试平台已收到您的消息！')

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def send_message(self, request):
        """
        发送消息到飞书
        """
        serializer = FeishuSendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # 获取配置
        config_id = data.get('config_id')
        if config_id:
            try:
                config = FeishuConfig.objects.get(id=config_id, created_by=request.user)
            except FeishuConfig.DoesNotExist:
                return Response({
                    'success': False,
                    'error': {'message': '配置不存在'}
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            config = FeishuConfig.objects.filter(created_by=request.user, is_default=True).first()
        
        if not config:
            return Response({
                'success': False,
                'error': {'message': '没有可用的飞书配置'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取群聊ID
        chat_id = data.get('chat_id') or config.default_chat_id
        
        if not chat_id:
            return Response({
                'success': False,
                'error': {'message': '请提供群聊ID'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 发送消息
        service = FeishuService(config)
        
        try:
            # 优先使用Webhook方式（如果配置了webhook_url）
            if config.webhook_url:
                if data['message_type'] == 'text':
                    result = service.send_webhook_text(data['content'])
                else:
                    # 卡片消息
                    result = service.send_webhook_card(data['content'])
            else:
                # 使用App API方式
                if not chat_id:
                    return Response({
                        'success': False,
                        'error': {'message': '未配置Webhook URL，请提供群聊ID'}
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if data['message_type'] == 'text':
                    result = service.send_text_message(chat_id, data['content'])
                else:
                    # 卡片消息
                    result = service.send_card_message(chat_id, data['content'])
            
            # 记录日志
            FeishuNotificationLog.objects.create(
                config=config,
                message_type=data['message_type'],
                chat_id=chat_id or '',
                content={'text': data['content']},
                status='success' if result.get('code') == 0 else 'failed',
                response_data=result,
                created_by=request.user
            )
            
            return Response({
                'success': True,
                'data': result
            })
            
        except Exception as e:
            # 记录失败日志
            FeishuNotificationLog.objects.create(
                config=config,
                message_type=data['message_type'],
                chat_id=chat_id or '',
                content={'text': data['content']},
                status='failed',
                error_message=str(e),
                created_by=request.user
            )
            
            return Response({
                'success': False,
                'error': {'message': f'发送失败: {str(e)}'}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
