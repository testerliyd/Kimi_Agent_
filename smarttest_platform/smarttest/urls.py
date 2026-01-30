"""
SmartTest URL配置
主路由配置，包含所有应用的路由
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# API文档配置
schema_view = get_schema_view(
    openapi.Info(
        title="SmartTest API",
        default_version='v1',
        description="""
        智能化测试平台API文档
        
        ## 功能模块
        - 用户管理：用户注册、登录、权限管理
        - 项目管理：项目创建、成员管理
        - 用例管理：测试用例的CRUD操作
        - Bug管理：缺陷跟踪、状态流转
        - 接口测试：API自动化测试
        - 性能测试：负载测试、压力测试
        - 大模型配置：多厂商LLM API管理
        - 飞书集成：机器人通知、报告推送
        """,
        terms_of_service="https://www.smarttest.com/terms/",
        contact=openapi.Contact(email="support@smarttest.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # 管理后台
    path('admin/', admin.site.urls),
    
    # API认证
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API文档
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # 应用API路由
    path('api/users/', include('apps.users.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/testcases/', include('apps.testcases.urls')),
    path('api/bugs/', include('apps.bugs.urls')),
    path('api/apitest/', include('apps.apitest.urls')),
    path('api/perftest/', include('apps.perftest.urls')),
    path('api/llm/', include('apps.llm.urls')),
    path('api/feishu/', include('apps.feishu.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/core/', include('apps.core.urls')),
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
