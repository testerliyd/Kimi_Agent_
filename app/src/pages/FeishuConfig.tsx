import { useEffect, useState } from 'react';
import { Button, Card, Input, Modal, Form, Switch, Tag, Space, Tooltip, message, Popconfirm, Table, Tabs, Badge, List, Avatar } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SendOutlined, CopyOutlined, NotificationOutlined, MessageOutlined, RobotOutlined, LinkOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { feishuApi } from '@/services/api';
import type { FeishuConfig } from '@/types';
import dayjs from 'dayjs';

const { Search } = Input;
const { TextArea } = Input;
const { TabPane } = Tabs;

interface FeishuFormData {
  name: string;
  webhook_url: string;
  secret?: string;
  notify_events?: string[];
  is_active?: boolean;
  description?: string;
}

export default function FeishuConfigPage() {
  const [configs, setConfigs] = useState<FeishuConfig[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [bindings, setBindings] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isTemplateModalOpen, setIsTemplateModalOpen] = useState(false);
  const [editingConfig, setEditingConfig] = useState<FeishuConfig | null>(null);
  const [editingTemplate, setEditingTemplate] = useState<any | null>(null);
  const [form] = Form.useForm();
  const [templateForm] = Form.useForm();

  const fetchConfigs = async () => {
    setLoading(true);
    try {
      const response = await feishuApi.getConfigs();
      if (response.code === 200) {
        setConfigs(response.data.results || []);
      }
    } catch (error) {
      message.error('获取飞书配置失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await feishuApi.getTemplates();
      if (response.code === 200) {
        setTemplates(response.data || []);
      }
    } catch (error) {
      console.error('获取消息模板失败');
    }
  };

  const fetchBindings = async () => {
    try {
      const response = await feishuApi.getBindings();
      if (response.code === 200) {
        setBindings(response.data || []);
      }
    } catch (error) {
      console.error('获取绑定配置失败');
    }
  };

  useEffect(() => {
    fetchConfigs();
    fetchTemplates();
    fetchBindings();
  }, []);

  const handleCreate = () => {
    setEditingConfig(null);
    form.resetFields();
    form.setFieldsValue({ is_active: true, notify_events: ['bug_created', 'bug_resolved'] });
    setIsModalOpen(true);
  };

  const handleEdit = (config: FeishuConfig) => {
    setEditingConfig(config);
    form.setFieldsValue({
      ...config,
      notify_events: config.notify_events || [],
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await feishuApi.deleteConfig(id);
      message.success('删除成功');
      fetchConfigs();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async (values: FeishuFormData) => {
    try {
      if (editingConfig) {
        await feishuApi.updateConfig(editingConfig.id, values);
        message.success('更新成功');
      } else {
        await feishuApi.createConfig(values);
        message.success('创建成功');
      }
      setIsModalOpen(false);
      fetchConfigs();
    } catch (error) {
      message.error(editingConfig ? '更新失败' : '创建失败');
    }
  };

  const handleTestWebhook = async (id: number) => {
    try {
      const response = await feishuApi.testWebhook(id);
      if (response.code === 200) {
        message.success('测试消息发送成功');
      } else {
        message.error(response.message || '测试失败');
      }
    } catch (error) {
      message.error('测试失败');
    }
  };

  const eventOptions = [
    { label: 'Bug创建', value: 'bug_created' },
    { label: 'Bug分配', value: 'bug_assigned' },
    { label: 'Bug解决', value: 'bug_resolved' },
    { label: 'Bug关闭', value: 'bug_closed' },
    { label: '测试计划完成', value: 'test_plan_completed' },
    { label: '测试报告生成', value: 'report_generated' },
  ];

  const columns = [
    {
      title: '配置名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: FeishuConfig) => (
        <div>
          <RobotOutlined className="mr-2 text-blue-500" />
          <span className="font-medium">{text}</span>
          {record.is_default && <Tag color="blue" className="ml-2">默认</Tag>}
        </div>
      ),
    },
    {
      title: 'Webhook地址',
      dataIndex: 'webhook_url',
      key: 'webhook_url',
      ellipsis: true,
      render: (url: string) => (
        <span className="text-gray-400">{url.substring(0, 30)}...</span>
      ),
    },
    {
      title: '通知事件',
      dataIndex: 'notify_events',
      key: 'notify_events',
      render: (events: string[]) => (
        <div>
          {events?.map((event) => (
            <Tag key={event} size="small" className="mb-1">
              {eventOptions.find((e) => e.value === event)?.label || event}
            </Tag>
          ))}
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) => (
        <Badge status={isActive ? 'success' : 'default'} text={isActive ? '启用' : '禁用'} />
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: any, record: FeishuConfig) => (
        <Space size="small">
          <Tooltip title="测试Webhook">
            <Button
              type="text"
              icon={<SendOutlined style={{ color: '#52c41a' }} />}
              size="small"
              onClick={() => handleTestWebhook(record.id)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button type="text" icon={<EditOutlined />} size="small" onClick={() => handleEdit(record)} />
          </Tooltip>
          <Tooltip title="复制">
            <Button type="text" icon={<CopyOutlined />} size="small" />
          </Tooltip>
          <Popconfirm
            title="确认删除"
            onConfirm={() => handleDelete(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Button type="text" danger icon={<DeleteOutlined />} size="small" />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6">
      <Tabs defaultActiveKey="configs">
        <TabPane tab="机器人配置" key="configs">
          <Card
            title={
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold m-0">飞书机器人配置</h2>
                  <p className="text-gray-400 text-sm m-0 mt-1">配置飞书机器人Webhook，实现测试通知自动推送</p>
                </div>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  新建配置
                </Button>
              </div>
            }
          >
            <div className="flex gap-4 mb-4">
              <Search
                placeholder="搜索配置名称"
                allowClear
                onSearch={(value) => setSearchText(value)}
                style={{ width: 300 }}
              />
            </div>

            <Table
              columns={columns}
              dataSource={configs}
              rowKey="id"
              loading={loading}
            />
          </Card>
        </TabPane>

        <TabPane tab="消息模板" key="templates">
          <Card
            title={
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold m-0">消息模板</h2>
                  <p className="text-gray-400 text-sm m-0 mt-1">自定义飞书通知消息模板</p>
                </div>
                <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsTemplateModalOpen(true)}>
                  新建模板
                </Button>
              </div>
            }
          >
            <List
              grid={{ gutter: 16, column: 2 }}
              dataSource={templates}
              renderItem={(item) => (
                <List.Item>
                  <Card
                    title={item.name}
                    extra={
                      <Space>
                        <Button type="text" icon={<EditOutlined />} size="small" />
                        <Button type="text" danger icon={<DeleteOutlined />} size="small" />
                      </Space>
                    }
                  >
                    <p className="text-gray-400">{item.description}</p>
                    <pre className="bg-gray-800 p-2 rounded text-xs overflow-auto" style={{ maxHeight: 150 }}>
                      {item.content}
                    </pre>
                  </Card>
                </List.Item>
              )}
            />
          </Card>
        </TabPane>

        <TabPane tab="群聊绑定" key="bindings">
          <Card
            title={
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold m-0">群聊绑定</h2>
                  <p className="text-gray-400 text-sm m-0 mt-1">绑定飞书群聊，实现项目通知推送</p>
                </div>
                <Button type="primary" icon={<LinkOutlined />}>
                  绑定群聊
                </Button>
              </div>
            }
          >
            <List
              dataSource={bindings}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Button type="text" icon={<EditOutlined />} size="small">编辑</Button>,
                    <Button type="text" danger icon={<DeleteOutlined />} size="small">删除</Button>,
                  ]}
                >
                  <List.Item.Meta
                    avatar={<Avatar icon={<MessageOutlined />} />}
                    title={item.chat_name}
                    description={`绑定项目: ${item.project_name} | 创建时间: ${dayjs(item.created_at).format('YYYY-MM-DD')}`}
                  />
                </List.Item>
              )}
            />
          </Card>
        </TabPane>
      </Tabs>

      {/* 配置表单 Modal */}
      <Modal
        title={editingConfig ? '编辑飞书配置' : '新建飞书配置'}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        width={700}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="name"
            label="配置名称"
            rules={[{ required: true, message: '请输入配置名称' }]}
          >
            <Input placeholder="请输入配置名称，如：测试组通知" />
          </Form.Item>

          <Form.Item
            name="webhook_url"
            label="Webhook地址"
            rules={[{ required: true, message: '请输入Webhook地址' }]}
          >
            <Input.TextArea
              rows={2}
              placeholder="请输入飞书机器人Webhook地址"
            />
          </Form.Item>

          <Form.Item
            name="secret"
            label="签名密钥"
          >
            <Input.Password placeholder="如有签名密钥，请输入" />
          </Form.Item>

          <Form.Item
            name="notify_events"
            label="通知事件"
            rules={[{ required: true, message: '请选择通知事件' }]}
          >
            <Select mode="multiple" placeholder="请选择要通知的事件">
              {eventOptions.map((option) => (
                <Option key={option.value} value={option.value}>{option.label}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="is_active"
            label="启用状态"
            valuePropName="checked"
          >
            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
          </Form.Item>

          <Form.Item
            name="description"
            label="描述"
          >
            <TextArea rows={3} placeholder="请输入配置描述" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 模板表单 Modal */}
      <Modal
        title="消息模板"
        open={isTemplateModalOpen}
        onCancel={() => setIsTemplateModalOpen(false)}
        footer={null}
        width={800}
      >
        <Form form={templateForm} layout="vertical">
          <Form.Item name="name" label="模板名称" rules={[{ required: true }]}>
            <Input placeholder="请输入模板名称" />
          </Form.Item>
          <Form.Item name="event_type" label="事件类型" rules={[{ required: true }]}>
            <Select placeholder="选择事件类型">
              <Option value="bug_created">Bug创建</Option>
              <Option value="bug_resolved">Bug解决</Option>
              <Option value="test_completed">测试完成</Option>
            </Select>
          </Form.Item>
          <Form.Item name="content" label="模板内容" rules={[{ required: true }]}>
            <TextArea rows={10} placeholder="请输入模板内容，支持Markdown格式" />
          </Form.Item>
          <div className="text-gray-400 text-sm mb-4">
            <p>可用变量：</p>
            <ul className="list-disc list-inside">
              <li>{'{{bug.title}}'} - Bug标题</li>
              <li>{'{{bug.severity}}'} - 严重程度</li>
              <li>{'{{bug.reporter}}'} - 报告人</li>
              <li>{'{{bug.url}}'} - Bug链接</li>
            </ul>
          </div>
          <Form.Item>
            <Button type="primary">保存模板</Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
