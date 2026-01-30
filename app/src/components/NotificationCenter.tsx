import { useEffect, useState } from 'react';
import { Badge, Dropdown, List, Button, Empty, Tabs, Avatar, Tag, message } from 'antd';
import { BellOutlined, CheckCircleOutlined, MessageOutlined, BugOutlined, FileTextOutlined, ThunderboltOutlined, DeleteOutlined } from '@ant-design/icons';
import { notificationApi } from '@/services/api';
import type { Notification } from '@/types';
import dayjs from 'dayjs';

const { TabPane } = Tabs;

interface NotificationCenterProps {
  onCountChange?: (count: number) => void;
}

export default function NotificationCenter({ onCountChange }: NotificationCenterProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await notificationApi.getNotifications({
        unread_only: activeTab === 'unread',
      });
      if (response.code === 200) {
        setNotifications(response.data.results || []);
      }
    } catch (error) {
      console.error('获取通知失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchUnreadCount = async () => {
    try {
      const response = await notificationApi.getUnreadCount();
      if (response.code === 200) {
        setUnreadCount(response.data.count || 0);
        onCountChange?.(response.data.count || 0);
      }
    } catch (error) {
      console.error('获取未读数失败');
    }
  };

  useEffect(() => {
    fetchNotifications();
    fetchUnreadCount();

    // 定时刷新
    const interval = setInterval(() => {
      fetchUnreadCount();
    }, 30000);

    return () => clearInterval(interval);
  }, [activeTab]);

  const handleMarkAsRead = async (id: number) => {
    try {
      await notificationApi.markAsRead(id);
      fetchNotifications();
      fetchUnreadCount();
    } catch (error) {
      message.error('标记已读失败');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationApi.markAllAsRead();
      message.success('全部标记为已读');
      fetchNotifications();
      fetchUnreadCount();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await notificationApi.deleteNotification(id);
      fetchNotifications();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const getIconByType = (type: string) => {
    const icons: Record<string, React.ReactNode> = {
      bug: <BugOutlined style={{ color: '#ff4d4f' }} />,
      testcase: <FileTextOutlined style={{ color: '#1890ff' }} />,
      report: <FileTextOutlined style={{ color: '#52c41a' }} />,
      system: <MessageOutlined style={{ color: '#faad14' }} />,
      perftest: <ThunderboltOutlined style={{ color: '#722ed1' }} />,
    };
    return icons[type] || <MessageOutlined style={{ color: '#8c8c8c' }} />;
  };

  const getNotificationContent = (notification: Notification) => {
    return (
      <div className="notification-item">
        <div className="font-medium">{notification.title}</div>
        <div className="text-sm text-gray-400 mt-1">{notification.content}</div>
        <div className="flex items-center justify-between mt-2">
          <span className="text-xs text-gray-500">
            {dayjs(notification.created_at).format('MM-DD HH:mm')}
          </span>
          {!notification.is_read && (
            <Tag color="red" size="small">未读</Tag>
          )}
        </div>
      </div>
    );
  };

  const notificationList = (
    <div className="notification-dropdown" style={{ width: 400, maxHeight: 500, overflow: 'auto' }}>
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <h3 className="text-lg font-bold m-0">通知中心</h3>
        {unreadCount > 0 && (
          <Button type="link" size="small" onClick={handleMarkAllAsRead}>
            全部已读
          </Button>
        )}
      </div>

      <Tabs activeKey={activeTab} onChange={setActiveTab} className="px-4">
        <TabPane tab="全部" key="all" />
        <TabPane tab={`未读 (${unreadCount})`} key="unread" />
      </Tabs>

      <List
        dataSource={notifications}
        loading={loading}
        locale={{
          emptyText: (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="暂无通知"
            />
          ),
        }}
        renderItem={(item) => (
          <List.Item
            className={`px-4 hover:bg-gray-800 cursor-pointer ${!item.is_read ? 'bg-gray-800/50' : ''}`}
            actions={[
              !item.is_read && (
                <Button
                  type="text"
                  icon={<CheckCircleOutlined />}
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleMarkAsRead(item.id);
                  }}
                />
              ),
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(item.id);
                }}
              />,
            ]}
          >
            <List.Item.Meta
              avatar={<Avatar icon={getIconByType(item.type)} />}
              title={getNotificationContent(item)}
            />
          </List.Item>
        )}
      />

      <div className="p-4 border-t border-gray-700 text-center">
        <Button type="link">查看全部通知</Button>
      </div>
    </div>
  );

  return (
    <Dropdown
      dropdownRender={() => notificationList}
      placement="bottomRight"
      trigger={['click']}
      arrow
    >
      <div className="notification-bell cursor-pointer relative">
        <Badge count={unreadCount} overflowCount={99}>
          <BellOutlined className="text-xl" />
        </Badge>
      </div>
    </Dropdown>
  );
}
