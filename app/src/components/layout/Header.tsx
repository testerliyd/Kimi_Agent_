import { useState } from 'react';
import { User, LogOut, Settings, ChevronDown } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';
import NotificationCenter from '@/components/NotificationCenter';

interface HeaderProps {
  collapsed: boolean;
}

export default function Header({ collapsed }: HeaderProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [notificationCount, setNotificationCount] = useState(0);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header
      className={cn(
        'fixed top-0 right-0 h-16 bg-slate-900/95 backdrop-blur-xl border-b border-cyan-500/20 transition-all duration-300 z-30 flex items-center justify-between px-6',
        collapsed ? 'left-16' : 'left-64'
      )}
    >
      {/* 左侧 - 页面标题 */}
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold text-slate-100">
          智能测试平台
        </h1>
        <div className="h-6 w-px bg-cyan-500/30" />
        <span className="text-sm text-slate-400">
          {new Date().toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'long',
          })}
        </span>
      </div>

      {/* 右侧 - 用户操作 */}
      <div className="flex items-center gap-4">
        {/* 通知中心 */}
        <NotificationCenter onCountChange={setNotificationCount} />

        {/* 用户菜单 */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="flex items-center gap-2 text-slate-300 hover:text-cyan-400 hover:bg-cyan-500/10"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_10px_rgba(34,211,238,0.3)]">
                <User className="w-4 h-4 text-white" />
              </div>
              <span className="hidden sm:inline">{user?.username || '用户'}</span>
              <ChevronDown className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48 bg-slate-800 border-cyan-500/30">
            <div className="px-3 py-2 border-b border-cyan-500/20">
              <p className="font-medium text-slate-200">{user?.username}</p>
              <p className="text-xs text-slate-400">{user?.email}</p>
            </div>
            <DropdownMenuItem asChild className="cursor-pointer hover:bg-cyan-500/10 focus:bg-cyan-500/10">
              <Link to="/profile" className="flex items-center gap-2">
                <User className="w-4 h-4" />
                个人资料
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild className="cursor-pointer hover:bg-cyan-500/10 focus:bg-cyan-500/10">
              <Link to="/config/system" className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                系统设置
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator className="bg-cyan-500/20" />
            <DropdownMenuItem
              onClick={handleLogout}
              className="cursor-pointer text-red-400 hover:text-red-300 hover:bg-red-500/10 focus:bg-red-500/10"
            >
              <LogOut className="w-4 h-4 mr-2" />
              退出登录
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
