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
} from '@/components/ui/dialog';
import { redisApi } from '@/services/api';
import type { RedisConfig } from '@/types';
import {
  Plus,
  Edit2,
  Trash2,
  Server,
  Check,
  X,
  TestTube,
  Star,
  Database,
  Hash,
  Lock,
  CheckCircle2,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function RedisConfigPage() {
  const [configs, setConfigs] = useState<RedisConfig[]>([]);
  const [currentConfig, setCurrentConfig] = useState<RedisConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingConfig, setEditingConfig] = useState<RedisConfig | null>(null);
  const [formData, setFormData] = useState<Partial<RedisConfig>>({
    name: '',
    host: 'localhost',
    port: 6379,
    password: '',
    db: 0,
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
        redisApi.getConfigs(),
        redisApi.getCurrentConfig(),
      ]);

      if (configsRes.code === 200) {
        setConfigs(configsRes.data);
      }
      if (currentRes.code === 200) {
        setCurrentConfig(currentRes.data);
      }
    } catch (error) {
      console.error('获取Redis配置失败:', error);
      // 模拟数据
      const mockConfig: RedisConfig = {
        id: 1,
        name: '默认Redis',
        host: 'localhost',
        port: 6379,
        password: '',
        db: 0,
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

  const handleOpenDialog = (config?: RedisConfig) => {
    if (config) {
      setEditingConfig(config);
      setFormData({ ...config });
    } else {
      setEditingConfig(null);
      setFormData({
        name: '',
        host: 'localhost',
        port: 6379,
        password: '',
        db: 0,
        is_active: true,
        is_default: false,
      });
    }
    setDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      if (editingConfig) {
        const response = await redisApi.updateConfig(editingConfig.id, formData);
        if (response.code === 200) {
          fetchData();
        }
      } else {
        const response = await redisApi.createConfig(formData);
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
      await redisApi.deleteConfig(id);
      fetchData();
    } catch (error) {
      console.error('删除配置失败:', error);
    }
  };

  const handleTest = async (id: number) => {
    setTestingId(id);
    try {
      const response = await redisApi.testConnection(id);
      setConnectionStatus((prev) => ({ ...prev, [id]: response.data.success }));
      alert(response.data.message);
    } catch (error) {
      setConnectionStatus((prev) => ({ ...prev, [id]: false }));
      alert('连接测试失败: ' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setTestingId(null);
    }
  };

  const handleSetDefault = async (id: number) => {
    try {
      const config = configs.find((c) => c.id === id);
      if (config) {
        await redisApi.updateCurrentConfig(config);
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
          <h1 className="text-2xl font-bold text-slate-100">Redis配置</h1>
          <p className="text-slate-400 mt-1">管理Redis缓存服务器连接配置</p>
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
        <Card className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border-red-500/30">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
                  <Database className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-slate-100">当前Redis配置</h3>
                  <p className="text-slate-400">
                    {currentConfig.name} · {currentConfig.host}:{currentConfig.port} · DB {currentConfig.db}
                  </p>
                </div>
              </div>
              <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                <CheckCircle2 className="w-3 h-3 mr-1" />
                已连接
              </Badge>
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
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
                    <Server className="w-5 h-5 text-white" />
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
                      Redis {config.host}:{config.port}
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
                  <Hash className="w-4 h-4" />
                  <span>数据库: {config.db}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <Lock className="w-4 h-4" />
                  <span>{config.password ? '已设置密码' : '无密码'}</span>
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
                placeholder="例如：生产环境Redis"
                className="bg-slate-800 border-slate-700 text-slate-200"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-300">主机</Label>
                <div className="relative">
                  <Server className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <Input
                    value={formData.host}
                    onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                    placeholder="localhost"
                    className="bg-slate-800 border-slate-700 text-slate-200 pl-10"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300">端口</Label>
                <Input
                  type="number"
                  value={formData.port}
                  onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                  placeholder="6379"
                  className="bg-slate-800 border-slate-700 text-slate-200"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">密码（可选）</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="无密码请留空"
                  className="bg-slate-800 border-slate-700 text-slate-200 pl-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">数据库编号</Label>
              <div className="relative">
                <Hash className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input
                  type="number"
                  value={formData.db}
                  onChange={(e) => setFormData({ ...formData, db: parseInt(e.target.value) })}
                  placeholder="0"
                  min={0}
                  max={15}
                  className="bg-slate-800 border-slate-700 text-slate-200 pl-10"
                />
              </div>
              <p className="text-xs text-slate-500">Redis数据库编号，范围 0-15</p>
            </div>
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
    </div>
  );
}
