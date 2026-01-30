"""
性能测试URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'scenarios', views.PerfTestScenarioViewSet, basename='perf-scenario')
router.register(r'jobs', views.PerfTestJobViewSet, basename='perf-job')
router.register(r'metrics', views.PerfTestMetricsViewSet, basename='perf-metrics')

urlpatterns = [
    path('', include(router.urls)),
]
