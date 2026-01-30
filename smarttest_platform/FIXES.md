# 问题修复记录

## 修复时间
2026-01-29

## 修复内容

### 1. 依赖包问题

**问题**: `feishu-bot-api==1.0.0` 包不存在

**解决方案**:
- 移除了不存在的 `feishu-bot-api` 包
- 移除了不使用的 `djongo` 和 `pymongo` 包
- 添加了 `django-redis` 包用于Redis缓存
- 添加了 `PyJWT` 包用于JWT处理

**修改文件**: `requirements.txt`

### 2. 飞书机器人实现

**问题**: 原代码依赖不存在的SDK

**解决方案**:
- 使用 `requests` 库直接调用飞书API
- 支持两种方式：
  1. **Webhook方式**（推荐）：通过Webhook URL + 签名校验发送消息
  2. **应用方式**：通过App ID/App Secret调用开放平台API

**修改文件**:
- `apps/feishu/services.py` - 重写飞书服务类
- `apps/feishu/views.py` - 更新测试连接和发送消息方法
- `apps/feishu/models.py` - 添加字段说明

**签名算法**:
```python
# 拼接字符串: timestamp + "\n" + secret
string_to_sign = f"{timestamp}\n{secret}"

# 使用HMAC-SHA256计算签名
hmac_code = hmac.new(
    secret.encode('utf-8'),      # key
    string_to_sign.encode('utf-8'),  # msg
    digestmod=hashlib.sha256
).digest()

# Base64编码
sign = base64.b64encode(hmac_code).decode('utf-8')
```

参考文档: https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot

### 3. 文档更新

**修改文件**:
- `README.md` - 添加飞书配置说明
- `docs/使用说明书.md` - 详细说明Webhook和应用两种方式

### 4. 新增测试脚本

**新增文件**: `test_feishu_webhook.py`

用于测试飞书Webhook消息发送和签名校验。

## 飞书配置方式对比

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| Webhook | 简单快捷，无需创建应用 | 功能有限 | 快速接入，简单通知 |
| 应用方式 | 功能完整，可控性强 | 需要创建应用 | 企业级应用，复杂场景 |

## 快速配置Webhook方式

1. 在飞书群聊中添加自定义机器人
2. 获取Webhook地址和签名校验密钥
3. 在平台创建配置：
   - 配置名称: 任意名称
   - Webhook URL: 填入Webhook地址
   - Encrypt Key: 填入签名校验密钥
4. 点击"测试连接"验证

## 测试脚本使用

```bash
python test_feishu_webhook.py
```

按提示输入Webhook URL和密钥即可测试消息发送。
