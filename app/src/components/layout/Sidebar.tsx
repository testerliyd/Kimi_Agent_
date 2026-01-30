import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Settings,
  Database,
  Cpu,
  Users,
  Shield,
  Server,
  MessageSquare,
  FolderKanban,
  Bug,
  FileText,
  ChevronLeft,
  ChevronRight,
  Zap,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface MenuItem {
  path: string;
  name: string;
  icon: React.ElementType;
  children?: MenuItem[];
}

const menuItems: MenuItem[] = [
  { path: '/', name: '仪表盘', icon: LayoutDashboard },
  { path: '/projects', name: '项目管理', icon: FolderKanban },
  { path: '/testcases', name: '用例管理', icon: FileText },
  { path: '/bugs', name: 'Bug管理', icon: Bug },
  { path: '/automation', name: '自动化测试', icon: Zap },
  {
    path: '/config',
    name: '系统配置',
    icon: Settings,
    children: [
      { path: '/config/database', name: '数据库配置', icon: Database },
      { path: '/config/redis', name: 'Redis配置', icon: Server },
      { path: '/config/llm', name: '大模型配置', icon: Cpu },
      { path: '/config/feishu', name: '飞书配置', icon: MessageSquare },
      { path: '/config/system', name: '系统设置', icon: Settings },
    ],
  },
  {
    path: '/auth',
    name: '权限管理',
    icon: Shield,
    children: [
      { path: '/auth/users', name: '用户管理', icon: Users },
      { path: '/auth/roles', name: '角色管理', icon: Shield },
    ],
  },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export default function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const location = useLocation();
  const [expandedMenus, setExpandedMenus] = useState<string[]>(['/config', '/auth']);

  const toggleMenu = (path: string) => {
    setExpandedMenus((prev) =>
      prev.includes(path) ? prev.filter((p) => p !== path) : [...prev, path]
    );
  };

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const renderMenuItem = (item: MenuItem, level: number = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedMenus.includes(item.path);
    const active = isActive(item.path);

    if (hasChildren) {
      return (
        <div key={item.path}>
          <button
            onClick={() => toggleMenu(item.path)}
            className={cn(
              'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 group',
              active
                ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-400 border-l-2 border-cyan-400'
                : 'text-slate-400 hover:text-cyan-400 hover:bg-cyan-500/10'
            )}
            style={{ paddingLeft: collapsed ? '1rem' : `${level * 12 + 16}px` }}
          >
            <item.icon className={cn(
              'w-5 h-5 transition-all duration-300',
              active && 'text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]'
            )} />
            {!collapsed && (
              <>
                <span className="flex-1 text-left font-medium">{item.name}</span>
                <ChevronLeft
                  className={cn(
                    'w-4 h-4 transition-transform duration-300',
                    isExpanded && '-rotate-90'
                  )}
                />
              </>
            )}
          </button>
          {!collapsed && isExpanded && (
            <div className="mt-1 space-y-1 animate-in slide-in-from-left-2 duration-200">
              {item.children?.map((child) => renderMenuItem(child, level + 1))}
            </div>
          )}
        </div>
      );
    }

    return (
      <Link
        key={item.path}
        to={item.path}
        className={cn(
          'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 group',
          active
            ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-400 border-l-2 border-cyan-400'
            : 'text-slate-400 hover:text-cyan-400 hover:bg-cyan-500/10'
        )}
        style={{ paddingLeft: collapsed ? '1rem' : `${level * 12 + 16}px` }}
      >
        <item.icon className={cn(
          'w-5 h-5 transition-all duration-300',
          active && 'text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]'
        )} />
        {!collapsed && (
          <span className="font-medium">{item.name}</span>
        )}
        {collapsed && active && (
          <div className="absolute left-full ml-2 px-3 py-1.5 bg-slate-800 text-cyan-400 text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-50 border border-cyan-500/30 shadow-[0_0_15px_rgba(34,211,238,0.3)]">
            {item.name}
          </div>
        )}
      </Link>
    );
  };

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-screen bg-slate-900/95 backdrop-blur-xl border-r border-cyan-500/20 transition-all duration-300 z-40',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo区域 */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-cyan-500/20">
        {!collapsed && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(34,211,238,0.5)]">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              SmartTest
            </span>
          </div>
        )}
        {collapsed && (
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(34,211,238,0.5)]">
            <Zap className="w-5 h-5 text-white" />
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-400 hover:bg-cyan-500/10 transition-all"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* 菜单区域 */}
      <nav className="p-3 space-y-1 overflow-y-auto h-[calc(100vh-4rem)] scrollbar-thin scrollbar-thumb-cyan-500/30 scrollbar-track-transparent">
        {menuItems.map((item) => renderMenuItem(item))}
      </nav>

      {/* 底部装饰 */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500 opacity-50" />
    </aside>
  );
}
