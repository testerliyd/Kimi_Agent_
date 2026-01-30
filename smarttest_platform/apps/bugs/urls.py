"""
Bug管理URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.BugViewSet, basename='bug')
router.register(r'comments', views.BugCommentViewSet, basename='bug-comment')
router.register(r'history', views.BugHistoryViewSet, basename='bug-history')
router.register(r'tags', views.BugTagViewSet, basename='bug-tag')
router.register(r'categories', views.BugCategoryViewSet, basename='bug-category')

urlpatterns = [
    path('', include(router.urls)),
]
