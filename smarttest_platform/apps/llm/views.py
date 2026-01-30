"""
大模型配置视图模块
"""
import time
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import LLMProvider, LLMConfig, LLMConversation, LLMMessage, LLMTestGeneration
from .serializers import (
    LLMProviderSerializer, LLMConfigListSerializer, LLMConfigDetailSerializer,
    LLMConfigCreateUpdateSerializer, LLMConversationSerializer, LLMConversationDetailSerializer,
    LLMMessageSerializer, LLMChatRequestSerializer, LLMChatResponseSerializer,
    LLMTestGenerationSerializer, LLMGenerateTestCaseSerializer
)
from .services import LLMService
from apps.core.pagination import StandardResultsSetPagination


class LLMProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    大模型提供商视图集（只读）
    """
    queryset = LLMProvider.objects.filter(is_active=True)
    serializer_class = LLMProviderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['code', 'api_key_required']
    ordering = ['name']


class LLMConfigViewSet(viewsets.ModelViewSet):
    """
    大模型配置视图集
    """
    serializer_class = LLMConfigDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['provider', 'is_default', 'is_active']
    search_fields = ['name']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        用户只能看到自己的配置
        """
        return LLMConfig.objects.filter(
            is_deleted=False,
            created_by=self.request.user
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return LLMConfigListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return LLMConfigCreateUpdateSerializer
        return LLMConfigDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        设置为默认配置
        """
        config = self.get_object()
        
        # 取消其他默认配置
        LLMConfig.objects.filter(created_by=request.user, is_default=True).update(is_default=False)
        
        config.is_default = True
        config.save()
        
        return Response({
            'success': True,
            'message': f'配置 {config.name} 已设置为默认'
        })

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """
        测试配置是否可用
        """
        config = self.get_object()
        
        try:
            service = LLMService(config)
            result = service.test_connection()
            
            return Response({
                'success': result['success'],
                'message': result['message'],
                'data': result.get('data')
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': {'message': f'测试失败: {str(e)}'}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LLMConversationViewSet(viewsets.ModelViewSet):
    """
    大模型对话视图集
    """
    serializer_class = LLMConversationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['config', 'project']
    search_fields = ['title']
    ordering = ['-updated_at']

    def get_queryset(self):
        return LLMConversation.objects.filter(
            is_deleted=False,
            created_by=self.request.user
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LLMConversationDetailSerializer
        return LLMConversationSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        """
        发送消息并获取回复
        """
        conversation = self.get_object()
        serializer = LLMChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message_content = serializer.validated_data['message']
        
        try:
            # 创建用户消息
            user_message = LLMMessage.objects.create(
                conversation=conversation,
                role='user',
                content=message_content,
                created_by=request.user
            )
            
            # 获取对话历史
            history = conversation.messages.order_by('created_at').values('role', 'content')
            messages = list(history)
            
            # 调用大模型服务
            start_time = time.time()
            service = LLMService(conversation.config)
            response = service.chat(messages)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # 创建助手消息
            assistant_message = LLMMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=response['content'],
                prompt_tokens=response.get('prompt_tokens', 0),
                completion_tokens=response.get('completion_tokens', 0),
                total_tokens=response.get('total_tokens', 0),
                response_time_ms=response_time_ms,
                created_by=request.user
            )
            
            # 更新对话统计
            conversation.message_count = conversation.messages.count()
            conversation.token_usage += response.get('total_tokens', 0)
            conversation.save()
            
            # 更新配置使用统计
            conversation.config.increment_usage()
            
            return Response({
                'success': True,
                'data': {
                    'message': response['content'],
                    'conversation_id': conversation.id,
                    'tokens_used': response.get('total_tokens', 0),
                    'response_time_ms': response_time_ms
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {'message': f'对话失败: {str(e)}'}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['delete'])
    def clear_history(self, request, pk=None):
        """
        清空对话历史
        """
        conversation = self.get_object()
        conversation.messages.all().delete()
        conversation.message_count = 0
        conversation.token_usage = 0
        conversation.save()
        
        return Response({
            'success': True,
            'message': '对话历史已清空'
        })


class LLMTestGenerationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    AI生成记录视图集（只读）
    """
    serializer_class = LLMTestGenerationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['generation_type', 'config', 'project']
    ordering = ['-created_at']

    def get_queryset(self):
        return LLMTestGeneration.objects.filter(
            is_deleted=False,
            created_by=self.request.user
        )

    @action(detail=False, methods=['post'])
    def generate_test_cases(self, request):
        """
        AI生成测试用例
        """
        serializer = LLMGenerateTestCaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            config = LLMConfig.objects.get(id=data['config_id'], created_by=request.user)
        except LLMConfig.DoesNotExist:
            return Response({
                'success': False,
                'error': {'message': '配置不存在'}
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 构建提示词
        prompt = f"""请根据以下需求生成测试用例：

需求描述：
{data['requirement']}

请生成详细的测试用例，包括：
1. 用例编号
2. 用例名称
3. 前置条件
4. 测试步骤
5. 预期结果

请以JSON格式返回，格式如下：
{{
    "test_cases": [
        {{
            "case_no": "TC001",
            "name": "测试用例名称",
            "preconditions": "前置条件",
            "steps": ["步骤1", "步骤2"],
            "expected_result": "预期结果"
        }}
    ],
    "explanation": "生成说明"
}}
"""
        
        try:
            start_time = time.time()
            service = LLMService(config)
            
            messages = [{'role': 'user', 'content': prompt}]
            response = service.chat(messages)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # 保存生成记录
            generation = LLMTestGeneration.objects.create(
                config=config,
                generation_type='testcase',
                prompt=prompt,
                context=data.get('context', {}),
                result=response['content'],
                project_id=data['project_id'],
                prompt_tokens=response.get('prompt_tokens', 0),
                completion_tokens=response.get('completion_tokens', 0),
                total_tokens=response.get('total_tokens', 0),
                response_time_ms=response_time_ms,
                created_by=request.user
            )
            
            # 更新配置使用统计
            config.increment_usage()
            
            return Response({
                'success': True,
                'data': {
                    'result': response['content'],
                    'generation_id': generation.id,
                    'tokens_used': response.get('total_tokens', 0),
                    'response_time_ms': response_time_ms
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {'message': f'生成失败: {str(e)}'}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """
        评价生成结果
        """
        generation = self.get_object()
        rating = request.data.get('rating')
        feedback = request.data.get('feedback', '')
        
        if rating is not None:
            generation.rating = rating
        generation.feedback = feedback
        generation.save()
        
        return Response({
            'success': True,
            'message': '评价已保存'
        })


class LLMChatViewSet(viewsets.ViewSet):
    """
    大模型聊天视图集
    提供快速聊天接口，无需创建对话
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def quick_chat(self, request):
        """
        快速聊天（不保存历史）
        """
        config_id = request.data.get('config_id')
        message = request.data.get('message')
        
        if not message:
            return Response({
                'success': False,
                'error': {'message': '请提供消息内容'}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取配置
        if config_id:
            try:
                config = LLMConfig.objects.get(id=config_id, created_by=request.user)
            except LLMConfig.DoesNotExist:
                return Response({
                    'success': False,
                    'error': {'message': '配置不存在'}
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # 使用默认配置
            config = LLMConfig.objects.filter(created_by=request.user, is_default=True).first()
            if not config:
                return Response({
                    'success': False,
                    'error': {'message': '没有可用的默认配置'}
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_time = time.time()
            service = LLMService(config)
            
            messages = [{'role': 'user', 'content': message}]
            response = service.chat(messages)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # 更新配置使用统计
            config.increment_usage()
            
            return Response({
                'success': True,
                'data': {
                    'message': response['content'],
                    'tokens_used': response.get('total_tokens', 0),
                    'response_time_ms': response_time_ms
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {'message': f'对话失败: {str(e)}'}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
