"""
性能测试异步任务模块
"""
import time
import random
import statistics
from datetime import datetime, timedelta
from celery import shared_task
from django.utils import timezone

from .models import PerfTestJob, PerfTestMetrics
from apps.feishu.services import FeishuService


@shared_task(bind=True, max_retries=3)
def execute_perf_test_job(self, job_id):
    """
    执行性能测试任务
    使用Locust框架进行负载测试
    """
    try:
        job = PerfTestJob.objects.get(id=job_id)
        scenario = job.scenario
    except PerfTestJob.DoesNotExist:
        return {'error': 'Job not found'}
    
    # 获取测试参数
    concurrent_users = job.concurrent_users or scenario.concurrent_users
    test_duration = job.test_duration or scenario.test_duration
    ramp_up_time = scenario.ramp_up_time
    
    # 更新状态
    job.status = 'running'
    job.save()
    
    try:
        # 模拟性能测试执行
        # 实际项目中应使用Locust或其他性能测试工具
        results = simulate_load_test(
            target_url=scenario.target_url,
            method=scenario.http_method,
            headers=scenario.headers,
            body=scenario.body,
            concurrent_users=concurrent_users,
            test_duration=test_duration,
            ramp_up_time=ramp_up_time,
            job=job
        )
        
        # 更新任务结果
        job.total_requests = results['total_requests']
        job.avg_response_time = results['avg_response_time']
        job.min_response_time = results['min_response_time']
        job.max_response_time = results['max_response_time']
        job.error_rate = results['error_rate']
        job.requests_per_second = results['requests_per_second']
        
        # 判断是否通过标准
        success_criteria = scenario.success_criteria
        passed = True
        
        if success_criteria:
            if 'avg_response_time' in success_criteria:
                passed = passed and (job.avg_response_time <= success_criteria['avg_response_time'])
            if 'error_rate' in success_criteria:
                passed = passed and (job.error_rate <= success_criteria['error_rate'])
        
        job.passed_criteria = passed
        job.status = 'passed' if passed else 'failed'
        job.completed_at = timezone.now()
        
        # 生成报告数据
        job.report_data = {
            'summary': results,
            'criteria': success_criteria,
            'passed': passed,
        }
        
        job.save()
        
        # 发送飞书通知
        try:
            FeishuService.send_perf_test_report(job)
        except Exception as e:
            print(f"发送飞书通知失败: {e}")
        
        return {
            'job_id': job_id,
            'status': job.status,
            'avg_response_time': job.avg_response_time,
            'error_rate': job.error_rate,
        }
        
    except Exception as e:
        job.status = 'error'
        job.completed_at = timezone.now()
        job.save()
        
        return {'error': str(e)}


def simulate_load_test(target_url, method, headers, body, concurrent_users, test_duration, ramp_up_time, job):
    """
    模拟负载测试
    实际项目中应使用Locust或其他性能测试工具
    """
    import requests
    
    total_requests = 0
    failed_requests = 0
    response_times = []
    
    start_time = time.time()
    metrics_data = []
    
    # 模拟测试执行
    while time.time() - start_time < test_duration:
        current_time = time.time() - start_time
        
        # 计算当前并发用户数（渐进式增加）
        if current_time < ramp_up_time:
            current_users = int(concurrent_users * (current_time / ramp_up_time))
        else:
            current_users = concurrent_users
        
        # 模拟请求
        for _ in range(current_users):
            try:
                request_start = time.time()
                
                # 模拟请求延迟
                delay = random.uniform(0.05, 0.5)
                time.sleep(delay)
                
                # 模拟响应时间
                response_time = random.gauss(200, 50)  # 平均200ms，标准差50ms
                response_time = max(10, response_time)  # 最小10ms
                
                response_times.append(response_time)
                total_requests += 1
                
                # 模拟错误（1%的错误率）
                if random.random() < 0.01:
                    failed_requests += 1
                
            except Exception as e:
                failed_requests += 1
        
        # 每5秒记录一次指标
        if int(current_time) % 5 == 0:
            if response_times:
                metrics_data.append({
                    'timestamp': timezone.now(),
                    'total_requests': total_requests,
                    'failed_requests': failed_requests,
                    'avg_response_time': statistics.mean(response_times[-100:]) if len(response_times) >= 100 else statistics.mean(response_times),
                    'min_response_time': min(response_times[-100:]) if len(response_times) >= 100 else min(response_times),
                    'max_response_time': max(response_times[-100:]) if len(response_times) >= 100 else max(response_times),
                    'p50_response_time': statistics.median(response_times[-100:]) if len(response_times) >= 100 else statistics.median(response_times),
                    'p95_response_time': sorted(response_times[-100:])[int(len(response_times[-100:]) * 0.95)] if len(response_times) >= 100 else sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0,
                    'p99_response_time': sorted(response_times[-100:])[int(len(response_times[-100:]) * 0.99)] if len(response_times) >= 100 else sorted(response_times)[int(len(response_times) * 0.99)] if response_times else 0,
                    'requests_per_second': total_requests / (time.time() - start_time) if time.time() - start_time > 0 else 0,
                    'bytes_per_second': random.randint(1000, 10000),
                    'current_users': current_users,
                })
        
        time.sleep(0.1)
    
    # 保存指标数据
    for metric in metrics_data:
        PerfTestMetrics.objects.create(
            job=job,
            created_by=job.executor,
            **metric
        )
    
    # 计算最终结果
    if response_times:
        return {
            'total_requests': total_requests,
            'failed_requests': failed_requests,
            'avg_response_time': round(statistics.mean(response_times), 2),
            'min_response_time': round(min(response_times), 2),
            'max_response_time': round(max(response_times), 2),
            'error_rate': round(failed_requests / total_requests, 4) if total_requests > 0 else 0,
            'requests_per_second': round(total_requests / test_duration, 2),
        }
    else:
        return {
            'total_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0,
            'min_response_time': 0,
            'max_response_time': 0,
            'error_rate': 0,
            'requests_per_second': 0,
        }
