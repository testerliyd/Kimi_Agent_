import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { dashboardApi } from '@/services/api';
import {
  FolderKanban,
  FileText,
  Bug,
  AlertCircle,
  Activity,
  TrendingUp,
  TrendingDown,
  Clock,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface Stats {
  total_projects: number;
  total_test_cases: number;
  total_bugs: number;
  pending_bugs: number;
}

interface RecentBug {
  id: number;
  title: string;
  severity: string;
  status: string;
  created_at: string;
}

interface RecentActivity {
  id: number;
  user: string;
  action: string;
  target: string;
  created_at: string;
}

const severityColors: Record<string, string> = {
  blocker: 'bg-red-500/20 text-red-400 border-red-500/30',
  critical: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  major: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  minor: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
};

const statusColors: Record<string, string> = {
  new: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  confirmed: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  in_progress: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  fixed: 'bg-green-500/20 text-green-400 border-green-500/30',
  rejected: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  closed: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
};

const severityLabels: Record<string, string> = {
  blocker: '阻断',
  critical: '严重',
  major: '主要',
  minor: '次要',
};

const statusLabels: Record<string, string> = {
  new: '新建',
  confirmed: '已确认',
  in_progress: '处理中',
  fixed: '已修复',
  rejected: '已拒绝',
  closed: '已关闭',
};

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    total_projects: 0,
    total_test_cases: 0,
    total_bugs: 0,
    pending_bugs: 0,
  });
  const [recentBugs, setRecentBugs] = useState<RecentBug[]>([]);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, bugsRes, activitiesRes] = await Promise.all([
          dashboardApi.getStats(),
          dashboardApi.getRecentBugs(),
          dashboardApi.getRecentActivities(),
        ]);

        if (statsRes.code === 200) {
          setStats(statsRes.data);
        }
        if (bugsRes.code === 200) {
          setRecentBugs(bugsRes.data);
        }
        if (activitiesRes.code === 200) {
          setRecentActivities(activitiesRes.data);
        }
      } catch (error) {
        console.error('获取仪表盘数据失败:', error);
        // 使用模拟数据
        setStats({
          total_projects: 12,
          total_test_cases: 856,
          total_bugs: 234,
          pending_bugs: 45,
        });
        setRecentBugs([
          { id: 1, title: '用户登录功能异常', severity: 'critical', status: 'in_progress', created_at: '2024-01-30T10:00:00Z' },
          { id: 2, title: '页面加载缓慢', severity: 'major', status: 'new', created_at: '2024-01-30T09:30:00Z' },
          { id: 3, title: '按钮样式错误', severity: 'minor', status: 'fixed', created_at: '2024-01-30T09:00:00Z' },
        ]);
        setRecentActivities([
          { id: 1, user: '张三', action: '创建了Bug', target: '用户登录功能异常', created_at: '2024-01-30T10:00:00Z' },
          { id: 2, user: '李四', action: '完成了测试', target: '接口自动化测试', created_at: '2024-01-30T09:45:00Z' },
          { id: 3, user: '王五', action: '更新了用例', target: '登录功能测试用例', created_at: '2024-01-30T09:30:00Z' },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const statCards = [
    {
      title: '项目总数',
      value: stats.total_projects,
      icon: FolderKanban,
      trend: '+12%',
      trendUp: true,
      color: 'from-cyan-500 to-blue-500',
    },
    {
      title: '测试用例',
      value: stats.total_test_cases,
      icon: FileText,
      trend: '+8%',
      trendUp: true,
      color: 'from-blue-500 to-indigo-500',
    },
    {
      title: 'Bug总数',
      value: stats.total_bugs,
      icon: Bug,
      trend: '-5%',
      trendUp: false,
      color: 'from-purple-500 to-pink-500',
    },
    {
      title: '待处理Bug',
      value: stats.pending_bugs,
      icon: AlertCircle,
      trend: '+3%',
      trendUp: false,
      color: 'from-orange-500 to-red-500',
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => (
          <Card
            key={index}
            className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20 hover:border-cyan-500/40 transition-all duration-300 group"
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-slate-400">{card.title}</p>
                  <p className="text-3xl font-bold text-slate-100 mt-2">{card.value}</p>
                  <div className="flex items-center gap-1 mt-2">
                    {card.trendUp ? (
                      <TrendingUp className="w-4 h-4 text-green-400" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-400" />
                    )}
                    <span className={cn(
                      'text-sm',
                      card.trendUp ? 'text-green-400' : 'text-red-400'
                    )}>
                      {card.trend}
                    </span>
                  </div>
                </div>
                <div className={cn(
                  'w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center',
                  card.color,
                  'shadow-lg group-hover:shadow-xl transition-shadow'
                )}>
                  <card.icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 主要内容区 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 最近Bug */}
        <Card className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20">
          <CardHeader className="border-b border-cyan-500/10">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                <Bug className="w-5 h-5 text-cyan-400" />
                最近Bug
              </CardTitle>
              <Badge variant="outline" className="border-cyan-500/30 text-cyan-400">
                查看更多
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-cyan-500/10">
              {recentBugs.map((bug) => (
                <div
                  key={bug.id}
                  className="p-4 hover:bg-cyan-500/5 transition-colors cursor-pointer group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-200 group-hover:text-cyan-400 transition-colors truncate">
                        {bug.title}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge
                          variant="outline"
                          className={cn('text-xs', severityColors[bug.severity])}
                        >
                          {severityLabels[bug.severity]}
                        </Badge>
                        <Badge
                          variant="outline"
                          className={cn('text-xs', statusColors[bug.status])}
                        >
                          {statusLabels[bug.status]}
                        </Badge>
                      </div>
                    </div>
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(bug.created_at).toLocaleDateString('zh-CN')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 最近活动 */}
        <Card className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20">
          <CardHeader className="border-b border-cyan-500/10">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                <Activity className="w-5 h-5 text-cyan-400" />
                最近活动
              </CardTitle>
              <Badge variant="outline" className="border-cyan-500/30 text-cyan-400">
                查看更多
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-cyan-500/10">
              {recentActivities.map((activity) => (
                <div
                  key={activity.id}
                  className="p-4 hover:bg-cyan-500/5 transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center flex-shrink-0">
                      <span className="text-xs font-medium text-white">
                        {activity.user.charAt(0)}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-200">
                        <span className="font-medium text-cyan-400">{activity.user}</span>
                        {' '}{activity.action}{' '}
                        <span className="font-medium">{activity.target}</span>
                      </p>
                      <span className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                        <Clock className="w-3 h-3" />
                        {new Date(activity.created_at).toLocaleString('zh-CN')}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 快捷操作 */}
      <Card className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20">
        <CardHeader className="border-b border-cyan-500/10">
          <CardTitle className="text-lg font-semibold text-slate-100">快捷操作</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: '新建项目', icon: FolderKanban, color: 'from-cyan-500 to-blue-500' },
              { name: '新建用例', icon: FileText, color: 'from-blue-500 to-indigo-500' },
              { name: '提交Bug', icon: Bug, color: 'from-purple-500 to-pink-500' },
              { name: '运行测试', icon: Activity, color: 'from-orange-500 to-red-500' },
            ].map((item, index) => (
              <button
                key={index}
                className="flex flex-col items-center gap-3 p-4 rounded-xl bg-slate-800/50 hover:bg-cyan-500/10 border border-cyan-500/10 hover:border-cyan-500/30 transition-all duration-300 group"
              >
                <div className={cn(
                  'w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center',
                  item.color,
                  'shadow-lg group-hover:shadow-xl group-hover:scale-110 transition-all'
                )}>
                  <item.icon className="w-6 h-6 text-white" />
                </div>
                <span className="text-sm text-slate-300 group-hover:text-cyan-400 transition-colors">
                  {item.name}
                </span>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
