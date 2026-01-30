"""
大模型配置URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'providers', views.LLMProviderViewSet, basename='llm-provider')
router.register(r'configs', views.LLMConfigViewSet, basename='llm-config')
router.register(r'conversations', views.LLMConversationViewSet, basename='llm-conversation')
router.register(r'generations', views.LLMTestGenerationViewSet, basename='llm-generation')
router.register(r'chat', views.LLMChatViewSet, basename='llm-chat')

urlpatterns = [
    path('', include(router.urls)),
]
