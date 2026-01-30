import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import Layout from '@/components/layout/Layout';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import ProjectManagement from '@/pages/ProjectManagement';
import TestCaseManagement from '@/pages/TestCaseManagement';
import BugManagement from '@/pages/BugManagement';
import AutomationTest from '@/pages/AutomationTest';
import LLMConfig from '@/pages/LLMConfig';
import FeishuConfig from '@/pages/FeishuConfig';
import UserManagement from '@/pages/UserManagement';
import RoleManagement from '@/pages/RoleManagement';
import DatabaseConfig from '@/pages/DatabaseConfig';
import RedisConfig from '@/pages/RedisConfig';
import SystemConfig from '@/pages/SystemConfig';

// 受保护路由组件
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// 公开路由组件（已登录用户重定向到首页）
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      {/* 登录页面 */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />

      {/* 受保护的路由 */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* 仪表盘 */}
        <Route index element={<Dashboard />} />

        {/* 项目管理 */}
        <Route path="projects" element={<ProjectManagement />} />

        {/* 用例管理 */}
        <Route path="testcases" element={<TestCaseManagement />} />

        {/* Bug管理 */}
        <Route path="bugs" element={<BugManagement />} />

        {/* 自动化测试 */}
        <Route path="automation" element={<AutomationTest />} />

        {/* 系统配置 */}
        <Route path="config">
          <Route path="database" element={<DatabaseConfig />} />
          <Route path="redis" element={<RedisConfig />} />
          <Route path="llm" element={<LLMConfig />} />
          <Route path="feishu" element={<FeishuConfig />} />
          <Route path="system" element={<SystemConfig />} />
        </Route>

        {/* 权限管理 */}
        <Route path="auth">
          <Route path="users" element={<UserManagement />} />
          <Route path="roles" element={<RoleManagement />} />
        </Route>

        {/* 个人资料 */}
        <Route path="profile" element={<div className="text-slate-100">个人资料（开发中）</div>} />

        {/* 404页面 */}
        <Route path="*" element={<div className="text-slate-100">页面不存在</div>} />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
