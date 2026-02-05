"""
Django settings for SmartTest project.

智能化测试平台配置文件
包含：测试管理、项目管理、用例管理、Bug管理、接口自动化测试、
      性能测试、大模型API配置管理、用户管理、飞书机器人集成
"""

import os
from pathlib import Path
from datetime import timedelta

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全设置
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-change-in-production')

# 调试模式
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# 允许的主机
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# 应用定义
INSTALLED_APPS = [
    # Django内置应用
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 第三方应用
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_yasg',
    
    # 项目应用
    'apps.users',
    'apps.projects',
    'apps.testcases',
    'apps.bugs',
    'apps.apitest',
    'apps.perftest',
    'apps.llm',
    'apps.feishu',
    'apps.core',
    'apps.reports',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.RequestLogMiddleware',
]

ROOT_URLCONF = 'smarttest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'smarttest.wsgi.application'

# 数据库配置
# 根据环境变量选择数据库类型，默认使用SQLite（便于开发和测试）
DB_TYPE = os.environ.get('DB_TYPE', 'sqlite')

if DB_TYPE == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'smarttest'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'password'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    # SQLite配置（默认，用于开发和测试）
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 缓存配置
# 根据环境变量选择缓存类型，默认使用本地内存（便于开发和测试）
CACHE_TYPE = os.environ.get('CACHE_TYPE', 'locmem')

if CACHE_TYPE == 'redis':
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    # 本地内存缓存（默认，用于开发和测试）
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# 媒体文件
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 默认主键类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 自定义用户模型
AUTH_USER_MODEL = 'users.User'

# Django REST Framework配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardResultsSetPagination',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/minute',
        'user': '1000/minute',
    },
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

# JWT配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Celery配置
# 根据环境变量选择broker类型，默认使用内存（便于开发和测试）
CELERY_BROKER_TYPE = os.environ.get('CELERY_BROKER_TYPE', 'memory')

if CELERY_BROKER_TYPE == 'redis':
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
else:
    # 使用内存作为broker（默认，用于开发和测试）
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30分钟任务超时
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'error.log',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
            'level': 'ERROR',
        },
    },
    'root': {
        'handlers': ['console', 'file', 'error_file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# 飞书机器人配置
FEISHU_CONFIG = {
    'APP_ID': os.environ.get('FEISHU_APP_ID', ''),
    'APP_SECRET': os.environ.get('FEISHU_APP_SECRET', ''),
    'VERIFICATION_TOKEN': os.environ.get('FEISHU_VERIFICATION_TOKEN', ''),
    'ENCRYPT_KEY': os.environ.get('FEISHU_ENCRYPT_KEY', ''),
    'WEBHOOK_URL': os.environ.get('FEISHU_WEBHOOK_URL', ''),
}

# 大模型API配置
LLM_CONFIG = {
    # OpenAI
    'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', ''),
    'OPENAI_BASE_URL': os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
    
    # Anthropic Claude
    'ANTHROPIC_API_KEY': os.environ.get('ANTHROPIC_API_KEY', ''),
    'ANTHROPIC_BASE_URL': os.environ.get('ANTHROPIC_BASE_URL', 'https://api.anthropic.com'),
    
    # Google Gemini
    'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY', ''),
    
    # 百度文心一言
    'BAIDU_API_KEY': os.environ.get('BAIDU_API_KEY', ''),
    'BAIDU_SECRET_KEY': os.environ.get('BAIDU_SECRET_KEY', ''),
    
    # 阿里通义千问
    'DASHSCOPE_API_KEY': os.environ.get('DASHSCOPE_API_KEY', ''),
    
    # 讯飞星火
    'XUNFEI_APP_ID': os.environ.get('XUNFEI_APP_ID', ''),
    'XUNFEI_API_KEY': os.environ.get('XUNFEI_API_KEY', ''),
    'XUNFEI_API_SECRET': os.environ.get('XUNFEI_API_SECRET', ''),
    
    # 智谱AI
    'ZHIPU_API_KEY': os.environ.get('ZHIPU_API_KEY', ''),
    
    # 月之暗面Kimi
    'MOONSHOT_API_KEY': os.environ.get('MOONSHOT_API_KEY', ''),
    'MOONSHOT_BASE_URL': os.environ.get('MOONSHOT_BASE_URL', 'https://api.moonshot.cn/v1'),
    
    # DeepSeek
    'DEEPSEEK_API_KEY': os.environ.get('DEEPSEEK_API_KEY', ''),
    'DEEPSEEK_BASE_URL': os.environ.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1'),
    
    # MiniMax
    'MINIMAX_API_KEY': os.environ.get('MINIMAX_API_KEY', ''),
    'MINIMAX_GROUP_ID': os.environ.get('MINIMAX_GROUP_ID', ''),
    
    # 零一万物
    '01WW_API_KEY': os.environ.get('01WW_API_KEY', ''),
}

# 测试执行配置
TEST_EXECUTION_CONFIG = {
    'MAX_CONCURRENT_TESTS': 10,
    'TEST_TIMEOUT': 300,  # 5分钟
    'API_TEST_TIMEOUT': 60,  # 1分钟
    'PERF_TEST_DEFAULT_DURATION': 60,  # 1分钟
    'PERF_TEST_MAX_DURATION': 3600,  # 1小时
}

# 报告配置
REPORT_CONFIG = {
    'RETENTION_DAYS': 90,
    'MAX_REPORT_SIZE_MB': 50,
    'DEFAULT_FORMAT': 'html',
}

# 文件上传配置
FILE_UPLOAD_CONFIG = {
    'MAX_SIZE_MB': 100,
    'ALLOWED_EXTENSIONS': ['.json', '.yaml', '.yml', '.xml', '.csv', '.xlsx', '.har', '.jmx'],
}

# Swagger文档配置
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
}

# 安全设置
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
