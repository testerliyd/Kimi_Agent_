"""
飞书机器人服务模块
封装飞书API调用，支持Webhook+签名校验
"""
import json
import time
import hashlib
import base64
import hmac
import requests
from typing import Optional, Dict, Any
from django.conf import settings


class FeishuService:
    """
    飞书机器人服务类
    支持两种方式：
    1. 通过App ID/App Secret调用开放平台API
    2. 通过Webhook URL直接发送消息（使用签名校验）
    """
    
    def __init__(self, config=None):
        """
        初始化服务
        Args:
            config: FeishuConfig实例，为None则使用默认配置
        """
        from .models import FeishuConfig
        
        if config is None:
            config = FeishuConfig.objects.filter(is_default=True, is_active=True).first()
        
        self.config = config
        self.app_id = config.app_id if config else ''
        self.app_secret = config.app_secret if config else ''
        self.webhook_url = config.webhook_url if config else ''
        self.encrypt_key = config.encrypt_key if config else ''
        self.access_token = None
        
    def _get_access_token(self) -> str:
        """
        获取飞书访问令牌（应用方式）
        """
        if self.access_token:
            return self.access_token
        
        if not self.app_id or not self.app_secret:
            raise ValueError("App ID和App Secret不能为空")
        
        url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal'
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            'app_id': self.app_id,
            'app_secret': self.app_secret
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') != 0:
            raise Exception(f"获取access_token失败: {result.get('msg')}")
        
        self.access_token = result['app_access_token']
        return self.access_token
    
    def _generate_webhook_sign(self, timestamp: str) -> str:
        """
        生成Webhook签名
        签名算法: base64encode(hmac_sha256(timestamp + "\n" + secret))
        参考文档: https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
        """
        if not self.encrypt_key:
            return ''
        
        # 拼接字符串: timestamp + "\n" + secret
        string_to_sign = f"{timestamp}\n{self.encrypt_key}"
        
        # 使用HMAC-SHA256计算签名
        # hmac.new(key, msg, digestmod)
        hmac_code = hmac.new(
            self.encrypt_key.encode('utf-8'),  # key
            string_to_sign.encode('utf-8'),     # msg
            digestmod=hashlib.sha256
        ).digest()
        
        # Base64编码
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign
    
    def send_text_message(self, chat_id: str, content: str) -> Dict[str, Any]:
        """
        发送文本消息（通过App API）
        """
        url = 'https://open.feishu.cn/open-apis/message/v4/send/'
        
        headers = {
            'Authorization': f'Bearer {self._get_access_token()}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'chat_id': chat_id,
            'msg_type': 'text',
            'content': {
                'text': content
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def send_card_message(self, chat_id: str, card: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送卡片消息（通过App API）
        """
        url = 'https://open.feishu.cn/open-apis/message/v4/send/'
        
        headers = {
            'Authorization': f'Bearer {self._get_access_token()}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'chat_id': chat_id,
            'msg_type': 'interactive',
            'card': card
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def send_webhook_text(self, content: str, webhook_url: str = None) -> Dict[str, Any]:
        """
        通过Webhook发送文本消息（支持签名校验）
        
        Args:
            content: 消息内容
            webhook_url: Webhook地址，不传则使用配置中的地址
        """
        url = webhook_url or self.webhook_url
        
        if not url:
            raise ValueError("Webhook URL不能为空")
        
        timestamp = str(int(time.time()))
        sign = self._generate_webhook_sign(timestamp)
        
        data = {
            'timestamp': timestamp,
            'sign': sign,
            'msg_type': 'text',
            'content': {
                'text': content
            }
        }
        
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # 记录日志
        if result.get('code') != 0:
            raise Exception(f"发送失败: {result.get('msg')}")
        
        return result
    
    def send_webhook_card(self, card: Dict[str, Any], webhook_url: str = None) -> Dict[str, Any]:
        """
        通过Webhook发送卡片消息（支持签名校验）
        
        Args:
            card: 卡片内容
            webhook_url: Webhook地址，不传则使用配置中的地址
        """
        url = webhook_url or self.webhook_url
        
        if not url:
            raise ValueError("Webhook URL不能为空")
        
        timestamp = str(int(time.time()))
        sign = self._generate_webhook_sign(timestamp)
        
        data = {
            'timestamp': timestamp,
            'sign': sign,
            'msg_type': 'interactive',
            'card': card
        }
        
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') != 0:
            raise Exception(f"发送失败: {result.get('msg')}")
        
        return result
    
    def test_connection(self) -> Dict[str, Any]:
        """
        测试连接是否可用
        优先测试Webhook方式，如果没有配置Webhook则测试App方式
        """
        try:
            if self.webhook_url:
                # 测试Webhook方式
                result = self.send_webhook_text("测试消息：飞书机器人连接成功！")
                return {
                    'success': True,
                    'message': 'Webhook连接成功',
                    'method': 'webhook',
                    'data': result
                }
            elif self.app_id and self.app_secret:
                # 测试App方式
                token = self._get_access_token()
                return {
                    'success': True,
                    'message': 'App API连接成功',
                    'method': 'app_api',
                    'data': {'access_token': token[:20] + '...'}
                }
            else:
                return {
                    'success': False,
                    'message': '未配置有效的连接方式（需要Webhook URL或App ID/App Secret）'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'连接失败: {str(e)}'
            }
    
    @classmethod
    def send_bug_notification(cls, bug, action: str, config=None):
        """
        发送Bug通知
        Args:
            bug: Bug实例
            action: 动作类型 (created, assigned, resolved, closed, reopened)
            config: FeishuConfig实例
        """
        from .models import FeishuChatBinding
        
        service = cls(config)
        
        # 获取项目绑定的群聊
        bindings = FeishuChatBinding.objects.filter(
            project=bug.project,
            config=service.config,
            is_deleted=False
        )
        
        # 根据动作类型检查是否需要通知
        for binding in bindings:
            should_notify = False
            
            if action == 'created' and binding.notify_bug_created:
                should_notify = True
                title = '🐛 新Bug创建'
                color = 'red'
            elif action in ['assigned', 'resolved', 'closed', 'reopened'] and binding.notify_bug_status_change:
                should_notify = True
                action_names = {
                    'assigned': '已分配',
                    'resolved': '已解决',
                    'closed': '已关闭',
                    'reopened': '重新打开'
                }
                title = f'📝 Bug{action_names.get(action, action)}'
                color = 'blue' if action == 'assigned' else 'green' if action in ['resolved', 'closed'] else 'orange'
            
            if should_notify:
                card = cls._build_bug_card(bug, title, color)
                
                try:
                    # 优先使用Webhook方式
                    if binding.config and binding.config.webhook_url:
                        service.send_webhook_card(card, binding.config.webhook_url)
                    else:
                        # 使用App API方式
                        service.send_card_message(binding.chat_id, card)
                except Exception as e:
                    print(f"发送Bug通知失败: {e}")
    
    @classmethod
    def send_api_test_report(cls, job, chat_id: str = None, config=None):
        """
        发送API测试报告
        """
        service = cls(config)
        
        # 如果没有指定chat_id，使用默认配置
        if not chat_id and service.config:
            chat_id = service.config.default_chat_id
        
        if not chat_id and not service.webhook_url:
            return
        
        # 确定状态颜色
        if job.status == 'passed':
            color = 'green'
            status_text = '✅ 通过'
        elif job.status == 'failed':
            color = 'red'
            status_text = '❌ 失败'
        else:
            color = 'orange'
            status_text = '⚠️ 异常'
        
        card = {
            'config': {'wide_screen_mode': True},
            'header': {
                'title': {
                    'tag': 'plain_text',
                    'content': f'API测试报告: {job.name}'
                },
                'template': color
            },
            'elements': [
                {
                    'tag': 'div',
                    'text': {
                        'tag': 'lark_md',
                        'content': f'**项目:** {job.project.name}\n**状态:** {status_text}\n**执行人:** {job.executor.username if job.executor else "系统"}'
                    }
                },
                {
                    'tag': 'hr'
                },
                {
                    'tag': 'div',
                    'text': {
                        'tag': 'lark_md',
                        'content': f'**测试结果统计**\n\n总用例数: {job.total_cases}\n通过: {job.passed_cases} ✅\n失败: {job.failed_cases} ❌\n错误: {job.error_cases} ⚠️'
                    }
                },
                {
                    'tag': 'hr'
                },
                {
                    'tag': 'action',
                    'actions': [
                        {
                            'tag': 'button',
                            'text': {
                                'tag': 'plain_text',
                                'content': '查看详细报告'
                            },
                            'type': 'primary',
                            'url': job.report_url or f'/apitest/jobs/{job.id}'
                        }
                    ]
                }
            ]
        }
        
        try:
            # 优先使用Webhook方式
            if service.webhook_url:
                service.send_webhook_card(card)
            elif chat_id:
                service.send_card_message(chat_id, card)
        except Exception as e:
            print(f"发送API测试报告失败: {e}")
    
    @classmethod
    def send_perf_test_report(cls, job, chat_id: str = None, config=None):
        """
        发送性能测试报告
        """
        service = cls(config)
        
        if not chat_id and service.config:
            chat_id = service.config.default_chat_id
        
        if not chat_id and not service.webhook_url:
            return
        
        # 确定状态颜色
        if job.status == 'passed':
            color = 'green'
            status_text = '✅ 通过'
        elif job.status == 'failed':
            color = 'red'
            status_text = '❌ 失败'
        else:
            color = 'orange'
            status_text = '⚠️ 异常'
        
        card = {
            'config': {'wide_screen_mode': True},
            'header': {
                'title': {
                    'tag': 'plain_text',
                    'content': f'性能测试报告: {job.name}'
                },
                'template': color
            },
            'elements': [
                {
                    'tag': 'div',
                    'text': {
                        'tag': 'lark_md',
                        'content': f'**项目:** {job.project.name}\n**状态:** {status_text}\n**场景:** {job.scenario.name}'
                    }
                },
                {
                    'tag': 'hr'
                },
                {
                    'tag': 'div',
                    'text': {
                        'tag': 'lark_md',
                        'content': f'**性能指标**\n\n总请求数: {job.total_requests or "N/A"}\n平均响应时间: {job.avg_response_time or "N/A"} ms\n错误率: {(job.error_rate or 0) * 100}%\n每秒请求数: {job.requests_per_second or "N/A"}'
                    }
                },
                {
                    'tag': 'hr'
                },
                {
                    'tag': 'action',
                    'actions': [
                        {
                            'tag': 'button',
                            'text': {
                                'tag': 'plain_text',
                                'content': '查看详细报告'
                            },
                            'type': 'primary',
                            'url': f'/perftest/jobs/{job.id}'
                        }
                    ]
                }
            ]
        }
        
        try:
            # 优先使用Webhook方式
            if service.webhook_url:
                service.send_webhook_card(card)
            elif chat_id:
                service.send_card_message(chat_id, card)
        except Exception as e:
            print(f"发送性能测试报告失败: {e}")
    
    @staticmethod
    def _build_bug_card(bug, title: str, color: str) -> Dict[str, Any]:
        """
        构建Bug卡片
        """
        return {
            'config': {'wide_screen_mode': True},
            'header': {
                'title': {
                    'tag': 'plain_text',
                    'content': title
                },
                'template': color
            },
            'elements': [
                {
                    'tag': 'div',
                    'text': {
                        'tag': 'lark_md',
                        'content': f'**[{bug.bug_no}]** {bug.title}'
                    }
                },
                {
                    'tag': 'div',
                    'text': {
                        'tag': 'lark_md',
                        'content': f'**项目:** {bug.project.name}\n**严重程度:** {bug.get_severity_display()}\n**优先级:** {bug.get_priority_display()}\n**状态:** {bug.get_status_display()}\n**报告人:** {bug.reporter.username if bug.reporter else "未知"}\n**处理人:** {bug.assignee.username if bug.assignee else "未分配"}'
                    }
                },
                {
                    'tag': 'hr'
                },
                {
                    'tag': 'div',
                    'text': {
                        'tag': 'lark_md',
                        'content': f'**描述:**\n{bug.description[:200]}...' if len(bug.description) > 200 else f'**描述:**\n{bug.description}'
                    }
                },
                {
                    'tag': 'action',
                    'actions': [
                        {
                            'tag': 'button',
                            'text': {
                                'tag': 'plain_text',
                                'content': '查看详情'
                            },
                            'type': 'primary',
                            'url': f'/bugs/{bug.id}'
                        }
                    ]
                }
            ]
        }
