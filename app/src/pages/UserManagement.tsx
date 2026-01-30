import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { userApi, roleApi } from '@/services/api';
import type { User, Role } from '@/types';
import {
  Plus,
  Edit2,
  Trash2,
  Search,
  Check,
  X,
  User as UserIcon,
  Mail,
  Shield,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<Partial<User>>({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    is_active: true,
    is_staff: false,
  });
  const [selectedRoles, setSelectedRoles] = useState<number[]>([]);
  const [roleDialogOpen, setRoleDialogOpen] = useState(false);
  const [managingUser, setManagingUser] = useState<User | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [usersRes, rolesRes] = await Promise.all([
        userApi.getUsers(),
        roleApi.getRoles(),
      ]);

      if (usersRes.code === 200) {
        setUsers(usersRes.data.results);
      }
      if (rolesRes.code === 200) {
        setRoles(rolesRes.data);
      }
    } catch (error) {
      console.error('获取数据失败:', error);
      // 模拟数据
      setUsers([
        {
          id: 1,
          username: 'admin',
          email: 'admin@example.com',
          first_name: '系统',
          last_name: '管理员',
          is_active: true,
          is_staff: true,
          date_joined: '2024-01-01T00:00:00Z',
          last_login: '2024-01-30T10:00:00Z',
          roles: [],
        },
        {
          id: 2,
          username: 'tester',
          email: 'tester@example.com',
          first_name: '测试',
          last_name: '人员',
          is_active: true,
          is_staff: false,
          date_joined: '2024-01-15T00:00:00Z',
          last_login: '2024-01-30T09:00:00Z',
          roles: [],
        },
      ]);
      setRoles([
        { id: 1, name: '管理员', code: 'admin', description: '系统管理员', permissions: [], created_at: '', updated_at: '' },
        { id: 2, name: '测试人员', code: 'tester', description: '测试工程师', permissions: [], created_at: '', updated_at: '' },
        { id: 3, name: '开发人员', code: 'developer', description: '开发工程师', permissions: [], created_at: '', updated_at: '' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (user?: User) => {
    if (user) {
      setEditingUser(user);
      setFormData({
        username: user.username,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        is_active: user.is_active,
        is_staff: user.is_staff,
      });
    } else {
      setEditingUser(null);
      setFormData({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        is_active: true,
        is_staff: false,
      });
    }
    setDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      if (editingUser) {
        const response = await userApi.updateUser(editingUser.id, formData);
        if (response.code === 200) {
          fetchData();
        }
      } else {
        const response = await userApi.createUser(formData);
        if (response.code === 200) {
          fetchData();
        }
      }
      setDialogOpen(false);
    } catch (error) {
      console.error('保存用户失败:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此用户吗？')) return;
    try {
      await userApi.deleteUser(id);
      fetchData();
    } catch (error) {
      console.error('删除用户失败:', error);
    }
  };

  const handleManageRoles = (user: User) => {
    setManagingUser(user);
    setSelectedRoles(user.roles?.map((r) => r.id) || []);
    setRoleDialogOpen(true);
  };

  const handleSaveRoles = async () => {
    if (!managingUser) return;
    try {
      await userApi.updateUserRoles(managingUser.id, selectedRoles);
      fetchData();
      setRoleDialogOpen(false);
    } catch (error) {
      console.error('保存角色失败:', error);
    }
  };

  const filteredUsers = users.filter(
    (user) =>
      user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.first_name.includes(searchQuery) ||
      user.last_name.includes(searchQuery)
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">用户管理</h1>
          <p className="text-slate-400 mt-1">管理系统用户账号和权限</p>
        </div>
        <Button
          onClick={() => handleOpenDialog()}
          className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          新建用户
        </Button>
      </div>

      {/* 搜索栏 */}
      <Card className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20">
        <CardContent className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索用户名、邮箱或姓名..."
              className="bg-slate-800 border-slate-700 text-slate-200 pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* 用户列表 */}
      <Card className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="border-cyan-500/20 hover:bg-transparent">
                <TableHead className="text-slate-400">用户</TableHead>
                <TableHead className="text-slate-400">邮箱</TableHead>
                <TableHead className="text-slate-400">姓名</TableHead>
                <TableHead className="text-slate-400">角色</TableHead>
                <TableHead className="text-slate-400">状态</TableHead>
                <TableHead className="text-slate-400">最后登录</TableHead>
                <TableHead className="text-slate-400 text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredUsers.map((user) => (
                <TableRow
                  key={user.id}
                  className="border-cyan-500/10 hover:bg-cyan-500/5"
                >
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                        <span className="text-sm font-medium text-white">
                          {user.username.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <span className="font-medium text-slate-200">{user.username}</span>
                      {user.is_staff && (
                        <Badge className="bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
                          管理员
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="text-slate-400">{user.email}</TableCell>
                  <TableCell className="text-slate-400">
                    {user.first_name} {user.last_name}
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {user.roles?.map((role) => (
                        <Badge
                          key={role.id}
                          variant="outline"
                          className="border-cyan-500/30 text-cyan-400 text-xs"
                        >
                          {role.name}
                        </Badge>
                      ))}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleManageRoles(user)}
                        className="h-5 px-2 text-xs text-slate-500 hover:text-cyan-400"
                      >
                        <Plus className="w-3 h-3" />
                      </Button>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={cn(
                        'text-xs',
                        user.is_active
                          ? 'border-green-500/30 text-green-400'
                          : 'border-red-500/30 text-red-400'
                      )}
                    >
                      {user.is_active ? '激活' : '禁用'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-slate-400 text-sm">
                    {user.last_login
                      ? new Date(user.last_login).toLocaleString('zh-CN')
                      : '从未登录'}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleOpenDialog(user)}
                        className="text-slate-400 hover:text-cyan-400"
                      >
                        <Edit2 className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(user.id)}
                        className="text-slate-400 hover:text-red-400"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* 新建/编辑用户对话框 */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="bg-slate-900 border-cyan-500/30">
          <DialogHeader>
            <DialogTitle className="text-xl font-semibold text-slate-100">
              {editingUser ? '编辑用户' : '新建用户'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label className="text-slate-300">用户名</Label>
              <div className="relative">
                <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  placeholder="请输入用户名"
                  className="bg-slate-800 border-slate-700 text-slate-200 pl-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">邮箱</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="请输入邮箱"
                  className="bg-slate-800 border-slate-700 text-slate-200 pl-10"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-300">姓</Label>
                <Input
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  placeholder="姓"
                  className="bg-slate-800 border-slate-700 text-slate-200"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300">名</Label>
                <Input
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  placeholder="名"
                  className="bg-slate-800 border-slate-700 text-slate-200"
                />
              </div>
            </div>

            {!editingUser && (
              <div className="space-y-2">
                <Label className="text-slate-300">密码</Label>
                <Input
                  type="password"
                  placeholder="请输入密码"
                  className="bg-slate-800 border-slate-700 text-slate-200"
                />
              </div>
            )}

            <div className="flex items-center justify-between">
              <Label className="text-slate-300">激活状态</Label>
              <Switch
                checked={formData.is_active}
                onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
                className="data-[state=checked]:bg-cyan-500"
              />
            </div>

            <div className="flex items-center justify-between">
              <Label className="text-slate-300">管理员权限</Label>
              <Switch
                checked={formData.is_staff}
                onCheckedChange={(checked) => setFormData({ ...formData, is_staff: checked })}
                className="data-[state=checked]:bg-cyan-500"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDialogOpen(false)}
              className="border-slate-600 text-slate-300 hover:bg-slate-800"
            >
              <X className="w-4 h-4 mr-2" />
              取消
            </Button>
            <Button
              onClick={handleSave}
              className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white"
            >
              <Check className="w-4 h-4 mr-2" />
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 角色管理对话框 */}
      <Dialog open={roleDialogOpen} onOpenChange={setRoleDialogOpen}>
        <DialogContent className="bg-slate-900 border-cyan-500/30">
          <DialogHeader>
            <DialogTitle className="text-xl font-semibold text-slate-100">
              管理角色 - {managingUser?.username}
            </DialogTitle>
          </DialogHeader>

          <div className="py-4">
            <div className="space-y-2">
              {roles.map((role) => (
                <div
                  key={role.id}
                  className={cn(
                    'flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-all',
                    selectedRoles.includes(role.id)
                      ? 'border-cyan-500/50 bg-cyan-500/10'
                      : 'border-slate-700 bg-slate-800/50 hover:border-cyan-500/30'
                  )}
                  onClick={() => {
                    setSelectedRoles((prev) =>
                      prev.includes(role.id)
                        ? prev.filter((id) => id !== role.id)
                        : [...prev, role.id]
                    );
                  }}
                >
                  <div className="flex items-center gap-3">
                    <Shield className="w-5 h-5 text-cyan-400" />
                    <div>
                      <p className="font-medium text-slate-200">{role.name}</p>
                      <p className="text-sm text-slate-400">{role.description}</p>
                    </div>
                  </div>
                  {selectedRoles.includes(role.id) && (
                    <Check className="w-5 h-5 text-cyan-400" />
                  )}
                </div>
              ))}
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setRoleDialogOpen(false)}
              className="border-slate-600 text-slate-300 hover:bg-slate-800"
            >
              <X className="w-4 h-4 mr-2" />
              取消
            </Button>
            <Button
              onClick={handleSaveRoles}
              className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white"
            >
              <Check className="w-4 h-4 mr-2" />
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
