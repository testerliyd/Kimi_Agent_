"""
大模型服务模块
封装各种大模型API调用
"""
import json
import requests
from typing import List, Dict, Any, Optional


class LLMService:
    """
    大模型服务类
    统一封装各种大模型API调用
    """
    
    def __init__(self, config):
        """
        初始化服务
        Args:
            config: LLMConfig实例
        """
        self.config = config
        self.provider = config.provider.code
        self.base_url = config.custom_base_url or config.provider.base_url
        self.api_key = config.api_key
        self.api_secret = config.api_secret
        self.model = config.default_model
        
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        发送聊天请求
        Args:
            messages: 消息列表，格式为 [{'role': 'user', 'content': '...'}]
            **kwargs: 其他参数
        Returns:
            包含响应内容的字典
        """
        if self.provider == 'openai':
            return self._chat_openai(messages, **kwargs)
        elif self.provider == 'anthropic':
            return self._chat_anthropic(messages, **kwargs)
        elif self.provider == 'moonshot':
            return self._chat_moonshot(messages, **kwargs)
        elif self.provider == 'deepseek':
            return self._chat_deepseek(messages, **kwargs)
        elif self.provider == 'alibaba':
            return self._chat_alibaba(messages, **kwargs)
        elif self.provider == 'baidu':
            return self._chat_baidu(messages, **kwargs)
        elif self.provider == 'zhipu':
            return self._chat_zhipu(messages, **kwargs)
        else:
            # 默认使用OpenAI格式
            return self._chat_openai_compatible(messages, **kwargs)
    
    def test_connection(self) -> Dict[str, Any]:
        """
        测试连接是否可用
        Returns:
            测试结果字典
        """
        try:
            messages = [{'role': 'user', 'content': 'Hello'}]
            response = self.chat(messages, max_tokens=10)
            return {
                'success': True,
                'message': '连接成功',
                'data': response
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'连接失败: {str(e)}'
            }
    
    def _chat_openai(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        OpenAI API调用
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model or 'gpt-3.5-turbo',
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
            'top_p': kwargs.get('top_p', self.config.top_p),
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        return {
            'content': result['choices'][0]['message']['content'],
            'prompt_tokens': result['usage']['prompt_tokens'],
            'completion_tokens': result['usage']['completion_tokens'],
            'total_tokens': result['usage']['total_tokens'],
        }
    
    def _chat_anthropic(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Anthropic Claude API调用
        """
        url = f"{self.base_url}/v1/messages"
        
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        # 转换消息格式
        system_message = ''
        chat_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                chat_messages.append(msg)
        
        data = {
            'model': self.model or 'claude-3-sonnet-20240229',
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
            'messages': chat_messages,
        }
        
        if system_message:
            data['system'] = system_message
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        return {
            'content': result['content'][0]['text'],
            'prompt_tokens': result['usage']['input_tokens'],
            'completion_tokens': result['usage']['output_tokens'],
            'total_tokens': result['usage']['input_tokens'] + result['usage']['output_tokens'],
        }
    
    def _chat_moonshot(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        月之暗面Kimi API调用
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model or 'moonshot-v1-8k',
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        return {
            'content': result['choices'][0]['message']['content'],
            'prompt_tokens': result['usage']['prompt_tokens'],
            'completion_tokens': result['usage']['completion_tokens'],
            'total_tokens': result['usage']['total_tokens'],
        }
    
    def _chat_deepseek(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        DeepSeek API调用
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model or 'deepseek-chat',
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        return {
            'content': result['choices'][0]['message']['content'],
            'prompt_tokens': result['usage']['prompt_tokens'],
            'completion_tokens': result['usage']['completion_tokens'],
            'total_tokens': result['usage']['total_tokens'],
        }
    
    def _chat_alibaba(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        阿里通义千问API调用
        """
        url = f"{self.base_url}/compatible-mode/v1/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model or 'qwen-turbo',
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        return {
            'content': result['choices'][0]['message']['content'],
            'prompt_tokens': result['usage']['prompt_tokens'],
            'completion_tokens': result['usage']['completion_tokens'],
            'total_tokens': result['usage']['total_tokens'],
        }
    
    def _chat_baidu(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        百度文心一言API调用
        """
        # 百度API需要先获取access_token
        import urllib.parse
        
        # 获取access_token
        token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.api_secret}"
        token_response = requests.post(token_url, timeout=30)
        token_response.raise_for_status()
        access_token = token_response.json()['access_token']
        
        # 调用API
        url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{self.model or 'ernie-bot'}?access_token={access_token}"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # 转换消息格式
        chat_messages = [{'role': msg['role'], 'content': msg['content']} for msg in messages if msg['role'] != 'system']
        
        data = {
            'messages': chat_messages,
            'max_output_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        return {
            'content': result['result'],
            'prompt_tokens': result['usage']['prompt_tokens'],
            'completion_tokens': result['usage']['completion_tokens'],
            'total_tokens': result['usage']['total_tokens'],
        }
    
    def _chat_zhipu(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        智谱AI API调用
        """
        import jwt
        import time
        
        # 生成JWT token
        payload = {
            "api_key": self.api_key,
            "exp": int(time.time()) + 3600,
            "timestamp": int(time.time()),
        }
        token = jwt.encode(payload, self.api_secret, algorithm="HS256")
        
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            'Authorization': token,
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model or 'glm-4',
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        return {
            'content': result['choices'][0]['message']['content'],
            'prompt_tokens': result['usage']['prompt_tokens'],
            'completion_tokens': result['usage']['completion_tokens'],
            'total_tokens': result['usage']['total_tokens'],
        }
    
    def _chat_openai_compatible(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        OpenAI兼容格式API调用
        适用于大多数国内大模型
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model or 'default',
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
            'top_p': kwargs.get('top_p', self.config.top_p),
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        return {
            'content': result['choices'][0]['message']['content'],
            'prompt_tokens': result.get('usage', {}).get('prompt_tokens', 0),
            'completion_tokens': result.get('usage', {}).get('completion_tokens', 0),
            'total_tokens': result.get('usage', {}).get('total_tokens', 0),
        }
