import { useEffect, useState } from 'react';
import { Button, Card, Input, Modal, Form, Select, Tag, Space, Tooltip, message, Popconfirm, Table, Badge } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, TeamOutlined, SettingOutlined, EyeOutlined, BranchesOutlined, FlagOutlined, EnvironmentOutlined } from '@ant-design/icons';
import { projectApi } from '@/services/api';
import type { Project } from '@/types';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;
const { TextArea } = Input;

interface ProjectFormData {
  name: string;
  code: string;
  description?: string;
  project_type?: string;
  status?: string;
  priority?: string;
  start_date?: string;
  end_date?: string;
}

export default function ProjectManagement() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [form] = Form.useForm();

  const fetchProjects = async (page = 1, pageSize = 10) => {
    setLoading(true);
    try {
      const response = await projectApi.getProjects({
        page,
        page_size: pageSize,
        search: searchText || undefined,
        status: statusFilter || undefined,
      });
      if (response.code === 200) {
        setProjects(response.data.results || []);
        setPagination({
          current: page,
          pageSize,
          total: response.data.count || 0,
        });
      }
    } catch (error) {
      message.error('获取项目列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [searchText, statusFilter]);

  const handleSearch = (value: string) => {
    setSearchText(value);
    fetchProjects(1);
  };

  const handleTableChange = (newPagination: any) => {
    fetchProjects(newPagination.current, newPagination.pageSize);
  };

  const handleCreate = () => {
    setEditingProject(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEdit = (project: Project) => {
    setEditingProject(project);
    form.setFieldsValue({
      ...project,
      start_date: project.start_date ? dayjs(project.start_date).format('YYYY-MM-DD') : undefined,
      end_date: project.end_date ? dayjs(project.end_date).format('YYYY-MM-DD') : undefined,
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await projectApi.deleteProject(id);
      message.success('删除成功');
      fetchProjects(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleSubmit = async (values: ProjectFormData) => {
    try {
      if (editingProject) {
        await projectApi.updateProject(editingProject.id, values);
        message.success('更新成功');
      } else {
        await projectApi.createProject(values);
        message.success('创建成功');
      }
      setIsModalOpen(false);
      fetchProjects(pagination.current, pagination.pageSize);
    } catch (error) {
      message.error(editingProject ? '更新失败' : '创建失败');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'success',
      inactive: 'default',
      pending: 'warning',
      completed: 'blue',
      archived: 'gray',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      active: '进行中',
      inactive: '暂停',
      pending: '待开始',
      completed: '已完成',
      archived: '已归档',
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

  const getPriorityText = (priority: string) => {
    const texts: Record<string, string> = {
      high: '高',
      medium: '中',
      low: '低',
    };
    return texts[priority] || priority;
  };

  const columns = [
    {
      title: '项目名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Project) => (
        <div>
          <div className="font-medium">{text}</div>
          <div className="text-xs text-gray-400">{record.code}</div>
        </div>
      ),
    },
    {
      title: '项目类型',
      dataIndex: 'project_type',
      key: 'project_type',
      render: (type: string) => {
        const typeMap: Record<string, string> = {
          web: 'Web应用',
          app: '移动应用',
          api: '接口服务',
          desktop: '桌面应用',
          other: '其他',
        };
        return typeMap[type] || type;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Badge status={getStatusColor(status) as any} text={getStatusText(status)} />
      ),
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority: string) => (
        <Tag color={getPriorityColor(priority)}>{getPriorityText(priority)}</Tag>
      ),
    },
    {
      title: '负责人',
      dataIndex: 'owner',
      key: 'owner',
      render: (owner: any) => owner?.username || '-',
    },
    {
      title: '成员数',
      dataIndex: 'member_count',
      key: 'member_count',
      render: (count: number) => (
        <Space>
          <TeamOutlined />
          <span>{count || 0}</span>
        </Space>
      ),
    },
    {
      title: '时间',
      key: 'time',
      render: (_: any, record: Project) => (
        <div className="text-xs">
          {record.start_date && (
            <div>开始: {dayjs(record.start_date).format('YYYY-MM-DD')}</div>
          )}
          {record.end_date && (
            <div>结束: {dayjs(record.end_date).format('YYYY-MM-DD')}</div>
          )}
        </div>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: any, record: Project) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button type="text" icon={<EyeOutlined />} size="small" />
          </Tooltip>
          <Tooltip title="版本管理">
            <Button type="text" icon={<BranchesOutlined />} size="small" />
          </Tooltip>
          <Tooltip title="里程碑">
            <Button type="text" icon={<FlagOutlined />} size="small" />
          </Tooltip>
          <Tooltip title="环境配置">
            <Button type="text" icon={<EnvironmentOutlined />} size="small" />
          </Tooltip>
          <Tooltip title="编辑">
            <Button type="text" icon={<EditOutlined />} size="small" onClick={() => handleEdit(record)} />
          </Tooltip>
          <Tooltip title="成员管理">
            <Button type="text" icon={<TeamOutlined />} size="small" />
          </Tooltip>
          <Popconfirm
            title="确认删除"
            description="删除后无法恢复，是否继续？"
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
      <Card
        title={
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold m-0">项目管理</h2>
              <p className="text-gray-400 text-sm m-0 mt-1">管理测试项目、版本、里程碑和环境配置</p>
            </div>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              新建项目
            </Button>
          </div>
        }
      >
        <div className="flex gap-4 mb-4">
          <Search
            placeholder="搜索项目名称、代码"
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
            <Option value="active">进行中</Option>
            <Option value="pending">待开始</Option>
            <Option value="completed">已完成</Option>
            <Option value="archived">已归档</Option>
          </Select>
        </div>

        <Table
          columns={columns}
          dataSource={projects}
          rowKey="id"
          loading={loading}
          pagination={pagination}
          onChange={handleTableChange}
        />
      </Card>

      <Modal
        title={editingProject ? '编辑项目' : '新建项目'}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        width={700}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="项目名称"
            rules={[{ required: true, message: '请输入项目名称' }]}
          >
            <Input placeholder="请输入项目名称" />
          </Form.Item>

          <Form.Item
            name="code"
            label="项目代码"
            rules={[{ required: true, message: '请输入项目代码' }]}
          >
            <Input placeholder="请输入项目代码，如：PROJ001" />
          </Form.Item>

          <Form.Item
            name="project_type"
            label="项目类型"
            rules={[{ required: true, message: '请选择项目类型' }]}
          >
            <Select placeholder="请选择项目类型">
              <Option value="web">Web应用</Option>
              <Option value="app">移动应用</Option>
              <Option value="api">接口服务</Option>
              <Option value="desktop">桌面应用</Option>
              <Option value="other">其他</Option>
            </Select>
          </Form.Item>

          <div className="flex gap-4">
            <Form.Item
              name="status"
              label="状态"
              className="flex-1"
              initialValue="pending"
            >
              <Select placeholder="请选择状态">
                <Option value="active">进行中</Option>
                <Option value="pending">待开始</Option>
                <Option value="completed">已完成</Option>
                <Option value="archived">已归档</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="priority"
              label="优先级"
              className="flex-1"
              initialValue="medium"
            >
              <Select placeholder="请选择优先级">
                <Option value="high">高</Option>
                <Option value="medium">中</Option>
                <Option value="low">低</Option>
              </Select>
            </Form.Item>
          </div>

          <div className="flex gap-4">
            <Form.Item
              name="start_date"
              label="开始日期"
              className="flex-1"
            >
              <Input type="date" />
            </Form.Item>

            <Form.Item
              name="end_date"
              label="结束日期"
              className="flex-1"
            >
              <Input type="date" />
            </Form.Item>
          </div>

          <Form.Item
            name="description"
            label="项目描述"
          >
            <TextArea rows={4} placeholder="请输入项目描述" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
