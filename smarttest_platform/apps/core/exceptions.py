"""
异常处理模块
自定义异常类和全局异常处理器
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.utils.translation import gettext_lazy as _


class SmartTestException(APIException):
    """
    平台基础异常类
    所有自定义异常都应继承此类
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('服务器内部错误')
    default_code = 'internal_error'

    def __init__(self, detail=None, code=None, status_code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail, code)


class ValidationError(SmartTestException):
    """
    数据验证错误
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('数据验证失败')
    default_code = 'validation_error'


class AuthenticationFailed(SmartTestException):
    """
    认证失败
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('认证失败')
    default_code = 'authentication_failed'


class PermissionDenied(SmartTestException):
    """
    权限不足
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _('权限不足')
    default_code = 'permission_denied'


class NotFound(SmartTestException):
    """
    资源不存在
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('资源不存在')
    default_code = 'not_found'


class Conflict(SmartTestException):
    """
    资源冲突
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('资源冲突')
    default_code = 'conflict'


class RateLimitExceeded(SmartTestException):
    """
    请求频率超限
    """
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = _('请求过于频繁，请稍后重试')
    default_code = 'rate_limit_exceeded'


class ServiceUnavailable(SmartTestException):
    """
    服务不可用
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('服务暂时不可用')
    default_code = 'service_unavailable'


class BusinessError(SmartTestException):
    """
    业务逻辑错误
    用于处理特定的业务规则违反
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = _('业务逻辑错误')
    default_code = 'business_error'


class ExternalServiceError(SmartTestException):
    """
    外部服务调用错误
    """
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = _('外部服务调用失败')
    default_code = 'external_service_error'


class TestExecutionError(SmartTestException):
    """
    测试执行错误
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = _('测试执行失败')
    default_code = 'test_execution_error'


class LLMError(SmartTestException):
    """
    大模型调用错误
    """
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = _('大模型服务调用失败')
    default_code = 'llm_error'


class FeishuError(SmartTestException):
    """
    飞书API调用错误
    """
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = _('飞书服务调用失败')
    default_code = 'feishu_error'


def custom_exception_handler(exc, context):
    """
    自定义异常处理器
    统一处理所有异常，返回标准格式的错误响应
    """
    # 先调用DRF默认的异常处理器
    response = exception_handler(exc, context)
    
    if response is not None:
        # 获取错误详情
        error_detail = response.data
        
        # 构建标准错误响应格式
        error_response = {
            'success': False,
            'error': {
                'code': getattr(exc, 'code', 'unknown_error'),
                'message': get_error_message(error_detail),
                'status_code': response.status_code,
                'details': error_detail if isinstance(error_detail, dict) else None,
            }
        }
        
        response.data = error_response
    else:
        # 处理未捕获的异常
        import traceback
        import logging
        
        logger = logging.getLogger('apps')
        logger.error(f"未捕获的异常: {str(exc)}")
        logger.error(traceback.format_exc())
        
        # 在生产环境不暴露详细错误信息
        from django.conf import settings
        if not settings.DEBUG:
            from rest_framework.response import Response
            response = Response({
                'success': False,
                'error': {
                    'code': 'internal_error',
                    'message': '服务器内部错误',
                    'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'details': None,
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


def get_error_message(error_detail):
    """
    从错误详情中提取错误信息
    """
    if isinstance(error_detail, dict):
        # 处理字段级错误
        if 'detail' in error_detail:
            return error_detail['detail']
        # 处理验证错误
        if len(error_detail) > 0:
            first_key = list(error_detail.keys())[0]
            first_error = error_detail[first_key]
            if isinstance(first_error, list):
                return first_error[0]
            return str(first_error)
    elif isinstance(error_detail, list):
        return error_detail[0] if error_detail else '未知错误'
    
    return str(error_detail) if error_detail else '未知错误'
