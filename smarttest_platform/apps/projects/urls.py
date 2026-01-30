"""
项目管理URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.ProjectViewSet, basename='project')
router.register(r'versions', views.ProjectVersionViewSet, basename='project-version')
router.register(r'milestones', views.ProjectMilestoneViewSet, basename='project-milestone')
router.register(r'environments', views.ProjectEnvironmentViewSet, basename='project-environment')
router.register(r'members', views.ProjectMemberViewSet, basename='project-member')

urlpatterns = [
    path('', include(router.urls)),
]
