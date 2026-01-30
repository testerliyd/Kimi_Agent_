"""
分页模块
自定义分页类和分页工具函数
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    标准分页类
    提供统一的分页格式
    """
    page_size = 20  # 默认每页数量
    page_size_query_param = 'page_size'  # 允许客户端指定每页数量
    max_page_size = 100  # 最大每页数量
    page_query_param = 'page'  # 页码参数名

    def get_paginated_response(self, data):
        """
        自定义分页响应格式
        """
        return Response({
            'success': True,
            'data': {
                'results': data,
                'pagination': {
                    'page': self.page.number,
                    'page_size': self.get_page_size(self.request),
                    'total': self.page.paginator.count,
                    'total_pages': self.page.paginator.num_pages,
                    'has_next': self.page.has_next(),
                    'has_previous': self.page.has_previous(),
                }
            }
        })


class LargeResultsSetPagination(PageNumberPagination):
    """
    大数据量分页类
    适用于需要展示大量数据的场景
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'data': {
                'results': data,
                'pagination': {
                    'page': self.page.number,
                    'page_size': self.get_page_size(self.request),
                    'total': self.page.paginator.count,
                    'total_pages': self.page.paginator.num_pages,
                    'has_next': self.page.has_next(),
                    'has_previous': self.page.has_previous(),
                }
            }
        })


class SmallResultsSetPagination(PageNumberPagination):
    """
    小数据量分页类
    适用于展示少量数据的场景，如下拉列表
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'data': {
                'results': data,
                'pagination': {
                    'page': self.page.number,
                    'page_size': self.get_page_size(self.request),
                    'total': self.page.paginator.count,
                    'total_pages': self.page.paginator.num_pages,
                    'has_next': self.page.has_next(),
                    'has_previous': self.page.has_previous(),
                }
            }
        })


def paginate_queryset(queryset, request, paginator_class=StandardResultsSetPagination):
    """
    分页查询集的便捷函数
    
    Args:
        queryset: 需要分页的查询集
        request: HTTP请求对象
        paginator_class: 分页类，默认使用StandardResultsSetPagination
    
    Returns:
        tuple: (paginated_data, pagination_info)
    """
    paginator = paginator_class()
    page = paginator.paginate_queryset(queryset, request)
    
    if page is not None:
        return page, {
            'page': paginator.page.number,
            'page_size': paginator.get_page_size(request),
            'total': paginator.page.paginator.count,
            'total_pages': paginator.page.paginator.num_pages,
            'has_next': paginator.page.has_next(),
            'has_previous': paginator.page.has_previous(),
        }
    
    return queryset, None
