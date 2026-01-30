"""
飞书机器人序列化器模块
"""
from rest_framework import serializers
from .models import FeishuConfig, FeishuMessageTemplate, FeishuNotificationLog, FeishuChatBinding


class FeishuConfigListSerializer(serializers.ModelSerializer):
    """
    飞书配置列表序列化器
    """
    class Meta:
        model = FeishuConfig
        fields = ['id', 'name', 'app_id', 'is_default', 'is_active', 'created_at']


class FeishuConfigDetailSerializer(serializers.ModelSerializer):
    """
    飞书配置详情序列化器
    """
    class Meta:
        model = FeishuConfig
        fields = [
            'id', 'name', 'app_id', 'app_secret',
            'verification_token', 'encrypt_key', 'webhook_url',
            'default_chat_id', 'is_default', 'is_active', 'created_at'
        ]
        extra_kwargs = {
            'app_secret': {'write_only': True},
            'encrypt_key': {'write_only': True},
        }


class FeishuConfigCreateUpdateSerializer(serializers.ModelSerializer):
    """
    飞书配置创建/更新序列化器
    """
    class Meta:
        model = FeishuConfig
        fields = [
            'name', 'app_id', 'app_secret',
            'verification_token', 'encrypt_key', 'webhook_url',
            'default_chat_id', 'is_default', 'is_active'
        ]


class FeishuMessageTemplateSerializer(serializers.ModelSerializer):
    """
    飞书消息模板序列化器
    """
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    
    class Meta:
        model = FeishuMessageTemplate
        fields = [
            'id', 'name', 'template_type', 'template_type_display',
            'description', 'template_content', 'variables',
            'is_default', 'is_active', 'created_at'
        ]


class FeishuNotificationLogSerializer(serializers.ModelSerializer):
    """
    飞书通知日志序列化器
    """
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    config_name = serializers.CharField(source='config.name', read_only=True)
    
    class Meta:
        model = FeishuNotificationLog
        fields = [
            'id', 'config', 'config_name', 'message_type', 'message_type_display',
            'chat_id', 'user_id', 'content', 'related_object_type',
            'related_object_id', 'status', 'status_display',
            'error_message', 'created_at'
        ]


class FeishuChatBindingSerializer(serializers.ModelSerializer):
    """
    飞书群聊绑定序列化器
    """
    project_name = serializers.CharField(source='project.name', read_only=True)
    config_name = serializers.CharField(source='config.name', read_only=True)
    
    class Meta:
        model = FeishuChatBinding
        fields = [
            'id', 'project', 'project_name', 'chat_id', 'chat_name',
            'notify_bug_created', 'notify_bug_status_change', 'notify_test_completed',
            'config', 'config_name', 'created_at'
        ]


class FeishuSendMessageSerializer(serializers.Serializer):
    """
    发送飞书消息序列化器
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', '文本消息'),
        ('card', '卡片消息'),
    ]
    
    config_id = serializers.IntegerField(required=False, allow_null=True)
    chat_id = serializers.CharField(required=False, allow_blank=True)
    message_type = serializers.ChoiceField(choices=MESSAGE_TYPE_CHOICES, default='text')
    content = serializers.CharField(required=True)
    template_id = serializers.IntegerField(required=False, allow_null=True)
    template_variables = serializers.JSONField(required=False, default=dict)


class FeishuWebhookSerializer(serializers.Serializer):
    """
    飞书Webhook序列化器
    """
    timestamp = serializers.CharField(required=False, allow_blank=True)
    sign = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True)
    challenge = serializers.CharField(required=False, allow_blank=True)
    token = serializers.CharField(required=False, allow_blank=True)
    event = serializers.JSONField(required=False, default=dict)
