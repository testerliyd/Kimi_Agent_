import { useEffect, useState } from 'react';
import { Button, Card, Input, Modal, Form, Select, Tag, Space, Tooltip, message, Table, Tabs, Badge, Progress, Radio } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined, PauseCircleOutlined, CopyOutlined, ApiOutlined, ThunderboltOutlined, BarChartOutlined, LineChartOutlined } from '@ant-design/icons';
import { apiTestApi, perfTestApi } from '@/services/api';
import type { ApiDefinition, ApiTestCase, ApiTestJob, PerfTestScenario, PerfTestJob } from '@/types';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

export default function AutomationTest() {
  const [activeTab, setActiveTab] = useState('api');
  const [apiDefinitions, setApiDefinitions] = useState<ApiDefinition[]>([]);
  const [apiTestCases, setApiTestCases] = useState<ApiTestCase[]>([]);
  const [apiTestJobs, setApiTestJobs] = useState<ApiTestJob[]>([]);
  const [perfScenarios, setPerfScenarios] = useState<PerfTestScenario[]>([]);
  const [perfTestJobs, setPerfTestJobs] = useState<PerfTestJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [searchText, setSearchText] = useState('');
  const [isApiCaseModalOpen, setIsApiCaseModalOpen] = useState(false);
  const [isApiDefModalOpen, setIsApiDefModalOpen] = useState(false);
  const [isPerfScenarioModalOpen, setIsPerfScenarioModalOpen] = useState(false);
  const [editingApiCase, setEditingApiCase] = useState<ApiTestCase | null>(null);
  const [editingApiDef, setEditingApiDef] = useState<ApiDefinition | null>(null);
  const [editingPerfScenario, setEditingPerfScenario] = useState<PerfTestScenario | null>(null);
  const [apiCaseForm] = Form.useForm();
  const [apiDefForm] = Form.useForm();
  const [perfScenarioForm] = Form.useForm();

  const fetchApiDefinitions = async () => {
    try {
      const response = await apiTestApi.getApiDefinitions();
      if (response.code === 200) {
        setApiDefinitions(response.data.results || []);
      }
    } catch (error) {
      message.error('获取API定义失败');
    }
  };

  const fetchApiTestCases = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      const response = await apiTestApi.getApiTestCases({
        page,
        page_size: pageSize,
        search: searchText || undefined,
      });
      if (response.code === 200) {
        setApiTestCases(response.data.results || []);
        setPagination({
          current: page,
          pageSize,
          total: response.data.count || 0,
        });
      }
    } catch (error) {
      message.error('获取API测试用例失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchApiTestJobs = async () => {
    try {
      const response = await apiTestApi.getApiTestJobs();
      if (response.code === 200) {
        setApiTestJobs(response.data.results || []);
      }
    } catch (error) {
      console.error('获取API测试任务失败');
    }
  };

  const fetchPerfScenarios = async () => {
    try {
      const response = await perfTestApi.getScenarios();
      if (response.code === 200) {
        setPerfScenarios(response.data.results || []);
      }
    } catch (error) {
      message.error('获取性能测试场景失败');
    }
  };

  const fetchPerfTestJobs = async () => {
    try {
      const response = await perfTestApi.getPerfTestJobs();
      if (response.code === 200) {
        setPerfTestJobs(response.data.results || []);
      }
    } catch (error) {
      console.error('获取性能测试任务失败');
    }
  };

  useEffect(() => {
    if (activeTab === 'api') {
      fetchApiTestCases();
      fetchApiDefinitions();
      fetchApiTestJobs();
    } else if (activeTab === 'performance') {
      fetchPerfScenarios();
      fetchPerfTestJobs();
    }
  }, [activeTab, searchText]);

  // API测试用例操作
  const handleCreateApiCase = () => {
    setEditingApiCase(null);
    apiCaseForm.resetFields();
    setIsApiCaseModalOpen(true);
  };

  const handleEditApiCase = (testCase: ApiTestCase) => {
    setEditingApiCase(testCase);
    apiCaseForm.setFieldsValue(testCase);
    setIsApiCaseModalOpen(true);
  };

  const handleDeleteApiCase = async (id: number) => {
    try {
      await apiTestApi.deleteApiTestCase(id);
      message.success('删除成功');
      fetchApiTestCases(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleRunApiCase = async (id: number) => {
    try {
      const response = await apiTestApi.runTest(id);
      if (response.code === 200) {
        message.success('测试执行成功');
        fetchApiTestCases(pagination.current, pagination.pageSize);
      }
    } catch (error) {
      message.error('测试执行失败');
    }
  };

  const handleSubmitApiCase = async (values: any) => {
    try {
      if (editingApiCase) {
        await apiTestApi.updateApiTestCase(editingApiCase.id, values);
        message.success('更新成功');
      } else {
        await apiTestApi.createApiTestCase(values);
        message.success('创建成功');
      }
      setIsApiCaseModalOpen(false);
      fetchApiTestCases(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error(editingApiCase ? '更新失败' : '创建失败');
    }
  };

  // API定义操作
  const handleCreateApiDef = () => {
    setEditingApiDef(null);
    apiDefForm.resetFields();
    setIsApiDefModalOpen(true);
  };

  const handleSubmitApiDef = async (values: any) => {
    try {
      if (editingApiDef) {
        await apiTestApi.updateApiDefinition(editingApiDef.id, values);
        message.success('更新成功');
      } else {
        await apiTestApi.createApiDefinition(values);
        message.success('创建成功');
      }
      setIsApiDefModalOpen(false);
      fetchApiDefinitions();
    } catch (error) {
      message.error(editingApiDef ? '更新失败' : '创建失败');
    }
  };

  // 性能测试场景操作
  const handleCreatePerfScenario = () => {
    setEditingPerfScenario(null);
    perfScenarioForm.resetFields();
    setIsPerfScenarioModalOpen(true);
  };

  const handleEditPerfScenario = (scenario: PerfTestScenario) => {
    setEditingPerfScenario(scenario);
    perfScenarioForm.setFieldsValue(scenario);
    setIsPerfScenarioModalOpen(true);
  };

  const handleDeletePerfScenario = async (id: number) => {
    try {
      await perfTestApi.deleteScenario(id);
      message.success('删除成功');
      fetchPerfScenarios();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmitPerfScenario = async (values: any) => {
    try {
      if (editingPerfScenario) {
        await perfTestApi.updateScenario(editingPerfScenario.id, values);
        message.success('更新成功');
      } else {
        await perfTestApi.createScenario(values);
        message.success('创建成功');
      }
      setIsPerfScenarioModalOpen(false);
      fetchPerfScenarios();
    } catch (error) {
      message.error(editingPerfScenario ? '更新失败' : '创建失败');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'default',
      running: 'processing',
      passed: 'success',
      failed: 'error',
      completed: 'success',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      pending: '待执行',
      running: '执行中',
      passed: '通过',
      failed: '失败',
      completed: '已完成',
    };
    return texts[status] || status;
  };

  const apiCaseColumns = [
    {
      title: '用例名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: ApiTestCase) => (
        <div>
          <ApiOutlined className="mr-2 text-blue-500" />
          <span className="font-medium">{text}</span>
        </div>
      ),
    },
    {
      title: '请求方法',
      dataIndex: 'method',
      key: 'method',
      width: 100,
      render: (method: string) => (
        <Tag color={method === 'GET' ? 'green' : method === 'POST' ? 'blue' : method === 'PUT' ? 'orange' : 'red'}>
          {method}
        </Tag>
      ),
    },
    {
      title: '请求URL',
      dataIndex: 'url',
      key: 'url',
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Badge status={getStatusColor(status) as any} text={getStatusText(status)} />
      ),
    },
    {
      title: '最后执行',
      dataIndex: 'last_executed_at',
      key: 'last_executed_at',
      width: 150,
      render: (date: string) => date ? dayjs(date).format('MM-DD HH:mm') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (_: any, record: ApiTestCase) => (
        <Space size="small">
          <Tooltip title="执行">
            <Button type="text" icon={<PlayCircleOutlined style={{ color: '#52c41a' }} />} size="small" onClick={() => handleRunApiCase(record.id)} />
          </Tooltip>
          <Tooltip title="编辑">
            <Button type="text" icon={<EditOutlined />} size="small" onClick={() => handleEditApiCase(record)} />
          </Tooltip>
          <Tooltip title="复制">
            <Button type="text" icon={<CopyOutlined />} size="small" />
          </Tooltip>
          <Tooltip title="删除">
            <Button type="text" danger icon={<DeleteOutlined />} size="small" onClick={() => handleDeleteApiCase(record.id)} />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const apiJobColumns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Badge status={getStatusColor(status) as any} text={getStatusText(status)} />
      ),
    },
    {
      title: '进度',
      key: 'progress',
      width: 150,
      render: (_: any, record: ApiTestJob) => (
        <Progress percent={record.progress || 0} size="small" />
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => dayjs(date).format('MM-DD HH:mm'),
    },
  ];

  const perfScenarioColumns = [
    {
      title: '场景名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <div>
          <ThunderboltOutlined className="mr-2 text-yellow-500" />
          <span className="font-medium">{text}</span>
        </div>
      ),
    },
    {
      title: '并发数',
      dataIndex: 'concurrent_users',
      key: 'concurrent_users',
      width: 100,
    },
    {
      title: '持续时间',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
      render: (duration: number) => `${duration}秒`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Badge status={getStatusColor(status) as any} text={getStatusText(status)} />
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: PerfTestScenario) => (
        <Space size="small">
          <Tooltip title="执行">
            <Button type="text" icon={<PlayCircleOutlined style={{ color: '#52c41a' }} />} size="small" />
          </Tooltip>
          <Tooltip title="编辑">
            <Button type="text" icon={<EditOutlined />} size="small" onClick={() => handleEditPerfScenario(record)} />
          </Tooltip>
          <Tooltip title="删除">
            <Button type="text" danger icon={<DeleteOutlined />} size="small" onClick={() => handleDeletePerfScenario(record.id)} />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const perfJobColumns = [
    {
      title: '任务名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Badge status={getStatusColor(status) as any} text={getStatusText(status)} />
      ),
    },
    {
      title: 'TPS',
      dataIndex: 'tps',
      key: 'tps',
      width: 100,
    },
    {
      title: '平均响应时间',
      dataIndex: 'avg_response_time',
      key: 'avg_response_time',
      width: 120,
      render: (time: number) => `${time}ms`,
    },
    {
      title: '错误率',
      dataIndex: 'error_rate',
      key: 'error_rate',
      width: 100,
      render: (rate: number) => `${rate}%`,
    },
  ];

  return (
    <div className="p-6">
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane
          tab={<span><ApiOutlined /> 接口测试</span>}
          key="api"
        >
          <Tabs type="card">
            <TabPane tab="测试用例" key="api-cases">
              <Card
                title={
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold m-0">API测试用例</h2>
                      <p className="text-gray-400 text-sm m-0 mt-1">管理接口测试用例</p>
                    </div>
                    <Space>
                      <Button onClick={handleCreateApiDef}>管理API定义</Button>
                      <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateApiCase}>
                        新建用例
                      </Button>
                    </Space>
                  </div>
                }
              >
                <div className="flex gap-4 mb-4">
                  <Search
                    placeholder="搜索用例名称"
                    allowClear
                    onSearch={(value) => setSearchText(value)}
                    style={{ width: 300 }}
                  />
                </div>

                <Table
                  columns={apiCaseColumns}
                  dataSource={apiTestCases}
                  rowKey="id"
                  loading={loading}
                  pagination={pagination}
                  onChange={(newPagination) => fetchApiTestCases(newPagination.current, newPagination.pageSize)}
                />
              </Card>
            </TabPane>

            <TabPane tab="执行任务" key="api-jobs">
              <Card title="API测试任务">
                <Table
                  columns={apiJobColumns}
                  dataSource={apiTestJobs}
                  rowKey="id"
                />
              </Card>
            </TabPane>
          </Tabs>
        </TabPane>

        <TabPane
          tab={<span><ThunderboltOutlined /> 性能测试</span>}
          key="performance"
        >
          <Tabs type="card">
            <TabPane tab="测试场景" key="perf-scenarios">
              <Card
                title={
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-bold m-0">性能测试场景</h2>
                      <p className="text-gray-400 text-sm m-0 mt-1">管理性能测试场景配置</p>
                    </div>
                    <Button type="primary" icon={<PlusOutlined />} onClick={handleCreatePerfScenario}>
                      新建场景
                    </Button>
                  </div>
                }
              >
                <Table
                  columns={perfScenarioColumns}
                  dataSource={perfScenarios}
                  rowKey="id"
                />
              </Card>
            </TabPane>

            <TabPane tab="执行任务" key="perf-jobs">
              <Card title="性能测试任务">
                <Table
                  columns={perfJobColumns}
                  dataSource={perfTestJobs}
                  rowKey="id"
                />
              </Card>
            </TabPane>
          </Tabs>
        </TabPane>
      </Tabs>

      {/* API测试用例 Modal */}
      <Modal
        title={editingApiCase ? '编辑API测试用例' : '新建API测试用例'}
        open={isApiCaseModalOpen}
        onCancel={() => setIsApiCaseModalOpen(false)}
        onOk={() => apiCaseForm.submit()}
        width={800}
      >
        <Form form={apiCaseForm} layout="vertical" onFinish={handleSubmitApiCase}>
          <Form.Item name="name" label="用例名称" rules={[{ required: true }]}>
            <Input placeholder="请输入用例名称" />
          </Form.Item>

          <div className="flex gap-4">
            <Form.Item name="method" label="请求方法" className="flex-1" initialValue="GET">
              <Select>
                <Option value="GET">GET</Option>
                <Option value="POST">POST</Option>
                <Option value="PUT">PUT</Option>
                <Option value="DELETE">DELETE</Option>
                <Option value="PATCH">PATCH</Option>
              </Select>
            </Form.Item>

            <Form.Item name="api_definition" label="API定义" className="flex-1">
              <Select placeholder="选择API定义">
                {apiDefinitions.map((def) => (
                  <Option key={def.id} value={def.id}>{def.name}</Option>
                ))}
              </Select>
            </Form.Item>
          </div>

          <Form.Item name="url" label="请求URL" rules={[{ required: true }]}>
            <Input placeholder="请输入请求URL" />
          </Form.Item>

          <Form.Item name="headers" label="请求头">
            <TextArea rows={3} placeholder='{"Content-Type": "application/json"}' />
          </Form.Item>

          <Form.Item name="body" label="请求体">
            <TextArea rows={4} placeholder="请输入请求体（JSON格式）" />
          </Form.Item>

          <Form.Item name="expected_response" label="预期响应">
            <TextArea rows={3} placeholder="请输入预期响应" />
          </Form.Item>
        </Form>
      </Modal>

      {/* API定义 Modal */}
      <Modal
        title="API定义管理"
        open={isApiDefModalOpen}
        onCancel={() => setIsApiDefModalOpen(false)}
        footer={null}
        width={900}
      >
        <Table
          dataSource={apiDefinitions}
          rowKey="id"
          columns={[
            { title: '名称', dataIndex: 'name', key: 'name' },
            { title: '方法', dataIndex: 'method', key: 'method' },
            { title: '路径', dataIndex: 'path', key: 'path' },
            {
              title: '操作',
              key: 'action',
              render: (_: any, record: ApiDefinition) => (
                <Space>
                  <Button type="text" icon={<EditOutlined />} size="small" />
                  <Button type="text" danger icon={<DeleteOutlined />} size="small" />
                </Space>
              ),
            },
          ]}
        />
      </Modal>

      {/* 性能测试场景 Modal */}
      <Modal
        title={editingPerfScenario ? '编辑性能测试场景' : '新建性能测试场景'}
        open={isPerfScenarioModalOpen}
        onCancel={() => setIsPerfScenarioModalOpen(false)}
        onOk={() => perfScenarioForm.submit()}
        width={700}
      >
        <Form form={perfScenarioForm} layout="vertical" onFinish={handleSubmitPerfScenario}>
          <Form.Item name="name" label="场景名称" rules={[{ required: true }]}>
            <Input placeholder="请输入场景名称" />
          </Form.Item>

          <div className="flex gap-4">
            <Form.Item name="concurrent_users" label="并发用户数" className="flex-1" initialValue={100}>
              <Input type="number" placeholder="并发用户数" />
            </Form.Item>

            <Form.Item name="duration" label="持续时间(秒)" className="flex-1" initialValue={60}>
              <Input type="number" placeholder="持续时间" />
            </Form.Item>
          </div>

          <div className="flex gap-4">
            <Form.Item name="ramp_up" label="Ramp Up(秒)" className="flex-1" initialValue={10}>
              <Input type="number" placeholder="Ramp Up时间" />
            </Form.Item>

            <Form.Item name="think_time" label="思考时间(秒)" className="flex-1" initialValue={1}>
              <Input type="number" placeholder="思考时间" />
            </Form.Item>
          </div>

          <Form.Item name="target_url" label="目标URL" rules={[{ required: true }]}>
            <Input placeholder="请输入目标URL" />
          </Form.Item>

          <Form.Item name="description" label="场景描述">
            <TextArea rows={3} placeholder="请输入场景描述" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
