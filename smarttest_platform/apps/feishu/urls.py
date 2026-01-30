"""
飞书机器人URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'configs', views.FeishuConfigViewSet, basename='feishu-config')
router.register(r'templates', views.FeishuMessageTemplateViewSet, basename='feishu-template')
router.register(r'logs', views.FeishuNotificationLogViewSet, basename='feishu-log')
router.register(r'bindings', views.FeishuChatBindingViewSet, basename='feishu-binding')
router.register(r'webhook', views.FeishuWebhookViewSet, basename='feishu-webhook')

urlpatterns = [
    path('', include(router.urls)),
]
