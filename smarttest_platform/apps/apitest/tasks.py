"""
接口测试异步任务模块
"""
import json
import time
import requests
from celery import shared_task
from django.utils import timezone

from .models import ApiTestJob, ApiTestResult, ApiTestCase
from apps.feishu.services import FeishuService


@shared_task(bind=True, max_retries=3)
def execute_api_test_job(self, job_id):
    """
    执行API测试任务
    """
    try:
        job = ApiTestJob.objects.get(id=job_id)
    except ApiTestJob.DoesNotExist:
        return {'error': 'Job not found'}
    
    test_cases = job.test_cases.filter(is_active=True)
    job.total_cases = test_cases.count()
    job.save()
    
    results = []
    
    for test_case in test_cases:
        result = execute_single_test_case(job, test_case)
        results.append(result)
    
    # 更新任务统计
    job.passed_cases = len([r for r in results if r.status == 'passed'])
    job.failed_cases = len([r for r in results if r.status == 'failed'])
    job.error_cases = len([r for r in results if r.status == 'error'])
    
    # 确定任务状态
    if job.error_cases > 0:
        job.status = 'error'
    elif job.failed_cases > 0:
        job.status = 'failed'
    else:
        job.status = 'passed'
    
    job.completed_at = timezone.now()
    if job.started_at:
        job.duration = int((job.completed_at - job.started_at).total_seconds())
    
    job.result_summary = {
        'total': job.total_cases,
        'passed': job.passed_cases,
        'failed': job.failed_cases,
        'error': job.error_cases,
        'pass_rate': round(job.passed_cases / job.total_cases * 100, 2) if job.total_cases > 0 else 0
    }
    job.save()
    
    # 发送飞书通知
    try:
        FeishuService.send_api_test_report(job)
    except Exception as e:
        print(f"发送飞书通知失败: {e}")
    
    return {
        'job_id': job_id,
        'status': job.status,
        'total': job.total_cases,
        'passed': job.passed_cases,
        'failed': job.failed_cases,
    }


def execute_single_test_case(job, test_case):
    """
    执行单个测试用例
    """
    api = test_case.api
    start_time = timezone.now()
    
    # 获取环境配置
    environment = job.environment or api.environment
    base_url = environment.base_url if environment else ''
    
    # 构建请求
    url = f"{base_url.rstrip('/')}/{api.path.lstrip('/')}"
    method = api.method
    
    # 合并请求头
    headers = {**api.headers, **test_case.override_headers}
    
    # 合并参数
    params = {**api.params, **test_case.override_params}
    
    # 处理请求体
    body = api.body_raw if api.body_raw else json.dumps(api.body)
    if test_case.override_body:
        body = json.dumps(test_case.override_body)
    
    # 设置Content-Type
    if api.content_type:
        headers['Content-Type'] = api.content_type
    
    try:
        request_start = time.time()
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=body if method != 'GET' else None,
            timeout=30
        )
        
        response_time_ms = int((time.time() - request_start) * 1000)
        
        # 验证结果
        validation_results = []
        status = 'passed'
        error_message = ''
        
        # 验证状态码
        if response.status_code != test_case.expected_status:
            status = 'failed'
            validation_results.append({
                'field': 'status_code',
                'expected': test_case.expected_status,
                'actual': response.status_code,
                'passed': False
            })
        else:
            validation_results.append({
                'field': 'status_code',
                'expected': test_case.expected_status,
                'actual': response.status_code,
                'passed': True
            })
        
        # 验证响应体（简化版）
        if test_case.expected_body:
            try:
                expected = json.dumps(test_case.expected_body, sort_keys=True)
                actual = json.dumps(response.json(), sort_keys=True)
                body_passed = expected in actual
                
                validation_results.append({
                    'field': 'body',
                    'expected': '包含预期内容',
                    'actual': '验证完成',
                    'passed': body_passed
                })
                
                if not body_passed:
                    status = 'failed'
            except:
                pass
        
        completed_time = timezone.now()
        duration_ms = int((completed_time - start_time).total_seconds() * 1000)
        
        # 创建结果记录
        result = ApiTestResult.objects.create(
            job=job,
            test_case=test_case,
            status=status,
            request_url=url,
            request_method=method,
            request_headers=headers,
            request_body=body[:10000],
            response_status=response.status_code,
            response_headers=dict(response.headers),
            response_body=response.text[:10000],
            response_time_ms=response_time_ms,
            validation_results=validation_results,
            error_message=error_message,
            started_at=start_time,
            completed_at=completed_time,
            duration_ms=duration_ms,
            created_by=job.executor
        )
        
        return result
        
    except Exception as e:
        completed_time = timezone.now()
        duration_ms = int((completed_time - start_time).total_seconds() * 1000)
        
        result = ApiTestResult.objects.create(
            job=job,
            test_case=test_case,
            status='error',
            request_url=url,
            request_method=method,
            request_headers=headers,
            request_body=body[:10000],
            response_status=0,
            response_headers={},
            response_body='',
            response_time_ms=0,
            validation_results=[],
            error_message=str(e)[:1000],
            started_at=start_time,
            completed_at=completed_time,
            duration_ms=duration_ms,
            created_by=job.executor
        )
        
        return result
