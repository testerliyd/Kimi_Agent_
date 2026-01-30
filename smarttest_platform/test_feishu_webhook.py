#!/usr/bin/env python
"""
飞书Webhook测试脚本
用于验证Webhook签名校验和消息发送
"""
import time
import hashlib
import base64
import hmac
import requests


def generate_sign(timestamp: str, secret: str) -> str:
    """
    生成飞书Webhook签名
    签名算法: base64encode(hmac_sha256(timestamp + "\n" + secret))
    参考文档: https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
    """
    # 拼接字符串: timestamp + "\n" + secret
    string_to_sign = f"{timestamp}\n{secret}"
    
    # 使用HMAC-SHA256计算签名
    # hmac.new(key, msg, digestmod)
    hmac_code = hmac.new(
        secret.encode('utf-8'),         # key
        string_to_sign.encode('utf-8'),  # msg
        digestmod=hashlib.sha256
    ).digest()
    
    # Base64编码
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


def send_webhook_message(webhook_url: str, secret: str, content: str):
    """
    发送Webhook消息
    """
    timestamp = str(int(time.time()))
    sign = generate_sign(timestamp, secret)
    
    data = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "text",
        "content": {
            "text": content
        }
    }
    
    print(f"请求URL: {webhook_url}")
    print(f"请求数据: {data}")
    
    response = requests.post(webhook_url, json=data, timeout=30)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    return response.json()


def send_webhook_card(webhook_url: str, secret: str, title: str, content: str):
    """
    发送Webhook卡片消息
    """
    timestamp = str(int(time.time()))
    sign = generate_sign(timestamp, secret)
    
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": content}
            }
        ]
    }
    
    data = {
        "timestamp": timestamp,
        "sign": sign,
        "msg_type": "interactive",
        "card": card
    }
    
    print(f"请求URL: {webhook_url}")
    print(f"请求数据: {data}")
    
    response = requests.post(webhook_url, json=data, timeout=30)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    return response.json()


def main():
    print("=" * 50)
    print("飞书Webhook测试工具")
    print("=" * 50)
    print()
    
    # 用户输入
    webhook_url = input("请输入Webhook URL: ").strip()
    secret = input("请输入签名校验密钥（如果没有请直接回车）: ").strip()
    
    if not webhook_url:
        print("错误: Webhook URL不能为空")
        return
    
    print()
    print("选择测试类型:")
    print("1. 发送文本消息")
    print("2. 发送卡片消息")
    
    choice = input("请输入选项(1/2): ").strip()
    
    if choice == "1":
        content = input("请输入消息内容: ").strip()
        if not content:
            content = "测试消息：SmartTest平台飞书机器人连接成功！"
        
        print()
        print("发送文本消息...")
        result = send_webhook_message(webhook_url, secret, content)
        
        if result.get('code') == 0:
            print("✅ 发送成功！")
        else:
            print(f"❌ 发送失败: {result.get('msg')}")
    
    elif choice == "2":
        title = input("请输入卡片标题: ").strip() or "测试卡片"
        content = input("请输入卡片内容: ").strip() or "这是来自SmartTest测试平台的卡片消息"
        
        print()
        print("发送卡片消息...")
        result = send_webhook_card(webhook_url, secret, title, content)
        
        if result.get('code') == 0:
            print("✅ 发送成功！")
        else:
            print(f"❌ 发送失败: {result.get('msg')}")
    
    else:
        print("无效的选项")


if __name__ == '__main__':
    main()
