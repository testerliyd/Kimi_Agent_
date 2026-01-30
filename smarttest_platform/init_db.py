#!/usr/bin/env python
"""
数据库初始化脚本
创建默认数据
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarttest.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import Role, Permission
from apps.llm.models import LLMProvider
from apps.feishu.models import FeishuMessageTemplate

User = get_user_model()


def init_permissions():
    """初始化权限数据"""
    print("初始化权限...")
    
    permissions = [
        # 用户管理
        {'code': 'user_view', 'name': '查看用户', 'category': 'user'},
        {'code': 'user_create', 'name': '创建用户', 'category': 'user'},
        {'code': 'user_update', 'name': '编辑用户', 'category': 'user'},
        {'code': 'user_delete', 'name': '删除用户', 'category': 'user'},
        
        # 项目管理
        {'code': 'project_view', 'name': '查看项目', 'category': 'project'},
        {'code': 'project_create', 'name': '创建项目', 'category': 'project'},
        {'code': 'project_update', 'name': '编辑项目', 'category': 'project'},
        {'code': 'project_delete', 'name': '删除项目', 'category': 'project'},
        
        # 用例管理
        {'code': 'testcase_view', 'name': '查看用例', 'category': 'testcase'},
        {'code': 'testcase_create', 'name': '创建用例', 'category': 'testcase'},
        {'code': 'testcase_update', 'name': '编辑用例', 'category': 'testcase'},
        {'code': 'testcase_delete', 'name': '删除用例', 'category': 'testcase'},
        {'code': 'testcase_execute', 'name': '执行用例', 'category': 'testcase'},
        
        # Bug管理
        {'code': 'bug_view', 'name': '查看Bug', 'category': 'bug'},
        {'code': 'bug_create', 'name': '创建Bug', 'category': 'bug'},
        {'code': 'bug_update', 'name': '编辑Bug', 'category': 'bug'},
        {'code': 'bug_delete', 'name': '删除Bug', 'category': 'bug'},
        {'code': 'bug_assign', 'name': '分配Bug', 'category': 'bug'},
        
        # 接口测试
        {'code': 'apitest_view', 'name': '查看接口测试', 'category': 'apitest'},
        {'code': 'apitest_create', 'name': '创建接口测试', 'category': 'apitest'},
        {'code': 'apitest_execute', 'name': '执行接口测试', 'category': 'apitest'},
        
        # 性能测试
        {'code': 'perftest_view', 'name': '查看性能测试', 'category': 'perftest'},
        {'code': 'perftest_create', 'name': '创建性能测试', 'category': 'perftest'},
        {'code': 'perftest_execute', 'name': '执行性能测试', 'category': 'perftest'},
        
        # 报告管理
        {'code': 'report_view', 'name': '查看报告', 'category': 'report'},
        {'code': 'report_create', 'name': '创建报告', 'category': 'report'},
        
        # 系统设置
        {'code': 'system_config', 'name': '系统配置', 'category': 'system'},
    ]
    
    for perm_data in permissions:
        Permission.objects.get_or_create(
            code=perm_data['code'],
            defaults=perm_data
        )
    
    print(f"权限初始化完成，共 {len(permissions)} 个权限")


def init_roles():
    """初始化角色数据"""
    print("初始化角色...")
    
    roles = [
        {
            'code': 'ADMIN',
            'name': '系统管理员',
            'role_type': 'system',
            'permissions': [p.code for p in Permission.objects.all()]
        },
        {
            'code': 'PROJECT_MANAGER',
            'name': '项目经理',
            'role_type': 'system',
            'permissions': [
                'project_view', 'project_create', 'project_update',
                'testcase_view', 'testcase_create', 'testcase_update', 'testcase_execute',
                'bug_view', 'bug_create', 'bug_update', 'bug_assign',
                'apitest_view', 'apitest_create', 'apitest_execute',
                'perftest_view', 'perftest_create', 'perftest_execute',
                'report_view', 'report_create'
            ]
        },
        {
            'code': 'TESTER',
            'name': '测试工程师',
            'role_type': 'system',
            'permissions': [
                'project_view',
                'testcase_view', 'testcase_create', 'testcase_update', 'testcase_execute',
                'bug_view', 'bug_create', 'bug_update',
                'apitest_view', 'apitest_create', 'apitest_execute',
                'perftest_view', 'perftest_create', 'perftest_execute',
                'report_view'
            ]
        },
        {
            'code': 'DEVELOPER',
            'name': '开发工程师',
            'role_type': 'system',
            'permissions': [
                'project_view',
                'testcase_view',
                'bug_view', 'bug_update',
                'report_view'
            ]
        },
        {
            'code': 'VIEWER',
            'name': '访客',
            'role_type': 'system',
            'permissions': [
                'project_view',
                'testcase_view',
                'bug_view',
                'report_view'
            ]
        },
    ]
    
    for role_data in roles:
        permissions = role_data.pop('permissions', [])
        role, created = Role.objects.get_or_create(
            code=role_data['code'],
            defaults=role_data
        )
        role.permissions = permissions
        role.save()
    
    print(f"角色初始化完成，共 {len(roles)} 个角色")


def init_llm_providers():
    """初始化大模型提供商"""
    print("初始化大模型提供商...")
    
    providers = [
        {
            'code': 'openai',
            'name': 'OpenAI',
            'base_url': 'https://api.openai.com/v1',
            'api_key_required': True,
            'supported_models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo']
        },
        {
            'code': 'anthropic',
            'name': 'Anthropic Claude',
            'base_url': 'https://api.anthropic.com',
            'api_key_required': True,
            'supported_models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
        },
        {
            'code': 'moonshot',
            'name': '月之暗面Kimi',
            'base_url': 'https://api.moonshot.cn/v1',
            'api_key_required': True,
            'supported_models': ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k']
        },
        {
            'code': 'deepseek',
            'name': 'DeepSeek',
            'base_url': 'https://api.deepseek.com/v1',
            'api_key_required': True,
            'supported_models': ['deepseek-chat', 'deepseek-coder']
        },
        {
            'code': 'alibaba',
            'name': '阿里通义千问',
            'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'api_key_required': True,
            'supported_models': ['qwen-turbo', 'qwen-plus', 'qwen-max']
        },
        {
            'code': 'baidu',
            'name': '百度文心一言',
            'base_url': 'https://aip.baidubce.com',
            'api_key_required': True,
            'api_secret_required': True,
            'supported_models': ['ernie-bot', 'ernie-bot-turbo']
        },
        {
            'code': 'zhipu',
            'name': '智谱AI',
            'base_url': 'https://open.bigmodel.cn/api/paas/v4',
            'api_key_required': True,
            'api_secret_required': True,
            'supported_models': ['glm-4', 'glm-4-plus', 'glm-3-turbo']
        },
    ]
    
    for provider_data in providers:
        LLMProvider.objects.get_or_create(
            code=provider_data['code'],
            defaults=provider_data
        )
    
    print(f"大模型提供商初始化完成，共 {len(providers)} 个提供商")


def init_feishu_templates():
    """初始化飞书消息模板"""
    print("初始化飞书消息模板...")
    
    templates = [
        {
            'name': 'Bug创建通知',
            'template_type': 'bug_created',
            'template_content': {
                'config': {'wide_screen_mode': True},
                'header': {
                    'title': {'tag': 'plain_text', 'content': '🐛 新Bug创建'},
                    'template': 'red'
                },
                'elements': [
                    {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**[{{bug_no}}]** {{title}}'}},
                    {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**项目:** {{project_name}}\n**严重程度:** {{severity}}\n**报告人:** {{reporter}}'}},
                    {'tag': 'hr'},
                    {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '{{description}}'}},
                ]
            },
            'is_default': True
        },
        {
            'name': 'Bug分配通知',
            'template_type': 'bug_assigned',
            'template_content': {
                'config': {'wide_screen_mode': True},
                'header': {
                    'title': {'tag': 'plain_text', 'content': '📝 Bug已分配'},
                    'template': 'blue'
                },
                'elements': [
                    {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**[{{bug_no}}]** {{title}}'}},
                    {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**分配给:** {{assignee}}\n**分配人:** {{assigned_by}}'}},
                ]
            },
            'is_default': True
        },
        {
            'name': 'API测试完成通知',
            'template_type': 'api_test_completed',
            'template_content': {
                'config': {'wide_screen_mode': True},
                'header': {
                    'title': {'tag': 'plain_text', 'content': '🧪 API测试完成'},
                    'template': '{{color}}'
                },
                'elements': [
                    {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**任务:** {{job_name}}\n**项目:** {{project_name}}\n**状态:** {{status}}'}},
                    {'tag': 'hr'},
                    {'tag': 'div', 'text': {'tag': 'lark_md', 'content': '**统计:**\n总用例: {{total_cases}}\n通过: {{passed_cases}} ✅\n失败: {{failed_cases}} ❌'}},
                ]
            },
            'is_default': True
        },
    ]
    
    for template_data in templates:
        FeishuMessageTemplate.objects.get_or_create(
            template_type=template_data['template_type'],
            is_default=True,
            defaults=template_data
        )
    
    print(f"飞书消息模板初始化完成，共 {len(templates)} 个模板")


def main():
    """主函数"""
    print("=" * 50)
    print("SmartTest 数据库初始化")
    print("=" * 50)
    print()
    
    try:
        init_permissions()
        init_roles()
        init_llm_providers()
        init_feishu_templates()
        
        print()
        print("=" * 50)
        print("数据库初始化完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"初始化失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
