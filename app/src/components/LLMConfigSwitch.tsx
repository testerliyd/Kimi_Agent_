import React, { useState, useEffect } from 'react';
import { Switch, Select, Slider, Tooltip, Badge } from 'antd';
import { RobotOutlined, SettingOutlined, InfoCircleOutlined } from '@ant-design/icons';

interface LLMConfig {
  enabled: boolean;
  provider: string;
  model: string;
  temperature: number;
  maxTokens: number;
  useRAG: boolean;
  ragKnowledgeBase?: string;
}

interface LLMConfigSwitchProps {
  value?: LLMConfig;
  onChange?: (config: LLMConfig) => void;
  showDetails?: boolean;
  title?: string;
  description?: string;
}

const providers = [
  { value: 'openai', label: 'OpenAI', models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'] },
  { value: 'anthropic', label: 'Anthropic', models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'] },
  { value: 'azure', label: 'Azure OpenAI', models: ['gpt-4', 'gpt-35-turbo'] },
  { value: 'ollama', label: 'Ollama', models: ['llama2', 'codellama', 'mistral'] },
  { value: 'custom', label: '自定义', models: ['custom'] },
];

const defaultConfig: LLMConfig = {
  enabled: false,
  provider: 'openai',
  model: 'gpt-4',
  temperature: 0.7,
  maxTokens: 2000,
  useRAG: false,
};

export default function LLMConfigSwitch({
  value,
  onChange,
  showDetails = true,
  title = 'AI 智能辅助',
  description = '启用大模型辅助生成或执行测试用例',
}: LLMConfigSwitchProps) {
  const [config, setConfig] = useState<LLMConfig>(value || defaultConfig);
  const [availableModels, setAvailableModels] = useState<string[]>(providers[0].models);

  useEffect(() => {
    if (value) {
      setConfig(value);
    }
  }, [value]);

  useEffect(() => {
    const provider = providers.find(p => p.value === config.provider);
    setAvailableModels(provider?.models || []);
    if (provider && !provider.models.includes(config.model)) {
      updateConfig({ model: provider.models[0] });
    }
  }, [config.provider]);

  const updateConfig = (updates: Partial<LLMConfig>) => {
    const newConfig = { ...config, ...updates };
    setConfig(newConfig);
    onChange?.(newConfig);
  };

  return (
    <div className="llm-config-switch bg-slate-900/60 rounded-lg border border-slate-700/50 overflow-hidden">
      {/* 主开关 */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700/50 bg-gradient-to-r from-purple-500/10 to-pink-500/10">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all ${
            config.enabled 
              ? 'bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg shadow-purple-500/30' 
              : 'bg-slate-700'
          }`}>
            <RobotOutlined className={`text-lg ${config.enabled ? 'text-white' : 'text-slate-400'}`} />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              {title}
              <Tooltip title={description}>
                <InfoCircleOutlined className="text-slate-500 text-xs cursor-help" />
              </Tooltip>
            </h4>
            <p className="text-xs text-slate-400 mt-0.5">
              {config.enabled ? 'AI 辅助已启用' : 'AI 辅助已关闭'}
            </p>
          </div>
        </div>
        <Switch
          checked={config.enabled}
          onChange={(checked) => updateConfig({ enabled: checked })}
          className={config.enabled ? 'bg-purple-500' : ''}
          checkedChildren="开启"
          unCheckedChildren="关闭"
        />
      </div>

      {/* 详细配置 */}
      {showDetails && config.enabled && (
        <div className="p-4 space-y-4 animate-in fade-in slide-in-from-top-2 duration-300">
          {/* 提供商选择 */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-400 mb-1.5 block">AI 提供商</label>
              <Select
                value={config.provider}
                onChange={(value) => updateConfig({ provider: value })}
                className="w-full"
                options={providers.map(p => ({ value: p.value, label: p.label }))}
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1.5 block">模型</label>
              <Select
                value={config.model}
                onChange={(value) => updateConfig({ model: value })}
                className="w-full"
                options={availableModels.map(m => ({ value: m, label: m }))}
              />
            </div>
          </div>

          {/* 温度设置 */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs text-slate-400">创造性 (Temperature)</label>
              <span className="text-xs text-purple-400 font-medium">{config.temperature}</span>
            </div>
            <Slider
              value={config.temperature}
              onChange={(value) => updateConfig({ temperature: value })}
              min={0}
              max={1}
              step={0.1}
              className="text-purple-500"
              tooltip={{ formatter: (v) => `${v} - ${(v as number) < 0.3 ? '精确' : (v as number) > 0.7 ? '创意' : '平衡'}` }}
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>精确 (0)</span>
              <span>平衡 (0.5)</span>
              <span>创意 (1)</span>
            </div>
          </div>

          {/* 最大Token */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs text-slate-400">最大 Token 数</label>
              <span className="text-xs text-purple-400 font-medium">{config.maxTokens}</span>
            </div>
            <Slider
              value={config.maxTokens}
              onChange={(value) => updateConfig({ maxTokens: value })}
              min={500}
              max={8000}
              step={500}
              className="text-purple-500"
            />
          </div>

          {/* RAG 知识库 */}
          <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
            <div className="flex items-center gap-2">
              <SettingOutlined className="text-slate-400" />
              <div>
                <span className="text-sm text-slate-200">RAG 知识库增强</span>
                <p className="text-[10px] text-slate-500">使用历史测试经验优化生成结果</p>
              </div>
            </div>
            <Switch
              checked={config.useRAG}
              onChange={(checked) => updateConfig({ useRAG: checked })}
              size="small"
            />
          </div>

          {config.useRAG && (
            <div className="animate-in fade-in slide-in-from-top-2">
              <label className="text-xs text-slate-400 mb-1.5 block">选择知识库</label>
              <Select
                value={config.ragKnowledgeBase}
                onChange={(value) => updateConfig({ ragKnowledgeBase: value })}
                className="w-full"
                placeholder="选择要使用的知识库"
                options={[
                  { value: 'default', label: '默认知识库' },
                  { value: 'team', label: '团队经验库' },
                  { value: 'project', label: '项目专属库' },
                ]}
              />
            </div>
          )}

          {/* 状态提示 */}
          <div className="flex items-center gap-2 p-2 bg-purple-500/10 rounded-lg">
            <Badge status="processing" className="bg-purple-500" />
            <span className="text-xs text-purple-300">
              配置已保存，将在下次生成/执行时生效
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
