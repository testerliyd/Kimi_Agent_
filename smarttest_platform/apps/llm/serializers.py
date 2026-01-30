"""
大模型配置序列化器模块
"""
from rest_framework import serializers
from .models import LLMProvider, LLMConfig, LLMConversation, LLMMessage, LLMTestGeneration


class LLMProviderSerializer(serializers.ModelSerializer):
    """
    大模型提供商序列化器
    """
    class Meta:
        model = LLMProvider
        fields = [
            'id', 'code', 'name', 'description',
            'base_url', 'api_key_required', 'api_secret_required',
            'supported_models', 'is_active'
        ]


class LLMConfigListSerializer(serializers.ModelSerializer):
    """
    大模型配置列表序列化器
    """
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider_code = serializers.CharField(source='provider.code', read_only=True)
    api_key_masked = serializers.CharField(source='get_api_key_display', read_only=True)
    
    class Meta:
        model = LLMConfig
        fields = [
            'id', 'name', 'provider', 'provider_name', 'provider_code',
            'api_key_masked', 'default_model', 'is_default', 'is_active',
            'usage_count', 'last_used_at', 'created_at'
        ]


class LLMConfigDetailSerializer(serializers.ModelSerializer):
    """
    大模型配置详情序列化器
    """
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider_code = serializers.CharField(source='provider.code', read_only=True)
    
    class Meta:
        model = LLMConfig
        fields = [
            'id', 'name', 'provider', 'provider_name', 'provider_code',
            'api_key', 'api_secret', 'custom_base_url', 'default_model',
            'max_tokens', 'temperature', 'top_p',
            'is_default', 'is_active',
            'usage_count', 'last_used_at', 'created_at'
        ]
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True},
        }


class LLMConfigCreateUpdateSerializer(serializers.ModelSerializer):
    """
    大模型配置创建/更新序列化器
    """
    class Meta:
        model = LLMConfig
        fields = [
            'name', 'provider', 'api_key', 'api_secret',
            'custom_base_url', 'default_model',
            'max_tokens', 'temperature', 'top_p',
            'is_default', 'is_active'
        ]

    def validate_temperature(self, value):
        if not 0 <= value <= 2:
            raise serializers.ValidationError('Temperature必须在0-2之间')
        return value

    def validate_top_p(self, value):
        if not 0 <= value <= 1:
            raise serializers.ValidationError('Top P必须在0-1之间')
        return value


class LLMMessageSerializer(serializers.ModelSerializer):
    """
    大模型消息序列化器
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = LLMMessage
        fields = [
            'id', 'role', 'role_display', 'content',
            'prompt_tokens', 'completion_tokens', 'total_tokens',
            'response_time_ms', 'created_at'
        ]


class LLMConversationSerializer(serializers.ModelSerializer):
    """
    大模型对话序列化器
    """
    config_name = serializers.CharField(source='config.name', read_only=True)
    provider_name = serializers.CharField(source='config.provider.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = LLMConversation
        fields = [
            'id', 'title', 'config', 'config_name', 'provider_name',
            'project', 'project_name', 'message_count', 'token_usage',
            'last_message', 'created_at', 'updated_at'
        ]

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'role': last_msg.role,
                'content': last_msg.content[:100],
                'created_at': last_msg.created_at
            }
        return None


class LLMConversationDetailSerializer(serializers.ModelSerializer):
    """
    大模型对话详情序列化器
    """
    config_name = serializers.CharField(source='config.name', read_only=True)
    provider_name = serializers.CharField(source='config.provider.name', read_only=True)
    messages = LLMMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = LLMConversation
        fields = [
            'id', 'title', 'config', 'config_name', 'provider_name',
            'project', 'messages', 'message_count', 'token_usage',
            'created_at', 'updated_at'
        ]


class LLMChatRequestSerializer(serializers.Serializer):
    """
    大模型聊天请求序列化器
    """
    message = serializers.CharField(required=True, help_text='用户消息')
    conversation_id = serializers.IntegerField(required=False, allow_null=True)
    config_id = serializers.IntegerField(required=False, allow_null=True)
    context = serializers.JSONField(required=False, default=dict)


class LLMChatResponseSerializer(serializers.Serializer):
    """
    大模型聊天响应序列化器
    """
    message = serializers.CharField()
    conversation_id = serializers.IntegerField()
    tokens_used = serializers.IntegerField()
    response_time_ms = serializers.IntegerField()


class LLMTestGenerationSerializer(serializers.ModelSerializer):
    """
    AI生成测试序列化器
    """
    generation_type_display = serializers.CharField(source='get_generation_type_display', read_only=True)
    config_name = serializers.CharField(source='config.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = LLMTestGeneration
        fields = [
            'id', 'generation_type', 'generation_type_display',
            'config', 'config_name', 'project', 'project_name',
            'prompt', 'result', 'total_tokens', 'response_time_ms',
            'rating', 'feedback', 'created_at'
        ]


class LLMGenerateTestCaseSerializer(serializers.Serializer):
    """
    AI生成测试用例请求序列化器
    """
    config_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True)
    requirement = serializers.CharField(required=True, help_text='需求描述')
    context = serializers.JSONField(required=False, default=dict)


class LLMTestCaseResultSerializer(serializers.Serializer):
    """
    AI生成测试用例结果序列化器
    """
    test_cases = serializers.ListField(child=serializers.DictField())
    explanation = serializers.CharField()
    tokens_used = serializers.IntegerField()
