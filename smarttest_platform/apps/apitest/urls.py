"""
接口测试URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'definitions', views.ApiDefinitionViewSet, basename='api-definition')
router.register(r'cases', views.ApiTestCaseViewSet, basename='api-test-case')
router.register(r'jobs', views.ApiTestJobViewSet, basename='api-test-job')
router.register(r'results', views.ApiTestResultViewSet, basename='api-test-result')

urlpatterns = [
    path('', include(router.urls)),
]
