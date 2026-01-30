"""
中间件模块
自定义中间件用于请求日志记录、性能监控等
"""
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

logger = logging.getLogger('apps')


class RequestLogMiddleware(MiddlewareMixin):
    """
    请求日志中间件
    记录所有API请求的详细信息
    """
    
    def process_request(self, request):
        """
        处理请求开始
        """
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """
        处理响应结束，记录日志
        """
        # 计算请求耗时
        duration = time.time() - getattr(request, 'start_time', time.time())
        
        # 只记录API请求
        if request.path.startswith('/api/'):
            log_data = {
                'timestamp': timezone.now().isoformat(),
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.GET),
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'user_id': getattr(request.user, 'id', None),
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
            
            # 根据状态码选择日志级别
            if response.status_code >= 500:
                logger.error(f"API请求错误: {log_data}")
            elif response.status_code >= 400:
                logger.warning(f"API请求警告: {log_data}")
            else:
                logger.info(f"API请求: {log_data}")
        
        # 添加响应头
        response['X-Request-Duration'] = str(round(duration * 1000, 2))
        
        return response
    
    def get_client_ip(self, request):
        """
        获取客户端真实IP地址
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip


class PerformanceMonitorMiddleware(MiddlewareMixin):
    """
    性能监控中间件
    监控请求处理时间和数据库查询次数
    """
    
    def process_request(self, request):
        """
        请求开始处理
        """
        request._start_time = time.time()
        request._query_count_start = len(request.META.get('queries', []))
        return None
    
    def process_response(self, request, response):
        """
        响应处理完成
        """
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # 慢请求警告（超过1秒）
            if duration > 1.0:
                logger.warning(
                    f"慢请求警告: {request.method} {request.path} "
                    f"耗时: {round(duration * 1000, 2)}ms"
                )
            
            # 添加性能监控头
            response['X-Response-Time'] = f"{round(duration * 1000, 2)}ms"
        
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    安全响应头中间件
    添加安全相关的HTTP响应头
    """
    
    def process_response(self, request, response):
        """
        添加安全响应头
        """
        # 防止点击劫持
        response['X-Frame-Options'] = 'DENY'
        
        # XSS保护
        response['X-XSS-Protection'] = '1; mode=block'
        
        # 内容类型嗅探保护
        response['X-Content-Type-Options'] = 'nosniff'
        
        # 引用策略
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # 内容安全策略（基础配置）
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self';"
        )
        
        return response


class CORSMiddleware(MiddlewareMixin):
    """
    自定义CORS中间件
    处理跨域请求
    """
    
    def process_request(self, request):
        """
        处理预检请求
        """
        if request.method == 'OPTIONS':
            response = self.get_response(request)
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response['Access-Control-Max-Age'] = '86400'
            return response
        return None
    
    def process_response(self, request, response):
        """
        添加CORS响应头
        """
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
