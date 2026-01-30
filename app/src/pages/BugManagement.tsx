import { useEffect, useState } from 'react';
import { Button, Card, Input, Modal, Form, Select, Tag, Space, Tooltip, message, Popconfirm, Table, Tabs, Badge, Timeline, Avatar, List } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, CheckCircleOutlined, UserOutlined, HistoryOutlined, MessageOutlined, ExclamationCircleOutlined, ClockCircleOutlined, SyncOutlined } from '@ant-design/icons';
import { bugApi } from '@/services/api';
import type { Bug } from '@/types';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

interface BugFormData {
  title: string;
  description?: string;
  bug_type?: string;
  severity?: string;
  priority?: string;
  module?: string;
  project?: number;
  version?: number;
}

export default function BugManagement() {
  const [activeTab, setActiveTab] = useState('all');
  const [bugs, setBugs] = useState<Bug[]>([]);
  const [myBugs, setMyBugs] = useState<Bug[]>([]);
  const [reportedByMe, setReportedByMe] = useState<Bug[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [isResolveModalOpen, setIsResolveModalOpen] = useState(false);
  const [isCommentModalOpen, setIsCommentModalOpen] = useState(false);
  const [editingBug, setEditingBug] = useState<Bug | null>(null);
  const [selectedBug, setSelectedBug] = useState<Bug | null>(null);
  const [bugComments, setBugComments] = useState<any[]>([]);
  const [bugHistory, setBugHistory] = useState<any[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [form] = Form.useForm();
  const [assignForm] = Form.useForm();
  const [resolveForm] = Form.useForm();
  const [commentForm] = Form.useForm();

  const fetchBugs = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      const response = await bugApi.getBugs({
        page,
        page_size: pageSize,
        search: searchText || undefined,
        status: statusFilter || undefined,
      });
      if (response.code === 200) {
        setBugs(response.data.results || []);
        setPagination({
          current: page,
          pageSize,
          total: response.data.count || 0,
        });
      }
    } catch (error) {
      message.error('获取Bug列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchMyBugs = async () => {
    try {
      const response = await bugApi.getMyBugs();
      if (response.code === 200) {
        setMyBugs(response.data || []);
      }
    } catch (error) {
      console.error('获取我的Bug失败');
    }
  };

  const fetchReportedByMe = async () => {
    try {
      const response = await bugApi.getReportedByMe();
      if (response.code === 200) {
        setReportedByMe(response.data || []);
      }
    } catch (error) {
      console.error('获取我报告的Bug失败');
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await bugApi.getStatistics();
      if (response.code === 200) {
        setStatistics(response.data);
      }
    } catch (error) {
      console.error('获取统计信息失败');
    }
  };

  const fetchBugComments = async (bugId: number) => {
    try {
      const response = await bugApi.getBugComments(bugId);
      if (response.code === 200) {
        setBugComments(response.data || []);
      }
    } catch (error) {
      console.error('获取评论失败');
    }
  };

  const fetchBugHistory = async (bugId: number) => {
    try {
      const response = await bugApi.getBugHistory(bugId);
      if (response.code === 200) {
        setBugHistory(response.data || []);
      }
    } catch (error) {
      console.error('获取历史记录失败');
    }
  };

  useEffect(() => {
    fetchBugs();
    fetchStatistics();
    fetchMyBugs();
    fetchReportedByMe();
  }, [searchText, statusFilter]);

  const handleSearch = (value: string) => {
    setSearchText(value);
    fetchBugs(1);
  };

  const handleTableChange = (newPagination: any) => {
    fetchBugs(newPagination.current, newPagination.pageSize);
  };

  const handleCreate = () => {
    setEditingBug(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEdit = (bug: Bug) => {
    setEditingBug(bug);
    form.setFieldsValue(bug);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await bugApi.deleteBug(id);
      message.success('删除成功');
      fetchBugs(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async (values: BugFormData) => {
    try {
      if (editingBug) {
        await bugApi.updateBug(editingBug.id, values);
        message.success('更新成功');
      } else {
        await bugApi.createBug(values);
        message.success('创建成功');
      }
      setIsModalOpen(false);
      fetchBugs(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error(editingBug ? '更新失败' : '创建失败');
    }
  };

  const handleViewDetail = (bug: Bug) => {
    setSelectedBug(bug);
    fetchBugComments(bug.id);
    fetchBugHistory(bug.id);
    setIsDetailModalOpen(true);
  };

  const handleAssign = (bug: Bug) => {
    setSelectedBug(bug);
    assignForm.resetFields();
    setIsAssignModalOpen(true);
  };

  const handleSubmitAssign = async (values: { assignee_id: number }) => {
    if (!selectedBug) return;
    try {
      await bugApi.assignBug(selectedBug.id, values);
      message.success('分配成功');
      setIsAssignModalOpen(false);
      fetchBugs(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error('分配失败');
    }
  };

  const handleResolve = (bug: Bug) => {
    setSelectedBug(bug);
    resolveForm.resetFields();
    setIsResolveModalOpen(true);
  };

  const handleSubmitResolve = async (values: { resolution: string }) => {
    if (!selectedBug) return;
    try {
      await bugApi.resolveBug(selectedBug.id, values);
      message.success('解决成功');
      setIsResolveModalOpen(false);
      fetchBugs(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error('解决失败');
    }
  };

  const handleClose = async (id: number) => {
    try {
      await bugApi.closeBug(id);
      message.success('关闭成功');
      fetchBugs(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error('关闭失败');
    }
  };

  const handleReopen = async (id: number) => {
    try {
      await bugApi.reopenBug(id, { reason: '重新打开' });
      message.success('重新打开成功');
      fetchBugs(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error('重新打开失败');
    }
  };

  const handleAddComment = (bug: Bug) => {
    setSelectedBug(bug);
    commentForm.resetFields();
    setIsCommentModalOpen(true);
  };

  const handleSubmitComment = async (values: { content: string }) => {
    if (!selectedBug) return;
    try {
      await bugApi.addBugComment(selectedBug.id, values);
      message.success('评论添加成功');
      setIsCommentModalOpen(false);
      fetchBugComments(selectedBug.id);
    } catch (error) {
      message.error('添加评论失败');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      new: 'blue',
      confirmed: 'processing',
      in_progress: 'warning',
      resolved: 'success',
      closed: 'default',
      reopened: 'error',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      new: '新建',
      confirmed: '已确认',
      in_progress: '处理中',
      resolved: '已解决',
      closed: '已关闭',
      reopened: '重新打开',
    };
    return texts[status] || status;
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'red',
      high: 'orange',
      medium: 'yellow',
      low: 'green',
    };
    return colors[severity] || 'default';
  };

  const getSeverityText = (severity: string) => {
    const texts: Record<string, string> = {
      critical: '致命',
      high: '严重',
      medium: '一般',
      low: '轻微',
    };
    return texts[severity] || severity;
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      urgent: 'red',
      high: 'orange',
      medium: 'blue',
      low: 'green',
    };
    return colors[priority] || 'default';
  };

  const columns = [
    {
      title: 'Bug编号',
      dataIndex: 'bug_no',
      key: 'bug_no',
      width: 130,
      render: (text: string) => <span className="font-mono text-blue-400">{text}</span>,
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: Bug) => (
        <div>
          <div className="font-medium cursor-pointer hover:text-blue-400" onClick={() => handleViewDetail(record)}>
            {text}
          </div>
          <div className="text-xs text-gray-400">{record.module}</div>
        </div>
      ),
    },
    {
      title: '严重程度',
      dataIndex: 'severity',
      key: 'severity',
      width: 90,
      render: (severity: string) => (
        <Tag color={getSeverityColor(severity)}>{getSeverityText(severity)}</Tag>
      ),
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority: string) => (
        <Tag color={getPriorityColor(priority)}>
          {priority === 'urgent' ? '紧急' : priority === 'high' ? '高' : priority === 'medium' ? '中' : '低'}
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
      title: '负责人',
      dataIndex: 'assignee',
      key: 'assignee',
      width: 100,
      render: (assignee: any) => assignee?.username || <span className="text-gray-500">未分配</span>,
    },
    {
      title: '报告人',
      dataIndex: 'reporter',
      key: 'reporter',
      width: 100,
      render: (reporter: any) => reporter?.username || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (date: string) => dayjs(date).format('MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'action',
      width: 250,
      render: (_: any, record: Bug) => (
        <Space size="small">
          {['new', 'confirmed', 'reopened'].includes(record.status) && (
            <Tooltip title="分配">
              <Button type="text" icon={<UserOutlined />} size="small" onClick={() => handleAssign(record)} />
            </Tooltip>
          )}
          {record.status === 'in_progress' && (
            <Tooltip title="解决">
              <Button type="text" icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />} size="small" onClick={() => handleResolve(record)} />
            </Tooltip>
          )}
          {record.status === 'resolved' && (
            <Tooltip title="关闭">
              <Button type="text" icon={<CheckCircleOutlined style={{ color: '#1890ff' }} />} size="small" onClick={() => handleClose(record.id)} />
            </Tooltip>
          )}
          {record.status === 'closed' && (
            <Tooltip title="重新打开">
              <Button type="text" icon={<SyncOutlined style={{ color: '#faad14' }} />} size="small" onClick={() => handleReopen(record.id)} />
            </Tooltip>
          )}
          <Tooltip title="评论">
            <Button type="text" icon={<MessageOutlined />} size="small" onClick={() => handleAddComment(record)} />
          </Tooltip>
          <Tooltip title="编辑">
            <Button type="text" icon={<EditOutlined />} size="small" onClick={() => handleEdit(record)} />
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

  const renderBugTable = (data: Bug[]) => (
    <Table
      columns={columns}
      dataSource={data}
      rowKey="id"
      loading={loading}
      pagination={pagination}
      onChange={handleTableChange}
      size="small"
    />
  );

  return (
    <div className="p-6">
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane
          tab={`全部 Bug ${statistics?.total ? `(${statistics.total})` : ''}`}
          key="all"
        >
          <Card
            title={
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold m-0">Bug 管理</h2>
                  {statistics && (
                    <p className="text-gray-400 text-sm m-0 mt-1">
                      <Tag color="blue">新建: {statistics.by_status?.find((s: any) => s.status === 'new')?.count || 0}</Tag>
                      <Tag color="processing">处理中: {statistics.by_status?.find((s: any) => s.status === 'in_progress')?.count || 0}</Tag>
                      <Tag color="success">已解决: {statistics.by_status?.find((s: any) => s.status === 'resolved')?.count || 0}</Tag>
                      <Tag color="default">已关闭: {statistics.by_status?.find((s: any) => s.status === 'closed')?.count || 0}</Tag>
                    </p>
                  )}
                </div>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                  提交 Bug
                </Button>
              </div>
            }
          >
            <div className="flex gap-4 mb-4">
              <Search
                placeholder="搜索Bug标题、编号"
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
                <Option value="new">新建</Option>
                <Option value="confirmed">已确认</Option>
                <Option value="in_progress">处理中</Option>
                <Option value="resolved">已解决</Option>
                <Option value="closed">已关闭</Option>
                <Option value="reopened">重新打开</Option>
              </Select>
            </div>

            {renderBugTable(bugs)}
          </Card>
        </TabPane>

        <TabPane tab={`分配给我 (${myBugs.length})`} key="my">
          <Card title="分配给我的 Bug">{renderBugTable(myBugs)}</Card>
        </TabPane>

        <TabPane tab={`我报告的 (${reportedByMe.length})`} key="reported">
          <Card title="我报告的 Bug">{renderBugTable(reportedByMe)}</Card>
        </TabPane>
      </Tabs>

      {/* 创建/编辑Bug Modal */}
      <Modal
        title={editingBug ? '编辑 Bug' : '提交 Bug'}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        width={700}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item name="title" label="Bug标题" rules={[{ required: true, message: '请输入Bug标题' }]}>
            <Input placeholder="请输入Bug标题" />
          </Form.Item>

          <div className="flex gap-4">
            <Form.Item name="bug_type" label="Bug类型" className="flex-1" initialValue="functional">
              <Select>
                <Option value="functional">功能问题</Option>
                <Option value="ui">界面问题</Option>
                <Option value="performance">性能问题</Option>
                <Option value="compatibility">兼容问题</Option>
                <Option value="security">安全问题</Option>
                <Option value="other">其他</Option>
              </Select>
            </Form.Item>

            <Form.Item name="severity" label="严重程度" className="flex-1" initialValue="medium">
              <Select>
                <Option value="critical">致命</Option>
                <Option value="high">严重</Option>
                <Option value="medium">一般</Option>
                <Option value="low">轻微</Option>
              </Select>
            </Form.Item>

            <Form.Item name="priority" label="优先级" className="flex-1" initialValue="medium">
              <Select>
                <Option value="urgent">紧急</Option>
                <Option value="high">高</Option>
                <Option value="medium">中</Option>
                <Option value="low">低</Option>
              </Select>
            </Form.Item>
          </div>

          <Form.Item name="module" label="所属模块">
            <Input placeholder="请输入所属模块" />
          </Form.Item>

          <Form.Item name="description" label="详细描述">
            <TextArea rows={4} placeholder="请详细描述Bug的重现步骤、实际结果和期望结果" />
          </Form.Item>
        </Form>
      </Modal>

      {/* Bug详情 Modal */}
      <Modal
        title={selectedBug?.bug_no}
        open={isDetailModalOpen}
        onCancel={() => setIsDetailModalOpen(false)}
        footer={null}
        width={900}
      >
        {selectedBug && (
          <div>
            <h3 className="text-lg font-bold mb-4">{selectedBug.title}</h3>
            <div className="flex gap-2 mb-4">
              <Tag color={getSeverityColor(selectedBug.severity)}>{getSeverityText(selectedBug.severity)}</Tag>
              <Tag color={getStatusColor(selectedBug.status)}>{getStatusText(selectedBug.status)}</Tag>
              <Tag color={getPriorityColor(selectedBug.priority)}>
                {selectedBug.priority === 'urgent' ? '紧急' : selectedBug.priority === 'high' ? '高' : selectedBug.priority === 'medium' ? '中' : '低'}
              </Tag>
            </div>

            <Tabs defaultActiveKey="comments">
              <TabPane tab="评论" key="comments">
                <List
                  dataSource={bugComments}
                  renderItem={(item) => (
                    <List.Item>
                      <List.Item.Meta
                        avatar={<Avatar icon={<UserOutlined />} />}
                        title={<span>{item.created_by?.username} <span className="text-gray-400 text-xs">{dayjs(item.created_at).format('YYYY-MM-DD HH:mm')}</span></span>}
                        description={item.content}
                      />
                    </List.Item>
                  )}
                />
              </TabPane>
              <TabPane tab="历史记录" key="history">
                <Timeline>
                  {bugHistory.map((item, index) => (
                    <Timeline.Item key={index}>
                      <p>{item.action}</p>
                      <p className="text-gray-400 text-xs">{dayjs(item.created_at).format('YYYY-MM-DD HH:mm')}</p>
                    </Timeline.Item>
                  ))}
                </Timeline>
              </TabPane>
            </Tabs>
          </div>
        )}
      </Modal>

      {/* 分配 Modal */}
      <Modal
        title="分配 Bug"
        open={isAssignModalOpen}
        onCancel={() => setIsAssignModalOpen(false)}
        onOk={() => assignForm.submit()}
      >
        <Form form={assignForm} layout="vertical" onFinish={handleSubmitAssign}>
          <Form.Item name="assignee_id" label="分配给" rules={[{ required: true, message: '请选择负责人' }]}>
            <Select placeholder="请选择负责人">
              <Option value={1}>管理员</Option>
              <Option value={2}>测试人员</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 解决 Modal */}
      <Modal
        title="解决 Bug"
        open={isResolveModalOpen}
        onCancel={() => setIsResolveModalOpen(false)}
        onOk={() => resolveForm.submit()}
      >
        <Form form={resolveForm} layout="vertical" onFinish={handleSubmitResolve}>
          <Form.Item name="resolution" label="解决方案" rules={[{ required: true, message: '请选择解决方案' }]}>
            <Select placeholder="请选择解决方案">
              <Option value="fixed">已修复</Option>
              <Option value="wont_fix">不修复</Option>
              <Option value="duplicate">重复问题</Option>
              <Option value="not_a_bug">不是Bug</Option>
              <Option value="cannot_reproduce">无法重现</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 评论 Modal */}
      <Modal
        title="添加评论"
        open={isCommentModalOpen}
        onCancel={() => setIsCommentModalOpen(false)}
        onOk={() => commentForm.submit()}
      >
        <Form form={commentForm} layout="vertical" onFinish={handleSubmitComment}>
          <Form.Item name="content" label="评论内容" rules={[{ required: true, message: '请输入评论内容' }]}>
            <TextArea rows={4} placeholder="请输入评论内容" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
