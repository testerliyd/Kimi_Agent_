"""
报告管理URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.ReportTemplateViewSet, basename='report-template')
router.register(r'', views.ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
