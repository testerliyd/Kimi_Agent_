#!/usr/bin/env python3
"""
SmartTest 数据库初始化脚本
用于部署时创建数据库表、初始化基础数据和校验数据完整性
"""

import os
import sys
import django
from datetime import datetime, timedelta

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarttest.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.db import connection, transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from apps.users.models import Role, Permission as CustomPermission
from apps.projects.models import Project
from apps.testcases.models import TestCase, TestSuite, TestPlan, TestCaseTag, TestCaseCategory
from apps.bugs.models import Bug, BugTag, BugCategory
from apps.llm.models import LLMConfig, LLMProvider
from apps.feishu.models import FeishuConfig
from apps.core.models import SystemConfig, AuditLog

User = get_user_model()


class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self):
        self.check_results = []
        self.init_results = []
    
    def log(self, message, level='INFO'):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def check_database_connection(self):
        """检查数据库连接"""
        self.log("检查数据库连接...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    self.log("✅ 数据库连接正常")
                    return True
        except Exception as e:
            self.log(f"❌ 数据库连接失败: {e}", 'ERROR')
            return False
    
    def check_tables_exist(self):
        """检查数据库表是否存在"""
        self.log("检查数据库表...")
        required_tables = [
            'users_user', 'users_role', 'users_permission',
            'projects_project', 'projects_projectversion', 'projects_projectmilestone',
            'testcases_testcase', 'testcases_testsuite', 'testcases_testplan',
            'testcases_testcasetag', 'testcases_testcasecategory',
            'bugs_bug', 'bugs_bugcomment', 'bugs_bughistory',
            'bugs_bugtag', 'bugs_bugcategory',
            'apitest_apidefinition', 'apitest_apitestcase', 'apitest_apitestjob',
            'perftest_perftestscenario', 'perftest_perftestjob',
            'llm_llmconfig', 'llm_llmprovider',
            'feishu_feishuconfig', 'feishu_feishumessagetemplate', 'feishu_feishuchatbinding',
            'core_systemconfig', 'core_auditlog', 'core_notification',
        ]
        
        missing_tables = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in required_tables:
                if table not in existing_tables:
                    missing_tables.append(table)
        
        if missing_tables:
            self.log(f"❌ 缺少 {len(missing_tables)} 个表: {', '.join(missing_tables)}", 'ERROR')
            return False
        
        self.log(f"✅ 所有 {len(required_tables)} 个表已存在")
        return True
    
    def run_migrations(self):
        """执行数据库迁移"""
        self.log("执行数据库迁移...")
        from django.core.management import call_command
        try:
            call_command('migrate', '--noinput', verbosity=0)
            self.log("✅ 数据库迁移完成")
            return True
        except Exception as e:
            self.log(f"❌ 数据库迁移失败: {e}", 'ERROR')
            return False
    
    def init_superuser(self):
        """初始化超级用户"""
        self.log("初始化超级用户...")
        try:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@smarttest.com',
                    password='admin123',
                    nickname='管理员',
                    phone='13800138000'
                )
                self.log("✅ 超级用户创建成功 (admin/admin123)")
            else:
                self.log("ℹ️ 超级用户已存在")
            return True
        except Exception as e:
            self.log(f"❌ 超级用户创建失败: {e}", 'ERROR')
            return False
    
    def init_roles(self):
        """初始化角色"""
        self.log("初始化角色...")
        roles_data = [
            {'name': '超级管理员', 'code': 'super_admin', 'description': '系统超级管理员，拥有所有权限'},
            {'name': '项目管理员', 'code': 'project_admin', 'description': '项目管理权限'},
            {'name': '测试负责人', 'code': 'test_lead', 'description': '测试团队负责人'},
            {'name': '测试工程师', 'code': 'test_engineer', 'description': '普通测试工程师'},
            {'name': '开发人员', 'code': 'developer', 'description': '开发人员'},
            {'name': '访客', 'code': 'guest', 'description': '只读权限'},
        ]
        
        try:
            for role_data in roles_data:
                Role.objects.get_or_create(
                    code=role_data['code'],
                    defaults=role_data
                )
            self.log(f"✅ 角色初始化完成 ({len(roles_data)} 个)")
            return True
        except Exception as e:
            self.log(f"❌ 角色初始化失败: {e}", 'ERROR')
            return False
    
    def init_permissions(self):
        """初始化权限"""
        self.log("初始化权限...")
        permissions_data = [
            # 用户管理权限
            {'name': '查看用户', 'code': 'user_view', 'module': 'user'},
            {'name': '创建用户', 'code': 'user_create', 'module': 'user'},
            {'name': '编辑用户', 'code': 'user_update', 'module': 'user'},
            {'name': '删除用户', 'code': 'user_delete', 'module': 'user'},
            # 项目管理权限
            {'name': '查看项目', 'code': 'project_view', 'module': 'project'},
            {'name': '创建项目', 'code': 'project_create', 'module': 'project'},
            {'name': '编辑项目', 'code': 'project_update', 'module': 'project'},
            {'name': '删除项目', 'code': 'project_delete', 'module': 'project'},
            # 测试用例权限
            {'name': '查看用例', 'code': 'testcase_view', 'module': 'testcase'},
            {'name': '创建用例', 'code': 'testcase_create', 'module': 'testcase'},
            {'name': '编辑用例', 'code': 'testcase_update', 'module': 'testcase'},
            {'name': '删除用例', 'code': 'testcase_delete', 'module': 'testcase'},
            {'name': '执行用例', 'code': 'testcase_execute', 'module': 'testcase'},
            # Bug管理权限
            {'name': '查看Bug', 'code': 'bug_view', 'module': 'bug'},
            {'name': '创建Bug', 'code': 'bug_create', 'module': 'bug'},
            {'name': '编辑Bug', 'code': 'bug_update', 'module': 'bug'},
            {'name': '删除Bug', 'code': 'bug_delete', 'module': 'bug'},
            {'name': '分配Bug', 'code': 'bug_assign', 'module': 'bug'},
            # 系统配置权限
            {'name': '查看配置', 'code': 'config_view', 'module': 'config'},
            {'name': '编辑配置', 'code': 'config_update', 'module': 'config'},
        ]
        
        try:
            for perm_data in permissions_data:
                CustomPermission.objects.get_or_create(
                    code=perm_data['code'],
                    defaults=perm_data
                )
            self.log(f"✅ 权限初始化完成 ({len(permissions_data)} 个)")
            return True
        except Exception as e:
            self.log(f"❌ 权限初始化失败: {e}", 'ERROR')
            return False
    
    def init_sample_project(self):
        """初始化示例项目"""
        self.log("初始化示例项目...")
        try:
            admin = User.objects.filter(username='admin').first()
            if not admin:
                self.log("❌ 超级用户不存在，无法创建示例项目", 'ERROR')
                return False
            
            project, created = Project.objects.get_or_create(
                code='DEMO001',
                defaults={
                    'name': 'SmartTest 演示项目',
                    'description': '这是一个用于演示的测试项目',
                    'project_type': 'web',
                    'status': 'active',
                    'priority': 'high',
                    'owner': admin,
                    'start_date': datetime.now().date(),
                    'end_date': (datetime.now() + timedelta(days=90)).date(),
                }
            )
            
            if created:
                # 创建示例测试用例
                TestCase.objects.get_or_create(
                    case_no='TC001',
                    defaults={
                        'name': '用户登录功能测试',
                        'description': '测试用户登录功能是否正常',
                        'pre_condition': '用户已注册',
                        'steps': '1. 打开登录页面\n2. 输入用户名和密码\n3. 点击登录按钮',
                        'expected_result': '登录成功，跳转到首页',
                        'case_type': 'functional',
                        'priority': 'high',
                        'status': 'active',
                        'project': project,
                        'creator': admin,
                    }
                )
                
                # 创建示例Bug
                Bug.objects.get_or_create(
                    bug_no='BUG001',
                    defaults={
                        'title': '登录页面加载缓慢',
                        'description': '登录页面加载时间超过5秒',
                        'bug_type': 'performance',
                        'severity': 'medium',
                        'priority': 'high',
                        'status': 'new',
                        'project': project,
                        'reporter': admin,
                    }
                )
                
                self.log("✅ 示例项目创建成功")
            else:
                self.log("ℹ️ 示例项目已存在")
            
            return True
        except Exception as e:
            self.log(f"❌ 示例项目创建失败: {e}", 'ERROR')
            return False
    
    def init_llm_providers(self):
        """初始化大模型提供商"""
        self.log("初始化大模型提供商...")
        providers_data = [
            {
                'name': 'OpenAI',
                'code': 'openai',
                'description': 'OpenAI GPT 系列模型',
                'supported_models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
                'is_active': True,
            },
            {
                'name': 'Anthropic',
                'code': 'anthropic',
                'description': 'Anthropic Claude 系列模型',
                'supported_models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
                'is_active': True,
            },
            {
                'name': 'Azure OpenAI',
                'code': 'azure',
                'description': 'Azure OpenAI 服务',
                'supported_models': ['gpt-4', 'gpt-35-turbo'],
                'is_active': True,
            },
            {
                'name': 'Ollama',
                'code': 'ollama',
                'description': '本地 Ollama 部署',
                'supported_models': ['llama2', 'codellama', 'mistral'],
                'is_active': True,
            },
        ]
        
        try:
            for provider_data in providers_data:
                LLMProvider.objects.get_or_create(
                    code=provider_data['code'],
                    defaults=provider_data
                )
            self.log(f"✅ 大模型提供商初始化完成 ({len(providers_data)} 个)")
            return True
        except Exception as e:
            self.log(f"❌ 大模型提供商初始化失败: {e}", 'ERROR')
            return False
    
    def init_system_configs(self):
        """初始化系统配置"""
        self.log("初始化系统配置...")
        configs_data = [
            {'key': 'site_name', 'value': 'SmartTest', 'category': 'general', 'description': '站点名称'},
            {'key': 'site_logo', 'value': '/logo.png', 'category': 'general', 'description': '站点Logo'},
            {'key': 'enable_registration', 'value': 'true', 'category': 'general', 'description': '是否允许注册'},
            {'key': 'enable_ai_features', 'value': 'true', 'category': 'ai', 'description': '是否启用AI功能'},
            {'key': 'default_llm_provider', 'value': 'openai', 'category': 'ai', 'description': '默认大模型提供商'},
            {'key': 'default_llm_model', 'value': 'gpt-4', 'category': 'ai', 'description': '默认大模型'},
            {'key': 'enable_feishu_notification', 'value': 'false', 'category': 'notification', 'description': '是否启用飞书通知'},
            {'key': 'enable_email_notification', 'value': 'false', 'category': 'notification', 'description': '是否启用邮件通知'},
        ]
        
        try:
            for config_data in configs_data:
                SystemConfig.objects.get_or_create(
                    key=config_data['key'],
                    defaults=config_data
                )
            self.log(f"✅ 系统配置初始化完成 ({len(configs_data)} 个)")
            return True
        except Exception as e:
            self.log(f"❌ 系统配置初始化失败: {e}", 'ERROR')
            return False
    
    def verify_data_integrity(self):
        """验证数据完整性"""
        self.log("验证数据完整性...")
        checks = [
            ('超级用户', User.objects.filter(is_superuser=True).count() >= 1),
            ('角色数据', Role.objects.count() >= 6),
            ('权限数据', CustomPermission.objects.count() >= 20),
            ('大模型提供商', LLMProvider.objects.count() >= 4),
            ('系统配置', SystemConfig.objects.count() >= 8),
        ]
        
        all_passed = True
        for name, passed in checks:
            status = "✅" if passed else "❌"
            self.log(f"{status} {name}: {'通过' if passed else '失败'}")
            if not passed:
                all_passed = False
        
        return all_passed
    
    def run_all(self):
        """运行所有初始化步骤"""
        self.log("=" * 60)
        self.log("SmartTest 数据库初始化开始")
        self.log("=" * 60)
        
        steps = [
            ('数据库连接检查', self.check_database_connection),
            ('数据库迁移', self.run_migrations),
            ('数据库表检查', self.check_tables_exist),
            ('超级用户初始化', self.init_superuser),
            ('角色初始化', self.init_roles),
            ('权限初始化', self.init_permissions),
            ('示例项目初始化', self.init_sample_project),
            ('大模型提供商初始化', self.init_llm_providers),
            ('系统配置初始化', self.init_system_configs),
            ('数据完整性验证', self.verify_data_integrity),
        ]
        
        results = []
        for name, step_func in steps:
            self.log(f"\n{'─' * 40}")
            try:
                result = step_func()
                results.append((name, result))
            except Exception as e:
                self.log(f"❌ {name} 执行异常: {e}", 'ERROR')
                results.append((name, False))
        
        # 输出总结
        self.log("\n" + "=" * 60)
        self.log("初始化结果总结")
        self.log("=" * 60)
        
        passed = sum(1 for _, r in results if r)
        failed = sum(1 for _, r in results if not r)
        
        for name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            self.log(f"{status} - {name}")
        
        self.log(f"\n总计: {len(results)} 项 | 通过: {passed} | 失败: {failed}")
        
        if failed == 0:
            self.log("\n🎉 数据库初始化全部成功！")
            return True
        else:
            self.log(f"\n⚠️ 有 {failed} 项初始化失败，请检查日志", 'WARNING')
            return False


def main():
    """主函数"""
    initializer = DatabaseInitializer()
    success = initializer.run_all()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
