import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { databaseApi } from '@/services/api';
import type { DatabaseConfig } from '@/types';
import {
  Plus,
  Edit2,
  Trash2,
  Database,
  Server,
  Check,
  X,
  TestTube,
  Star,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  HardDrive,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const dbTypes = [
  { code: 'mysql', name: 'MySQL' },
  { code: 'postgresql', name: 'PostgreSQL' },
  { code: 'sqlite', name: 'SQLite' },
];

export default function DatabaseConfigPage() {
  const [configs, setConfigs] = useState<DatabaseConfig[]>([]);
  const [currentConfig, setCurrentConfig] = useState<DatabaseConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingConfig, setEditingConfig] = useState<DatabaseConfig | null>(null);
  const [initDialogOpen, setInitDialogOpen] = useState(false);
  const [initializingId, setInitializingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<Partial<DatabaseConfig>>({
    name: '',
    db_type: 'mysql',
    host: 'localhost',
    port: 3306,
    database: '',
    username: '',
    password: '',
    is_active: true,
    is_default: false,
  });
  const [testingId, setTestingId] = useState<number | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<Record<number, boolean>>({});

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [configsRes, currentRes] = await Promise.all([
        databaseApi.getConfigs(),
        databaseApi.getCurrentConfig(),
      ]);

      if (configsRes.code === 200) {
        setConfigs(configsRes.data);
      }
      if (currentRes.code === 200) {
        setCurrentConfig(currentRes.data);
      }
    } catch (error) {
      console.error('获取数据库配置失败:', error);
      // 模拟数据
      const mockConfig: DatabaseConfig = {
        id: 1,
        name: '默认MySQL',
        db_type: 'mysql',
        host: 'localhost',
        port: 3306,
        database: 'smarttest',
        username: 'root',
        password: '******',
        is_active: true,
        is_default: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };
      setConfigs([mockConfig]);
      setCurrentConfig(mockConfig);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (config?: DatabaseConfig) => {
    if (config) {
      setEditingConfig(config);
      setFormData({ ...config });
    } else {
      setEditingConfig(null);
      setFormData({
        name: '',
        db_type: 'mysql',
        host: 'localhost',
        port: 3306,
        database: '',
        username: '',
        password: '',
        is_active: true,
        is_default: false,
      });
    }
    setDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      if (editingConfig) {
        const response = await databaseApi.updateConfig(editingConfig.id, formData);
        if (response.code === 200) {
          fetchData();
        }
      } else {
        const response = await databaseApi.createConfig(formData);
        if (response.code === 200) {
          fetchData();
        }
      }
      setDialogOpen(false);
    } catch (error) {
      console.error('保存配置失败:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此配置吗？')) return;
    try {
      await databaseApi.deleteConfig(id);
      fetchData();
    } catch (error) {
      console.error('删除配置失败:', error);
    }
  };

  const handleTest = async (id: number) => {
    setTestingId(id);
    try {
      const response = await databaseApi.testConnection(id);
      setConnectionStatus((prev) => ({ ...prev, [id]: response.data.success }));
      alert(response.data.message);
    } catch (error) {
      setConnectionStatus((prev) => ({ ...prev, [id]: false }));
      alert('连接测试失败: ' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setTestingId(null);
    }
  };

  const handleInitialize = async (id: number) => {
    setInitializingId(id);
    try {
      const response = await databaseApi.initializeDatabase(id);
      alert(response.data.message);
    } catch (error) {
      alert('初始化失败: ' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setInitializingId(null);
      setInitDialogOpen(false);
    }
  };

  const handleSetDefault = async (id: number) => {
    try {
      // 更新当前配置
      const config = configs.find((c) => c.id === id);
      if (config) {
        await databaseApi.updateCurrentConfig(config);
        fetchData();
      }
    } catch (error) {
      console.error('设置默认配置失败:', error);
    }
  };

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
          <h1 className="text-2xl font-bold text-slate-100">数据库配置</h1>
          <p className="text-slate-400 mt-1">管理数据库连接配置，支持MySQL、PostgreSQL和SQLite</p>
        </div>
        <Button
          onClick={() => handleOpenDialog()}
          className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          新建配置
        </Button>
      </div>

      {/* 当前配置状态 */}
      {currentConfig && (
        <Card className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border-cyan-500/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                  <Database className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-slate-100">当前数据库配置</h3>
                  <p className="text-slate-400">
                    {currentConfig.name} · {dbTypes.find((t) => t.code === currentConfig.db_type)?.name} · {currentConfig.host}:{currentConfig.port}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                  <CheckCircle2 className="w-3 h-3 mr-1" />
                  运行中
                </Badge>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInitDialogOpen(true)}
                  className="border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/10"
                >
                  <RefreshCw className="w-4 h-4 mr-1" />
                  初始化数据库
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 配置列表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {configs.map((config) => (
          <Card
            key={config.id}
            className={cn(
              'bg-slate-900/50 backdrop-blur-sm border-cyan-500/20 hover:border-cyan-500/40 transition-all duration-300',
              currentConfig?.id === config.id && 'border-cyan-500/50 shadow-[0_0_20px_rgba(34,211,238,0.1)]'
            )}
          >
            <CardHeader className="pb-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                    <HardDrive className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                      {config.name}
                      {currentConfig?.id === config.id && (
                        <Badge className="bg-green-500/20 text-green-400 border-green-500/30 text-xs">
                          当前使用
                        </Badge>
                      )}
                    </CardTitle>
                    <p className="text-sm text-slate-400">
                      {dbTypes.find((t) => t.code === config.db_type)?.name}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={config.is_active}
                    onCheckedChange={() => {}}
                    className="data-[state=checked]:bg-cyan-500"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-2 text-slate-400">
                  <Server className="w-4 h-4" />
                  <span>{config.host}:{config.port}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <Database className="w-4 h-4" />
                  <span>{config.database}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <span className="text-slate-500">用户名:</span>
                  <span>{config.username}</span>
                </div>
                <div className="flex items-center gap-2">
                  {connectionStatus[config.id] !== undefined && (
                    <Badge
                      variant="outline"
                      className={cn(
                        'text-xs',
                        connectionStatus[config.id]
                          ? 'border-green-500/30 text-green-400'
                          : 'border-red-500/30 text-red-400'
                      )}
                    >
                      {connectionStatus[config.id] ? '连接正常' : '连接失败'}
                    </Badge>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 pt-4 border-t border-cyan-500/10">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleOpenDialog(config)}
                  className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
                >
                  <Edit2 className="w-4 h-4 mr-1" />
                  编辑
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleTest(config.id)}
                  disabled={testingId === config.id}
                  className="border-green-500/30 text-green-400 hover:bg-green-500/10"
                >
                  {testingId === config.id ? (
                    <div className="w-4 h-4 border-2 border-green-400 border-t-transparent rounded-full animate-spin mr-1" />
                  ) : (
                    <TestTube className="w-4 h-4 mr-1" />
                  )}
                  测试连接
                </Button>
                {currentConfig?.id !== config.id && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleSetDefault(config.id)}
                    className="border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/10"
                  >
                    <Star className="w-4 h-4 mr-1" />
                    切换
                  </Button>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDelete(config.id)}
                  className="border-red-500/30 text-red-400 hover:bg-red-500/10 ml-auto"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 新建/编辑配置对话框 */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="bg-slate-900 border-cyan-500/30 max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-xl font-semibold text-slate-100">
              {editingConfig ? '编辑配置' : '新建配置'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label className="text-slate-300">配置名称</Label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="例如：生产环境MySQL"
                className="bg-slate-800 border-slate-700 text-slate-200"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">数据库类型</Label>
              <Select
                value={formData.db_type}
                onValueChange={(value) => setFormData({ ...formData, db_type: value as 'mysql' | 'postgresql' | 'sqlite' })}
              >
                <SelectTrigger className="bg-slate-800 border-slate-700 text-slate-200">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700">
                  {dbTypes.map((t) => (
                    <SelectItem key={t.code} value={t.code} className="text-slate-200">
                      {t.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {formData.db_type !== 'sqlite' && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-slate-300">主机</Label>
                    <Input
                      value={formData.host}
                      onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                      placeholder="localhost"
                      className="bg-slate-800 border-slate-700 text-slate-200"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-slate-300">端口</Label>
                    <Input
                      type="number"
                      value={formData.port}
                      onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                      placeholder="3306"
                      className="bg-slate-800 border-slate-700 text-slate-200"
                    />
                  </div>
                </div>
              </>
            )}

            <div className="space-y-2">
              <Label className="text-slate-300">数据库名</Label>
              <Input
                value={formData.database}
                onChange={(e) => setFormData({ ...formData, database: e.target.value })}
                placeholder="smarttest"
                className="bg-slate-800 border-slate-700 text-slate-200"
              />
            </div>

            {formData.db_type !== 'sqlite' && (
              <>
                <div className="space-y-2">
                  <Label className="text-slate-300">用户名</Label>
                  <Input
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    placeholder="root"
                    className="bg-slate-800 border-slate-700 text-slate-200"
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-slate-300">密码</Label>
                  <Input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder="******"
                    className="bg-slate-800 border-slate-700 text-slate-200"
                  />
                </div>
              </>
            )}
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDialogOpen(false)}
              className="border-slate-600 text-slate-300 hover:bg-slate-800"
            >
              <X className="w-4 h-4 mr-2" />
              取消
            </Button>
            <Button
              onClick={handleSave}
              className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white"
            >
              <Check className="w-4 h-4 mr-2" />
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 初始化数据库对话框 */}
      <Dialog open={initDialogOpen} onOpenChange={setInitDialogOpen}>
        <DialogContent className="bg-slate-900 border-cyan-500/30">
          <DialogHeader>
            <DialogTitle className="text-xl font-semibold text-slate-100 flex items-center gap-2">
              <AlertTriangle className="w-6 h-6 text-yellow-400" />
              初始化数据库
            </DialogTitle>
            <DialogDescription className="text-slate-400">
              此操作将执行数据库迁移并初始化数据。请确保已备份重要数据。
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
              <p className="text-sm text-yellow-400">
                <strong>警告：</strong> 初始化数据库将执行以下操作：
              </p>
              <ul className="mt-2 text-sm text-slate-400 list-disc list-inside space-y-1">
                <li>创建所有数据表</li>
                <li>执行数据库迁移</li>
                <li>初始化默认数据</li>
              </ul>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setInitDialogOpen(false)}
              className="border-slate-600 text-slate-300 hover:bg-slate-800"
            >
              <X className="w-4 h-4 mr-2" />
              取消
            </Button>
            <Button
              onClick={() => currentConfig && handleInitialize(currentConfig.id)}
              disabled={initializingId !== null}
              className="bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-500 hover:to-orange-500 text-white"
            >
              {initializingId !== null ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              确认初始化
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
