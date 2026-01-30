"""
核心应用URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'audit-logs', views.AuditLogViewSet, basename='audit-log')
router.register(r'system-configs', views.SystemConfigViewSet, basename='system-config')
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('stats/', views.SystemStatsView.as_view(), name='system-stats'),
]
