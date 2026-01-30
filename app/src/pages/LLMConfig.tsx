import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { llmApi } from '@/services/api';
import type { LLMConfig, LLMProvider } from '@/types';
import {
  Plus,
  Edit2,
  Trash2,
  Check,
  X,
  TestTube,
  Star,
  Cpu,
  Key,
  Link,
  Settings,
  Thermometer,
  Hash,
  Clock,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const providers: { code: LLMProvider; name: string }[] = [
  { code: 'openai', name: 'OpenAI' },
  { code: 'azure', name: 'Azure OpenAI' },
  { code: 'anthropic', name: 'Anthropic' },
  { code: 'baidu', name: '百度文心' },
  { code: 'alibaba', name: '阿里通义' },
  { code: 'zhipu', name: '智谱AI' },
  { code: 'moonshot', name: 'Moonshot' },
  { code: 'custom', name: '自定义' },
];

export default function LLMConfig() {
  const [configs, setConfigs] = useState<LLMConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingConfig, setEditingConfig] = useState<LLMConfig | null>(null);
  const [formData, setFormData] = useState<Partial<LLMConfig>>({
    name: '',
    provider: 'openai',
    api_key: '',
    api_base: '',
    model_name: '',
    temperature: 0.7,
    max_tokens: 2048,
    timeout: 30,
    is_active: true,
    is_default: false,
  });
  const [testingId, setTestingId] = useState<number | null>(null);

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      const response = await llmApi.getConfigs();
      if (response.code === 200) {
        setConfigs(response.data);
      }
    } catch (error) {
      console.error('获取大模型配置失败:', error);
      // 模拟数据
      setConfigs([
        {
          id: 1,
          name: 'OpenAI GPT-4',
          provider: 'openai',
          api_key: 'sk-****',
          api_base: 'https://api.openai.com/v1',
          model_name: 'gpt-4',
          temperature: 0.7,
          max_tokens: 2048,
          timeout: 30,
          is_active: true,
          is_default: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (config?: LLMConfig) => {
    if (config) {
      setEditingConfig(config);
      setFormData({ ...config });
    } else {
      setEditingConfig(null);
      setFormData({
        name: '',
        provider: 'openai',
        api_key: '',
        api_base: '',
        model_name: '',
        temperature: 0.7,
        max_tokens: 2048,
        timeout: 30,
        is_active: true,
        is_default: false,
      });
    }
    setDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      if (editingConfig) {
        const response = await llmApi.updateConfig(editingConfig.id, formData);
        if (response.code === 200) {
          fetchConfigs();
        }
      } else {
        const response = await llmApi.createConfig(formData);
        if (response.code === 200) {
          fetchConfigs();
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
      await llmApi.deleteConfig(id);
      fetchConfigs();
    } catch (error) {
      console.error('删除配置失败:', error);
    }
  };

  const handleTest = async (id: number) => {
    setTestingId(id);
    try {
      const response = await llmApi.testConfig(id);
      alert(response.data.message);
    } catch (error) {
      alert('测试失败: ' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setTestingId(null);
    }
  };

  const handleSetDefault = async (id: number) => {
    try {
      await llmApi.setDefaultConfig(id);
      fetchConfigs();
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
          <h1 className="text-2xl font-bold text-slate-100">大模型配置</h1>
          <p className="text-slate-400 mt-1">管理AI大模型API配置，支持多种主流模型提供商</p>
        </div>
        <Button
          onClick={() => handleOpenDialog()}
          className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          新建配置
        </Button>
      </div>

      {/* 配置列表 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {configs.map((config) => (
          <Card
            key={config.id}
            className={cn(
              'bg-slate-900/50 backdrop-blur-sm border-cyan-500/20 hover:border-cyan-500/40 transition-all duration-300',
              config.is_default && 'border-cyan-500/50 shadow-[0_0_20px_rgba(34,211,238,0.1)]'
            )}
          >
            <CardHeader className="pb-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                    <Cpu className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                      {config.name}
                      {config.is_default && (
                        <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                          <Star className="w-3 h-3 mr-1" />
                          默认
                        </Badge>
                      )}
                    </CardTitle>
                    <p className="text-sm text-slate-400">
                      {providers.find((p) => p.code === config.provider)?.name || config.provider}
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
                  <Link className="w-4 h-4" />
                  <span className="truncate">{config.api_base}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <Settings className="w-4 h-4" />
                  <span>{config.model_name}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <Thermometer className="w-4 h-4" />
                  <span>Temperature: {config.temperature}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <Hash className="w-4 h-4" />
                  <span>Max Tokens: {config.max_tokens}</span>
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
                  测试
                </Button>
                {!config.is_default && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleSetDefault(config.id)}
                    className="border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/10"
                  >
                    <Star className="w-4 h-4 mr-1" />
                    设为默认
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

      {/* 新建/编辑对话框 */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="bg-slate-900 border-cyan-500/30 max-w-lg max-h-[90vh] overflow-y-auto">
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
                placeholder="例如：OpenAI GPT-4"
                className="bg-slate-800 border-slate-700 text-slate-200"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">提供商</Label>
              <Select
                value={formData.provider}
                onValueChange={(value) => setFormData({ ...formData, provider: value as LLMProvider })}
              >
                <SelectTrigger className="bg-slate-800 border-slate-700 text-slate-200">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700">
                  {providers.map((p) => (
                    <SelectItem key={p.code} value={p.code} className="text-slate-200">
                      {p.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">API Key</Label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input
                  value={formData.api_key}
                  onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                  placeholder="sk-..."
                  className="bg-slate-800 border-slate-700 text-slate-200 pl-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">API Base URL</Label>
              <Input
                value={formData.api_base}
                onChange={(e) => setFormData({ ...formData, api_base: e.target.value })}
                placeholder="https://api.openai.com/v1"
                className="bg-slate-800 border-slate-700 text-slate-200"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">模型名称</Label>
              <Input
                value={formData.model_name}
                onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
                placeholder="gpt-4"
                className="bg-slate-800 border-slate-700 text-slate-200"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">
                Temperature: {formData.temperature}
              </Label>
              <Slider
                value={[formData.temperature || 0.7]}
                onValueChange={(value) => setFormData({ ...formData, temperature: value[0] })}
                min={0}
                max={2}
                step={0.1}
                className="py-2"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">Max Tokens</Label>
              <Input
                type="number"
                value={formData.max_tokens}
                onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
                className="bg-slate-800 border-slate-700 text-slate-200"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">超时时间（秒）</Label>
              <div className="relative">
                <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input
                  type="number"
                  value={formData.timeout}
                  onChange={(e) => setFormData({ ...formData, timeout: parseInt(e.target.value) })}
                  className="bg-slate-800 border-slate-700 text-slate-200 pl-10"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <Label className="text-slate-300">设为默认</Label>
              <Switch
                checked={formData.is_default}
                onCheckedChange={(checked) => setFormData({ ...formData, is_default: checked })}
                className="data-[state=checked]:bg-cyan-500"
              />
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
