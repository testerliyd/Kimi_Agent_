import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';

import { roleApi, permissionApi } from '@/services/api';
import type { Role, Permission } from '@/types';
import {
  Plus,
  Edit2,
  Trash2,
  Shield,
  Check,
  X,
  Key,
  ChevronRight,
  ChevronDown,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function RoleManagement() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissionsByModule, setPermissionsByModule] = useState<Record<string, Permission[]>>({});
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [permissionDialogOpen, setPermissionDialogOpen] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [managingRole, setManagingRole] = useState<Role | null>(null);
  const [formData, setFormData] = useState<Partial<Role>>({
    name: '',
    code: '',
    description: '',
  });
  const [selectedPermissions, setSelectedPermissions] = useState<number[]>([]);
  const [expandedModules, setExpandedModules] = useState<string[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [rolesRes, permissionsRes] = await Promise.all([
        roleApi.getRoles(),
        permissionApi.getPermissions(),
      ]);

      if (rolesRes.code === 200) {
        setRoles(rolesRes.data);
      }
      if (permissionsRes.code === 200) {
        // 按模块分组
        const grouped: Record<string, Permission[]> = {};
        permissionsRes.data.forEach((p) => {
          if (!grouped[p.module]) {
            grouped[p.module] = [];
          }
          grouped[p.module].push(p);
        });
        setPermissionsByModule(grouped);
      }
    } catch (error) {
      console.error('获取数据失败:', error);
      // 模拟数据
      const mockPermissions: Permission[] = [
        { id: 1, name: '查看项目', code: 'project.view', description: '查看项目列表和详情', module: 'project' },
        { id: 2, name: '创建项目', code: 'project.create', description: '创建新项目', module: 'project' },
        { id: 3, name: '编辑项目', code: 'project.edit', description: '编辑项目信息', module: 'project' },
        { id: 4, name: '删除项目', code: 'project.delete', description: '删除项目', module: 'project' },
        { id: 5, name: '查看用例', code: 'testcase.view', description: '查看测试用例', module: 'testcase' },
        { id: 6, name: '创建用例', code: 'testcase.create', description: '创建测试用例', module: 'testcase' },
        { id: 7, name: '编辑用例', code: 'testcase.edit', description: '编辑测试用例', module: 'testcase' },
        { id: 8, name: '删除用例', code: 'testcase.delete', description: '删除测试用例', module: 'testcase' },
        { id: 9, name: '查看Bug', code: 'bug.view', description: '查看Bug列表', module: 'bug' },
        { id: 10, name: '创建Bug', code: 'bug.create', description: '提交新Bug', module: 'bug' },
        { id: 11, name: '编辑Bug', code: 'bug.edit', description: '编辑Bug信息', module: 'bug' },
        { id: 12, name: '删除Bug', code: 'bug.delete', description: '删除Bug', module: 'bug' },
        { id: 13, name: '查看用户', code: 'user.view', description: '查看用户列表', module: 'user' },
        { id: 14, name: '创建用户', code: 'user.create', description: '创建新用户', module: 'user' },
        { id: 15, name: '编辑用户', code: 'user.edit', description: '编辑用户信息', module: 'user' },
        { id: 16, name: '删除用户', code: 'user.delete', description: '删除用户', module: 'user' },
      ];
      const grouped: Record<string, Permission[]> = {};
      mockPermissions.forEach((p) => {
        if (!grouped[p.module]) {
          grouped[p.module] = [];
        }
        grouped[p.module].push(p);
      });
      setPermissionsByModule(grouped);
      setRoles([
        { id: 1, name: '管理员', code: 'admin', description: '系统管理员，拥有所有权限', permissions: mockPermissions, created_at: '', updated_at: '' },
        { id: 2, name: '测试人员', code: 'tester', description: '测试工程师，可管理用例和Bug', permissions: mockPermissions.filter(p => ['testcase', 'bug'].includes(p.module)), created_at: '', updated_at: '' },
        { id: 3, name: '开发人员', code: 'developer', description: '开发工程师，可查看和编辑Bug', permissions: mockPermissions.filter(p => p.module === 'bug'), created_at: '', updated_at: '' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (role?: Role) => {
    if (role) {
      setEditingRole(role);
      setFormData({
        name: role.name,
        code: role.code,
        description: role.description,
      });
    } else {
      setEditingRole(null);
      setFormData({
        name: '',
        code: '',
        description: '',
      });
    }
    setDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      if (editingRole) {
        const response = await roleApi.updateRole(editingRole.id, formData);
        if (response.code === 200) {
          fetchData();
        }
      } else {
        const response = await roleApi.createRole(formData);
        if (response.code === 200) {
          fetchData();
        }
      }
      setDialogOpen(false);
    } catch (error) {
      console.error('保存角色失败:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此角色吗？')) return;
    try {
      await roleApi.deleteRole(id);
      fetchData();
    } catch (error) {
      console.error('删除角色失败:', error);
    }
  };

  const handleManagePermissions = (role: Role) => {
    setManagingRole(role);
    setSelectedPermissions(role.permissions?.map((p) => p.id) || []);
    setExpandedModules(Object.keys(permissionsByModule));
    setPermissionDialogOpen(true);
  };

  const handleSavePermissions = async () => {
    if (!managingRole) return;
    try {
      await roleApi.updateRolePermissions(managingRole.id, selectedPermissions);
      fetchData();
      setPermissionDialogOpen(false);
    } catch (error) {
      console.error('保存权限失败:', error);
    }
  };

  const toggleModule = (module: string) => {
    setExpandedModules((prev) =>
      prev.includes(module) ? prev.filter((m) => m !== module) : [...prev, module]
    );
  };

  const togglePermission = (permissionId: number) => {
    setSelectedPermissions((prev) =>
      prev.includes(permissionId)
        ? prev.filter((id) => id !== permissionId)
        : [...prev, permissionId]
    );
  };

  const selectAllInModule = (module: string, selected: boolean) => {
    const modulePermissions = permissionsByModule[module].map((p) => p.id);
    if (selected) {
      setSelectedPermissions((prev) => [...new Set([...prev, ...modulePermissions])]);
    } else {
      setSelectedPermissions((prev) => prev.filter((id) => !modulePermissions.includes(id)));
    }
  };

  const moduleLabels: Record<string, string> = {
    project: '项目管理',
    testcase: '用例管理',
    bug: 'Bug管理',
    user: '用户管理',
    system: '系统配置',
  };

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
          <h1 className="text-2xl font-bold text-slate-100">角色管理</h1>
          <p className="text-slate-400 mt-1">管理系统角色和权限配置</p>
        </div>
        <Button
          onClick={() => handleOpenDialog()}
          className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          新建角色
        </Button>
      </div>

      {/* 角色列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {roles.map((role) => (
          <Card
            key={role.id}
            className="bg-slate-900/50 backdrop-blur-sm border-cyan-500/20 hover:border-cyan-500/40 transition-all duration-300"
          >
            <CardHeader className="pb-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                    <Shield className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg font-semibold text-slate-100">
                      {role.name}
                    </CardTitle>
                    <p className="text-sm text-slate-400">{role.code}</p>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-slate-400">{role.description}</p>

              <div className="flex items-center gap-2 text-sm text-slate-400">
                <Key className="w-4 h-4" />
                <span>{role.permissions?.length || 0} 个权限</span>
              </div>

              <div className="flex flex-wrap gap-1">
                {role.permissions?.slice(0, 5).map((permission) => (
                  <Badge
                    key={permission.id}
                    variant="outline"
                    className="border-cyan-500/30 text-cyan-400 text-xs"
                  >
                    {permission.name}
                  </Badge>
                ))}
                {(role.permissions?.length || 0) > 5 && (
                  <Badge variant="outline" className="border-slate-600 text-slate-400 text-xs">
                    +{(role.permissions?.length || 0) - 5}
                  </Badge>
                )}
              </div>

              <div className="flex items-center gap-2 pt-4 border-t border-cyan-500/10">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleOpenDialog(role)}
                  className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
                >
                  <Edit2 className="w-4 h-4 mr-1" />
                  编辑
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleManagePermissions(role)}
                  className="border-purple-500/30 text-purple-400 hover:bg-purple-500/10"
                >
                  <Key className="w-4 h-4 mr-1" />
                  权限
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDelete(role.id)}
                  className="border-red-500/30 text-red-400 hover:bg-red-500/10 ml-auto"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 新建/编辑角色对话框 */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="bg-slate-900 border-cyan-500/30">
          <DialogHeader>
            <DialogTitle className="text-xl font-semibold text-slate-100">
              {editingRole ? '编辑角色' : '新建角色'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label className="text-slate-300">角色名称</Label>
              <div className="relative">
                <Shield className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="例如：测试人员"
                  className="bg-slate-800 border-slate-700 text-slate-200 pl-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">角色代码</Label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <Input
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  placeholder="例如：tester"
                  className="bg-slate-800 border-slate-700 text-slate-200 pl-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">描述</Label>
              <Input
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="角色描述"
                className="bg-slate-800 border-slate-700 text-slate-200"
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

      {/* 权限管理对话框 */}
      <Dialog open={permissionDialogOpen} onOpenChange={setPermissionDialogOpen}>
        <DialogContent className="bg-slate-900 border-cyan-500/30 max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl font-semibold text-slate-100">
              管理权限 - {managingRole?.name}
            </DialogTitle>
          </DialogHeader>

          <div className="py-4 space-y-4">
            {Object.entries(permissionsByModule).map(([module, modulePermissions]) => {
              const isExpanded = expandedModules.includes(module);
              const allSelected = modulePermissions.every((p) =>
                selectedPermissions.includes(p.id)
              );


              return (
                <div
                  key={module}
                  className="border border-slate-700 rounded-lg overflow-hidden"
                >
                  <div
                    className="flex items-center justify-between p-3 bg-slate-800/50 cursor-pointer"
                    onClick={() => toggleModule(module)}
                  >
                    <div className="flex items-center gap-3">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          selectAllInModule(module, !allSelected);
                        }}
                      >
                        <Checkbox
                          checked={allSelected}
                          className={cn(
                            'border-slate-500 data-[state=checked]:bg-cyan-500 data-[state=checked]:border-cyan-500'
                          )}
                        />
                      </button>
                      <span className="font-medium text-slate-200">
                        {moduleLabels[module] || module}
                      </span>
                      <Badge variant="outline" className="border-slate-600 text-slate-400 text-xs">
                        {modulePermissions.length}
                      </Badge>
                    </div>
                    {isExpanded ? (
                      <ChevronDown className="w-5 h-5 text-slate-400" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-slate-400" />
                    )}
                  </div>

                  {isExpanded && (
                    <div className="p-3 space-y-2">
                      {modulePermissions.map((permission) => (
                        <div
                          key={permission.id}
                          className={cn(
                            'flex items-start gap-3 p-2 rounded-lg cursor-pointer transition-all',
                            selectedPermissions.includes(permission.id)
                              ? 'bg-cyan-500/10'
                              : 'hover:bg-slate-800/50'
                          )}
                          onClick={() => togglePermission(permission.id)}
                        >
                          <Checkbox
                            checked={selectedPermissions.includes(permission.id)}
                            className="mt-0.5 border-slate-500 data-[state=checked]:bg-cyan-500 data-[state=checked]:border-cyan-500"
                          />
                          <div>
                            <p className="text-sm font-medium text-slate-200">
                              {permission.name}
                            </p>
                            <p className="text-xs text-slate-400">
                              {permission.description}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <DialogFooter>
            <div className="flex items-center gap-4 mr-auto">
              <span className="text-sm text-slate-400">
                已选择 {selectedPermissions.length} 个权限
              </span>
            </div>
            <Button
              variant="outline"
              onClick={() => setPermissionDialogOpen(false)}
              className="border-slate-600 text-slate-300 hover:bg-slate-800"
            >
              <X className="w-4 h-4 mr-2" />
              取消
            </Button>
            <Button
              onClick={handleSavePermissions}
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
