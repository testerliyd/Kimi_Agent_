import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { systemApi } from '@/services/api';
import {
  Settings,
  Server,
  Database,
  Cpu,
  CheckCircle2,
  XCircle,
  AlertCircle,
  RefreshCw,
  Code,
  Globe,
  Mail,
  Bell,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SystemInfo {
  version: string;
  django_version: string;
  python_version: string;
  database_type: string;
  redis_connected: boolean;
}

interface HealthStatus {
  status: string;
  database: boolean;
  redis: boolean;
  celery: boolean;
}

interface ConfigItem {
  id: number;
  key: string;
  value: string;
  description: string;
  category: string;
  is_editable: boolean;
}

export default function SystemConfig() {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [configs, setConfigs] = useState<ConfigItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [infoRes, healthRes, configsRes] = await Promise.all([
        systemApi.getSystemInfo(),
        systemApi.getHealthStatus(),
        systemApi.getConfigs(),
      ]);

      if (infoRes.code === 200) {
        setSystemInfo(infoRes.data);
      }
      if (healthRes.code === 200) {
        setHealthStatus(healthRes.data);
      }
      if (configsRes.code === 200) {
        setConfigs(configsRes.data);
      }
    } catch (error) {
      console.error('获取系统信息失败:', error);
      // 模拟数据
      setSystemInfo({
        version: '1.0.0',
        django_version: '4.2.0',
        python_version: '3.11.0',
        database_type: 'SQLite',
        redis_connected: false,
      });
      setHealthStatus({
        status: 'healthy',
        database: true,
        redis: false,
        celery: false,
      });
      setConfigs([
        { id: 1, key: 'SITE_NAME', value: 'SmartTest', description: '站点名称', category: 'basic', is_editable: true },
        { id: 2, key: 'SITE_LOGO', value: '', description: '站点Logo URL', category: 'basic', is_editable: true },
        { id: 3, key: 'PAGE_SIZE', value: '20', description: '默认分页大小', category: 'basic', is_editable: true },
        { id: 4, key: 'SESSION_TIMEOUT', value: '3600', description: '会话超时时间（秒）', category: 'security', is_editable: true },
        { id: 5, key: 'MAX_LOGIN_ATTEMPTS', value: '5', description: '最大登录尝试次数', category: 'security', is_editable: true },
        { id: 6, key: 'ENABLE_REGISTRATION', value: 'true', description: '是否开放注册', category: 'security', is_editable: true },
        { id: 7, key: 'EMAIL_HOST', value: 'smtp.example.com', description: 'SMTP服务器地址', category: 'email', is_editable: true },
        { id: 8, key: 'EMAIL_PORT', value: '587', description: 'SMTP端口', category: 'email', is_editable: true },
        { id: 9, key: 'EMAIL_USE_TLS', value: 'true', description: '是否使用TLS', category: 'email', is_editable: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  const handleUpdateConfig = async (id: number, value: string) => {
    try {
      await systemApi.updateConfig(id, value);
      fetchData();
    } catch (error) {
      console.error('更新配置失败:', error);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'basic':
        return Settings;
      case 'security':
        return AlertCircle;
      case 'email':
        return Mail;
      case 'notification':
        return Bell;
      default:
        return Settings;
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'basic':
        return '基础设置';
      case 'security':
        return '安全设置';
      case 'email':
        return '邮件设置';
      case 'notification':
        return '通知设置';
      default:
        return '其他设置';
    }
  };

  const categories = Array.from(new Set(configs.map((c) => c.category)));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">系统配置</h1>
          <p className="text-slate-400 mt-1">查看系统状态和管理系统配置</p>
        </div>
        <Button
          variant="outline"
          onClick={handleRefresh}
          disabled={refreshing}
          className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
        >
          <RefreshCw className={cn('w-4 h-4 mr-2', refreshing && 'animate-spin')} />
          刷新
        </Button>
      </div>

      {/* 系统状态卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                <Code className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-slate-400">系统版本</p>
                <p className="text-xl font-bold text-slate-100">{systemInfo?.version}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Django版本</p>
                <p className="text-xl font-bold text-slate-100">{systemInfo?.django_version}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-500 to-orange-500 flex items-center justify-center">
                <Cpu className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Python版本</p>
                <p className="text-xl font-bold text-slate-100">{systemInfo?.python_version}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20">
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-sm text-slate-400">数据库类型</p>
                <p className="text-xl font-bold text-slate-100">{systemInfo?.database_type}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 健康状态 */}
      <Card className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-slate-100 flex items-center gap-2">
            <Server className="w-5 h-5 text-cyan-400" />
            服务健康状态
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className={cn(
              'flex items-center gap-4 p-4 rounded-lg border',
              healthStatus?.database
                ? 'bg-green-500/10 border-green-500/30'
                : 'bg-red-500/10 border-red-500/30'
            )}>
              {healthStatus?.database ? (
                <CheckCircle2 className="w-8 h-8 text-green-400" />
              ) : (
                <XCircle className="w-8 h-8 text-red-400" />
              )}
              <div>
                <p className="font-medium text-slate-200">数据库</p>
                <p className={cn(
                  'text-sm',
                  healthStatus?.database ? 'text-green-400' : 'text-red-400'
                )}>
                  {healthStatus?.database ? '运行正常' : '连接异常'}
                </p>
              </div>
            </div>

            <div className={cn(
              'flex items-center gap-4 p-4 rounded-lg border',
              healthStatus?.redis
                ? 'bg-green-500/10 border-green-500/30'
                : 'bg-red-500/10 border-red-500/30'
            )}>
              {healthStatus?.redis ? (
                <CheckCircle2 className="w-8 h-8 text-green-400" />
              ) : (
                <XCircle className="w-8 h-8 text-red-400" />
              )}
              <div>
                <p className="font-medium text-slate-200">Redis</p>
                <p className={cn(
                  'text-sm',
                  healthStatus?.redis ? 'text-green-400' : 'text-red-400'
                )}>
                  {healthStatus?.redis ? '运行正常' : '连接异常'}
                </p>
              </div>
            </div>

            <div className={cn(
              'flex items-center gap-4 p-4 rounded-lg border',
              healthStatus?.celery
                ? 'bg-green-500/10 border-green-500/30'
                : 'bg-red-500/10 border-red-500/30'
            )}>
              {healthStatus?.celery ? (
                <CheckCircle2 className="w-8 h-8 text-green-400" />
              ) : (
                <XCircle className="w-8 h-8 text-red-400" />
              )}
              <div>
                <p className="font-medium text-slate-200">Celery</p>
                <p className={cn(
                  'text-sm',
                  healthStatus?.celery ? 'text-green-400' : 'text-red-400'
                )}>
                  {healthStatus?.celery ? '运行正常' : '未启动'}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 配置项 */}
      <Card className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-slate-100 flex items-center gap-2">
            <Settings className="w-5 h-5 text-cyan-400" />
            系统设置
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue={categories[0]} className="w-full">
            <TabsList className="bg-slate-800/50 border border-cyan-500/20 mb-6">
              {categories.map((category) => {
                const Icon = getCategoryIcon(category);
                return (
                  <TabsTrigger
                    key={category}
                    value={category}
                    className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400 text-slate-400"
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {getCategoryLabel(category)}
                  </TabsTrigger>
                );
              })}
            </TabsList>

            {categories.map((category) => (
              <TabsContent key={category} value={category} className="space-y-4">
                {configs
                  .filter((c) => c.category === category)
                  .map((config) => (
                    <div
                      key={config.id}
                      className="flex items-start justify-between p-4 rounded-lg bg-slate-800/30 border border-cyan-500/10 hover:border-cyan-500/30 transition-all"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Label className="text-slate-200 font-medium">
                            {config.key}
                          </Label>
                          {!config.is_editable && (
                            <Badge variant="outline" className="border-slate-600 text-slate-500 text-xs">
                              只读
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-slate-400 mt-1">{config.description}</p>
                      </div>
                      <div className="w-64 ml-4">
                        <Input
                          value={config.value}
                          onChange={(e) => {
                            const newConfigs = configs.map((c) =>
                              c.id === config.id ? { ...c, value: e.target.value } : c
                            );
                            setConfigs(newConfigs);
                          }}
                          onBlur={(e) => handleUpdateConfig(config.id, e.target.value)}
                          disabled={!config.is_editable}
                          className={cn(
                            'bg-slate-800 border-slate-700 text-slate-200',
                            !config.is_editable && 'opacity-50 cursor-not-allowed'
                          )}
                        />
                      </div>
                    </div>
                  ))}
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
