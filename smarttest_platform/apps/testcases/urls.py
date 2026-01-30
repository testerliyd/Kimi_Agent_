"""
用例管理URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cases', views.TestCaseViewSet, basename='testcase')
router.register(r'suites', views.TestSuiteViewSet, basename='testsuite')
router.register(r'plans', views.TestPlanViewSet, basename='testplan')
router.register(r'tags', views.TestCaseTagViewSet, basename='testcase-tag')
router.register(r'categories', views.TestCaseCategoryViewSet, basename='testcase-category')

urlpatterns = [
    path('', include(router.urls)),
]
