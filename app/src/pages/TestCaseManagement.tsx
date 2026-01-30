import { useEffect, useState } from 'react';
import { Button, Card, Input, Modal, Form, Select, Tag, Space, Tooltip, message, Popconfirm, Table, Tabs, Badge } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined, CopyOutlined, FolderOutlined, FileTextOutlined, CheckCircleOutlined, CloseCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';
import { testcaseApi } from '@/services/api';
import type { TestCase, TestSuite, TestPlan } from '@/types';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

interface TestCaseFormData {
  name: string;
  case_no?: string;
  description?: string;
  pre_condition?: string;
  steps?: string;
  expected_result?: string;
  case_type?: string;
  priority?: string;
  status?: string;
  module?: string;
  project?: number;
}

export default function TestCaseManagement() {
  const [activeTab, setActiveTab] = useState('cases');
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [testSuites, setTestSuites] = useState<TestSuite[]>([]);
  const [testPlans, setTestPlans] = useState<TestPlan[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [isCaseModalOpen, setIsCaseModalOpen] = useState(false);
  const [isSuiteModalOpen, setIsSuiteModalOpen] = useState(false);
  const [isPlanModalOpen, setIsPlanModalOpen] = useState(false);
  const [editingCase, setEditingCase] = useState<TestCase | null>(null);
  const [editingSuite, setEditingSuite] = useState<TestSuite | null>(null);
  const [editingPlan, setEditingPlan] = useState<TestPlan | null>(null);
  const [caseForm] = Form.useForm();
  const [suiteForm] = Form.useForm();
  const [planForm] = Form.useForm();
  const [statistics, setStatistics] = useState<any>(null);

  const fetchTestCases = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      const response = await testcaseApi.getTestCases({
        page,
        page_size: pageSize,
        search: searchText || undefined,
        status: statusFilter || undefined,
      });
      if (response.code === 200) {
        setTestCases(response.data.results || []);
        setPagination({
          current: page,
          pageSize,
          total: response.data.count || 0,
        });
      }
    } catch (error) {
      message.error('获取测试用例失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchTestSuites = async () => {
    try {
      const response = await testcaseApi.getTestSuites();
      if (response.code === 200) {
        setTestSuites(response.data.results || []);
      }
    } catch (error) {
      message.error('获取测试套件失败');
    }
  };

  const fetchTestPlans = async () => {
    try {
      const response = await testcaseApi.getTestPlans();
      if (response.code === 200) {
        setTestPlans(response.data.results || []);
      }
    } catch (error) {
      message.error('获取测试计划失败');
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await testcaseApi.getStatistics();
      if (response.code === 200) {
        setStatistics(response.data);
      }
    } catch (error) {
      console.error('获取统计信息失败');
    }
  };

  useEffect(() => {
    if (activeTab === 'cases') {
      fetchTestCases();
      fetchStatistics();
    } else if (activeTab === 'suites') {
      fetchTestSuites();
    } else if (activeTab === 'plans') {
      fetchTestPlans();
    }
  }, [activeTab, searchText, statusFilter]);

  const handleSearch = (value: string) => {
    setSearchText(value);
    fetchTestCases(1);
  };

  const handleTableChange = (newPagination: any) => {
    fetchTestCases(newPagination.current, newPagination.pageSize);
  };

  // 测试用例操作
  const handleCreateCase = () => {
    setEditingCase(null);
    caseForm.resetFields();
    setIsCaseModalOpen(true);
  };

  const handleEditCase = (testCase: TestCase) => {
    setEditingCase(testCase);
    caseForm.setFieldsValue(testCase);
    setIsCaseModalOpen(true);
  };

  const handleDeleteCase = async (id: number) => {
    try {
      await testcaseApi.deleteTestCase(id);
      message.success('删除成功');
      fetchTestCases(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleExecuteCase = async (id: number, result: string) => {
    try {
      await testcaseApi.executeTestCase(id, { result });
      message.success('执行成功');
      fetchTestCases(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error('执行失败');
    }
  };

  const handleSubmitCase = async (values: TestCaseFormData) => {
    try {
      if (editingCase) {
        await testcaseApi.updateTestCase(editingCase.id, values);
        message.success('更新成功');
      } else {
        await testcaseApi.createTestCase(values);
        message.success('创建成功');
      }
      setIsCaseModalOpen(false);
      fetchTestCases(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error(editingCase ? '更新失败' : '创建失败');
    }
  };

  // 测试套件操作
  const handleCreateSuite = () => {
    setEditingSuite(null);
    suiteForm.resetFields();
    setIsSuiteModalOpen(true);
  };

  const handleEditSuite = (suite: TestSuite) => {
    setEditingSuite(suite);
    suiteForm.setFieldsValue(suite);
    setIsSuiteModalOpen(true);
  };

  const handleDeleteSuite = async (id: number) => {
    try {
      await testcaseApi.deleteTestSuite(id);
      message.success('删除成功');
      fetchTestSuites();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmitSuite = async (values: any) => {
    try {
      if (editingSuite) {
        await testcaseApi.updateTestSuite(editingSuite.id, values);
        message.success('更新成功');
      } else {
        await testcaseApi.createTestSuite(values);
        message.success('创建成功');
      }
      setIsSuiteModalOpen(false);
      fetchTestSuites();
    } catch (error) {
      message.error(editingSuite ? '更新失败' : '创建失败');
    }
  };

  // 测试计划操作
  const handleCreatePlan = () => {
    setEditingPlan(null);
    planForm.resetFields();
    setIsPlanModalOpen(true);
  };

  const handleStartPlan = async (id: number) => {
    try {
      await testcaseApi.startTestPlan(id);
      message.success('计划已开始');
      fetchTestPlans();
    } catch (error) {
      message.error('启动失败');
    }
  };

  const handleCompletePlan = async (id: number) => {
    try {
      await testcaseApi.completeTestPlan(id);
      message.success('计划已完成');
      fetchTestPlans();
    } catch (error) {
      message.error('完成失败');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'default',
      active: 'success',
      deprecated: 'warning',
      passed: 'success',
      failed: 'error',
      blocked: 'orange',
      pending: 'blue',
      running: 'processing',
      completed: 'success',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      draft: '草稿',
      active: '有效',
      deprecated: '废弃',
      passed: '通过',
      failed: '失败',
      blocked: '阻塞',
      pending: '待执行',
      running: '执行中',
      completed: '已完成',
    };
    return texts[status] || status;
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      high: 'red',
      medium: 'orange',
      low: 'green',
    };
    return colors[priority] || 'default';
  };

  const caseColumns = [
    {
      title: '用例编号',
      dataIndex: 'case_no',
      key: 'case_no',
      width: 120,
    },
    {
      title: '用例名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: TestCase) => (
        <div>
          <div className="font-medium">{text}</div>
          <div className="text-xs text-gray-400">{record.module}</div>
        </div>
      ),
    },
    {
      title: '类型',
      dataIndex: 'case_type',
      key: 'case_type',
      width: 100,
      render: (type: string) => {
        const typeMap: Record<string, string> = {
          functional: '功能',
          performance: '性能',
          security: '安全',
          compatibility: '兼容',
          usability: '易用',
        };
        return typeMap[type] || type;
      },
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority: string) => (
        <Tag color={getPriorityColor(priority)}>
          {priority === 'high' ? '高' : priority === 'medium' ? '中' : '低'}
        </Tag>
      ),
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
      title: '执行次数',
      dataIndex: 'execution_count',
      key: 'execution_count',
      width: 100,
      render: (count: number) => count || 0,
    },
    {
      title: '最后执行',
      dataIndex: 'last_executed_at',
      key: 'last_executed_at',
      width: 150,
      render: (date: string) => date ? dayjs(date).format('YYYY-MM-DD HH:mm') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: any, record: TestCase) => (
        <Space size="small">
          <Tooltip title="执行通过">
            <Button
              type="text"
              icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
              size="small"
              onClick={() => handleExecuteCase(record.id, 'passed')}
            />
          </Tooltip>
          <Tooltip title="执行失败">
            <Button
              type="text"
              icon={<CloseCircleOutlined style={{ color: '#ff4d4f' }} />}
              size="small"
              onClick={() => handleExecuteCase(record.id, 'failed')}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button type="text" icon={<EditOutlined />} size="small" onClick={() => handleEditCase(record)} />
          </Tooltip>
          <Tooltip title="复制">
            <Button type="text" icon={<CopyOutlined />} size="small" />
          </Tooltip>
          <Popconfirm
            title="确认删除"
            onConfirm={() => handleDeleteCase(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Button type="text" danger icon={<DeleteOutlined />} size="small" />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const suiteColumns = [
    {
      title: '套件名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: TestSuite) => (
        <div>
          <FolderOutlined className="mr-2 text-blue-500" />
          <span className="font-medium">{text}</span>
          <div className="text-xs text-gray-400 mt-1">{record.description}</div>
        </div>
      ),
    },
    {
      title: '用例数',
      dataIndex: 'case_count',
      key: 'case_count',
      width: 100,
      render: (count: number) => (
        <Badge count={count || 0} style={{ backgroundColor: '#1890ff' }} />
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
      width: 150,
      render: (_: any, record: TestSuite) => (
        <Space size="small">
          <Tooltip title="编辑">
            <Button type="text" icon={<EditOutlined />} size="small" onClick={() => handleEditSuite(record)} />
          </Tooltip>
          <Popconfirm
            title="确认删除"
            onConfirm={() => handleDeleteSuite(record.id)}
            okText="确认"
            cancelText="取消"
          >
            <Button type="text" danger icon={<DeleteOutlined />} size="small" />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const planColumns = [
    {
      title: '计划名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: TestPlan) => (
        <div>
          <FileTextOutlined className="mr-2 text-green-500" />
          <span className="font-medium">{text}</span>
        </div>
      ),
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
      render: (_: any, record: TestPlan) => (
        <div>
          <div className="text-xs">
            {record.passed_cases || 0}/{record.total_cases || 0}
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2 mt-1">
            <div
              className="bg-green-500 h-2 rounded-full"
              style={{
                width: `${record.total_cases ? ((record.passed_cases || 0) / record.total_cases) * 100 : 0}%`,
              }}
            />
          </div>
        </div>
      ),
    },
    {
      title: '负责人',
      dataIndex: 'manager',
      key: 'manager',
      width: 120,
      render: (manager: any) => manager?.username || '-',
    },
    {
      title: '计划时间',
      key: 'time',
      width: 200,
      render: (_: any, record: TestPlan) => (
        <div className="text-xs">
          {record.planned_start_date && (
            <div>开始: {dayjs(record.planned_start_date).format('YYYY-MM-DD')}</div>
          )}
          {record.planned_end_date && (
            <div>结束: {dayjs(record.planned_end_date).format('YYYY-MM-DD')}</div>
          )}
        </div>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: any, record: TestPlan) => (
        <Space size="small">
          {record.status === 'pending' && (
            <Tooltip title="开始执行">
              <Button
                type="text"
                icon={<PlayCircleOutlined style={{ color: '#52c41a' }} />}
                size="small"
                onClick={() => handleStartPlan(record.id)}
              />
            </Tooltip>
          )}
          {record.status === 'running' && (
            <Tooltip title="完成">
              <Button
                type="text"
                icon={<CheckCircleOutlined style={{ color: '#1890ff' }} />}
                size="small"
                onClick={() => handleCompletePlan(record.id)}
              />
            </Tooltip>
          )}
          <Tooltip title="编辑">
            <Button type="text" icon={<EditOutlined />} size="small" />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6">
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab="测试用例" key="cases">
          <Card
            title={
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold m-0">测试用例</h2>
                  <p className="text-gray-400 text-sm m-0 mt-1">
                    共 {statistics?.total || 0} 个用例
                    {statistics && (
                      <span className="ml-4">
                        <Tag color="success">通过: {statistics.passed || 0}</Tag>
                        <Tag color="error">失败: {statistics.failed || 0}</Tag>
                        <Tag color="warning">阻塞: {statistics.blocked || 0}</Tag>
                      </span>
                    )}
                  </p>
                </div>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateCase}>
                  新建用例
                </Button>
              </div>
            }
          >
            <div className="flex gap-4 mb-4">
              <Search
                placeholder="搜索用例名称、编号"
                allowClear
                onSearch={handleSearch}
                style={{ width: 300 }}
              />
              <Select
                placeholder="状态筛选"
                allowClear
                style={{ width: 150 }}
                onChange={(value) => setStatusFilter(value)}
              >
                <Option value="draft">草稿</Option>
                <Option value="active">有效</Option>
                <Option value="passed">通过</Option>
                <Option value="failed">失败</Option>
                <Option value="blocked">阻塞</Option>
              </Select>
            </div>

            <Table
              columns={caseColumns}
              dataSource={testCases}
              rowKey="id"
              loading={loading}
              pagination={pagination}
              onChange={handleTableChange}
            />
          </Card>
        </TabPane>

        <TabPane tab="测试套件" key="suites">
          <Card
            title={
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold m-0">测试套件</h2>
                  <p className="text-gray-400 text-sm m-0 mt-1">管理测试用例集合</p>
                </div>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateSuite}>
                  新建套件
                </Button>
              </div>
            }
          >
            <Table
              columns={suiteColumns}
              dataSource={testSuites}
              rowKey="id"
              loading={loading}
            />
          </Card>
        </TabPane>

        <TabPane tab="测试计划" key="plans">
          <Card
            title={
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold m-0">测试计划</h2>
                  <p className="text-gray-400 text-sm m-0 mt-1">管理测试执行计划</p>
                </div>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreatePlan}>
                  新建计划
                </Button>
              </div>
            }
          >
            <Table
              columns={planColumns}
              dataSource={testPlans}
              rowKey="id"
              loading={loading}
            />
          </Card>
        </TabPane>
      </Tabs>

      {/* 用例表单Modal */}
      <Modal
        title={editingCase ? '编辑测试用例' : '新建测试用例'}
        open={isCaseModalOpen}
        onCancel={() => setIsCaseModalOpen(false)}
        onOk={() => caseForm.submit()}
        width={800}
      >
        <Form form={caseForm} layout="vertical" onFinish={handleSubmitCase}>
          <Form.Item name="name" label="用例名称" rules={[{ required: true }]}>
            <Input placeholder="请输入用例名称" />
          </Form.Item>

          <div className="flex gap-4">
            <Form.Item name="case_type" label="用例类型" className="flex-1" initialValue="functional">
              <Select>
                <Option value="functional">功能测试</Option>
                <Option value="performance">性能测试</Option>
                <Option value="security">安全测试</Option>
                <Option value="compatibility">兼容测试</Option>
                <Option value="usability">易用性测试</Option>
              </Select>
            </Form.Item>
            <Form.Item name="priority" label="优先级" className="flex-1" initialValue="medium">
              <Select>
                <Option value="high">高</Option>
                <Option value="medium">中</Option>
                <Option value="low">低</Option>
              </Select>
            </Form.Item>
          </div>

          <Form.Item name="module" label="所属模块">
            <Input placeholder="请输入所属模块" />
          </Form.Item>

          <Form.Item name="pre_condition" label="前置条件">
            <TextArea rows={2} placeholder="请输入前置条件" />
          </Form.Item>

          <Form.Item name="steps" label="测试步骤" rules={[{ required: true }]}>
            <TextArea rows={4} placeholder="请输入测试步骤" />
          </Form.Item>

          <Form.Item name="expected_result" label="预期结果" rules={[{ required: true }]}>
            <TextArea rows={2} placeholder="请输入预期结果" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 套件表单Modal */}
      <Modal
        title={editingSuite ? '编辑测试套件' : '新建测试套件'}
        open={isSuiteModalOpen}
        onCancel={() => setIsSuiteModalOpen(false)}
        onOk={() => suiteForm.submit()}
      >
        <Form form={suiteForm} layout="vertical" onFinish={handleSubmitSuite}>
          <Form.Item name="name" label="套件名称" rules={[{ required: true }]}>
            <Input placeholder="请输入套件名称" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="请输入套件描述" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
