#!/usr/bin/env python3
"""
SmartTest 部署校验脚本
用于部署时校验环境、数据库和配置是否正确
"""

import os
import sys
import subprocess
import sqlite3
import json
from datetime import datetime

# 项目路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'db.sqlite3')


class DeploymentVerifier:
    """部署校验器"""
    
    def __init__(self):
        self.checks = []
        self.errors = []
        self.warnings = []
    
    def log(self, message, level='INFO'):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {'INFO': 'ℹ️', 'SUCCESS': '✅', 'ERROR': '❌', 'WARNING': '⚠️'}.get(level, 'ℹ️')
        print(f"[{timestamp}] {prefix} {message}")
    
    def check_python_version(self):
        """检查 Python 版本"""
        self.log("检查 Python 版本...")
        version = sys.version_info
        if version.major == 3 and version.minor >= 10:
            self.log(f"Python {version.major}.{version.minor}.{version.micro} - 符合要求", 'SUCCESS')
            return True
        else:
            self.log(f"Python {version.major}.{version.minor}.{version.micro} - 需要 Python 3.10+", 'ERROR')
            return False
    
    def check_dependencies(self):
        """检查依赖包"""
        self.log("检查依赖包...")
        required_packages = [
            'django', 'djangorestframework', 'django-cors-headers',
            'django-filter', 'djangorestframework-simplejwt',
            'celery', 'redis', 'requests'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing.append(package)
        
        if missing:
            self.log(f"缺少依赖包: {', '.join(missing)}", 'ERROR')
            self.log("请运行: pip install -r requirements.txt", 'INFO')
            return False
        
        self.log(f"所有 {len(required_packages)} 个依赖包已安装", 'SUCCESS')
        return True
    
    def check_database_file(self):
        """检查数据库文件"""
        self.log("检查数据库文件...")
        if os.path.exists(DB_PATH):
            size = os.path.getsize(DB_PATH)
            self.log(f"数据库文件存在 ({size / 1024:.2f} KB)", 'SUCCESS')
            return True
        else:
            self.log("数据库文件不存在，需要执行迁移", 'WARNING')
            return False
    
    def check_database_tables(self):
        """检查数据库表"""
        self.log("检查数据库表...")
        
        if not os.path.exists(DB_PATH):
            self.log("数据库文件不存在，跳过表检查", 'WARNING')
            return False
        
        required_tables = {
            'users_user': '用户表',
            'users_role': '角色表',
            'users_permission': '权限表',
            'projects_project': '项目表',
            'testcases_testcase': '测试用例表',
            'testcases_testsuite': '测试套件表',
            'testcases_testplan': '测试计划表',
            'bugs_bug': 'Bug表',
            'llm_llmconfig': '大模型配置表',
            'llm_llmprovider': '大模型提供商表',
            'feishu_feishuconfig': '飞书配置表',
            'core_systemconfig': '系统配置表',
        }
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            missing = []
            for table, name in required_tables.items():
                if table not in existing_tables:
                    missing.append(f"{table} ({name})")
            
            if missing:
                self.log(f"缺少 {len(missing)} 个表: {', '.join(missing[:3])}...", 'ERROR')
                return False
            
            self.log(f"所有 {len(required_tables)} 个核心表已存在", 'SUCCESS')
            return True
            
        except Exception as e:
            self.log(f"数据库检查失败: {e}", 'ERROR')
            return False
    
    def check_superuser(self):
        """检查超级用户"""
        self.log("检查超级用户...")
        
        if not os.path.exists(DB_PATH):
            self.log("数据库文件不存在", 'WARNING')
            return False
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users_user WHERE is_superuser = 1")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count > 0:
                self.log(f"超级用户存在 ({count} 个)", 'SUCCESS')
                return True
            else:
                self.log("超级用户不存在", 'ERROR')
                return False
                
        except Exception as e:
            self.log(f"超级用户检查失败: {e}", 'ERROR')
            return False
    
    def check_django_settings(self):
        """检查 Django 配置"""
        self.log("检查 Django 配置...")
        
        settings_path = os.path.join(BASE_DIR, 'smarttest', 'settings.py')
        if not os.path.exists(settings_path):
            self.log("settings.py 不存在", 'ERROR')
            return False
        
        with open(settings_path, 'r') as f:
            content = f.read()
        
        required_settings = [
            'INSTALLED_APPS',
            'REST_FRAMEWORK',
            'SIMPLE_JWT',
            'DATABASES',
        ]
        
        missing = [s for s in required_settings if s not in content]
        if missing:
            self.log(f"缺少配置项: {', '.join(missing)}", 'ERROR')
            return False
        
        self.log("Django 配置正常", 'SUCCESS')
        return True
    
    def check_static_files(self):
        """检查静态文件"""
        self.log("检查静态文件...")
        
        static_dir = os.path.join(BASE_DIR, 'static')
        if os.path.exists(static_dir):
            files = os.listdir(static_dir)
            self.log(f"静态文件目录存在 ({len(files)} 个文件/目录)", 'SUCCESS')
            return True
        else:
            self.log("静态文件目录不存在", 'WARNING')
            return False
    
    def check_frontend_build(self):
        """检查前端构建"""
        self.log("检查前端构建...")
        
        frontend_dist = os.path.join(BASE_DIR, '..', 'app', 'dist')
        if os.path.exists(frontend_dist):
            index_html = os.path.join(frontend_dist, 'index.html')
            if os.path.exists(index_html):
                self.log("前端构建文件存在", 'SUCCESS')
                return True
        
        self.log("前端构建文件不存在，请运行 npm run build", 'WARNING')
        return False
    
    def check_environment_variables(self):
        """检查环境变量"""
        self.log("检查环境变量...")
        
        env_file = os.path.join(BASE_DIR, '.env')
        if os.path.exists(env_file):
            self.log("环境变量文件存在", 'SUCCESS')
            return True
        else:
            self.log("环境变量文件不存在，使用默认配置", 'WARNING')
            return True  # 不是致命错误
    
    def check_port_availability(self):
        """检查端口可用性"""
        self.log("检查端口可用性...")
        
        import socket
        ports = [8000, 5173, 6379]  # Django, Vite, Redis
        port_names = {8000: 'Django', 5173: 'Vite', 6379: 'Redis'}
        
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                self.log(f"端口 {port} ({port_names.get(port, 'Unknown')}) 已被占用", 'WARNING')
            else:
                self.log(f"端口 {port} ({port_names.get(port, 'Unknown')}) 可用", 'SUCCESS')
        
        return True
    
    def run_django_checks(self):
        """运行 Django 系统检查"""
        self.log("运行 Django 系统检查...")
        
        try:
            os.chdir(BASE_DIR)
            result = subprocess.run(
                [sys.executable, 'manage.py', 'check'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log("Django 系统检查通过", 'SUCCESS')
                return True
            else:
                self.log("Django 系统检查失败:", 'ERROR')
                print(result.stdout)
                print(result.stderr)
                return False
                
        except Exception as e:
            self.log(f"Django 检查失败: {e}", 'ERROR')
            return False
    
    def generate_report(self):
        """生成校验报告"""
        self.log("\n" + "=" * 60)
        self.log("部署校验报告")
        self.log("=" * 60)
        
        total = len(self.checks)
        passed = sum(1 for _, r in self.checks if r)
        failed = total - passed
        
        for name, result in self.checks:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {status} - {name}")
        
        print(f"\n  总计: {total} 项")
        print(f"  通过: {passed} 项")
        print(f"  失败: {failed} 项")
        
        if failed == 0:
            print("\n  🎉 部署校验全部通过！")
            print("\n  启动命令:")
            print("    后端: python manage.py runserver")
            print("    前端: npm run dev")
            return True
        else:
            print(f"\n  ⚠️ 有 {failed} 项校验失败")
            print("\n  请修复上述问题后重新运行校验")
            return False
    
    def run_all(self):
        """运行所有校验"""
        self.log("=" * 60)
        self.log("SmartTest 部署校验开始")
        self.log("=" * 60)
        
        checks = [
            ('Python 版本', self.check_python_version),
            ('依赖包', self.check_dependencies),
            ('数据库文件', self.check_database_file),
            ('数据库表', self.check_database_tables),
            ('超级用户', self.check_superuser),
            ('Django 配置', self.check_django_settings),
            ('静态文件', self.check_static_files),
            ('前端构建', self.check_frontend_build),
            ('环境变量', self.check_environment_variables),
            ('端口可用性', self.check_port_availability),
            ('Django 系统检查', self.run_django_checks),
        ]
        
        for name, check_func in checks:
            try:
                result = check_func()
                self.checks.append((name, result))
            except Exception as e:
                self.log(f"校验异常: {e}", 'ERROR')
                self.checks.append((name, False))
        
        return self.generate_report()


def main():
    """主函数"""
    verifier = DeploymentVerifier()
    success = verifier.run_all()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
