"""
用户管理URL配置
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'', views.UserViewSet, basename='user')
router.register(r'roles', views.RoleViewSet, basename='role')
router.register(r'permissions', views.PermissionViewSet, basename='permission')
router.register(r'login-logs', views.UserLoginLogViewSet, basename='login-log')

urlpatterns = [
    path('', include(router.urls)),
    # 认证相关端点
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'),
    path('auth/me/', views.CurrentUserView.as_view(), name='auth_me'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='auth_change_password'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth_logout'),
]
