import type {
  ApiResponse,
  AuthResponse,
  DatabaseConfig,
  FeishuConfig,
  LLMConfig,
  LoginCredentials,
  PaginatedResponse,
  Permission,
  Project,
  RedisConfig,
  Role,
  SystemConfig,
  User,
  TestCase,
  TestSuite,
  TestPlan,
  Bug,
  ApiDefinition,
  ApiTestCase,
  ApiTestJob,
  PerfTestScenario,
  PerfTestJob,
  Notification,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// 获取token
const getToken = (): string | null => {
  return localStorage.getItem('access_token');
};

// 通用请求函数
async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    const error = await response.json().catch(() => ({ message: '请求失败' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json() as Promise<T>;
}

// 认证相关API
export const authApi = {
  login: (credentials: LoginCredentials) =>
    request<ApiResponse<AuthResponse>>('/users/auth/login/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

  logout: () =>
    request<ApiResponse<void>>('/users/auth/logout/', {
      method: 'POST',
    }),

  refreshToken: (refresh: string) =>
    request<ApiResponse<{ access: string }>>('/users/auth/token/refresh/', {
      method: 'POST',
      body: JSON.stringify({ refresh }),
    }),

  getCurrentUser: () => request<ApiResponse<User>>('/users/auth/me/'),

  changePassword: (data: { old_password: string; new_password: string }) =>
    request<ApiResponse<void>>('/users/auth/change-password/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// 用户管理API
export const userApi = {
  getUsers: (params?: { page?: number; page_size?: number; search?: string }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.search) queryParams.append('search', params.search);
    return request<ApiResponse<PaginatedResponse<User>>>(`/users/?${queryParams.toString()}`);
  },

  getUser: (id: number) => request<ApiResponse<User>>(`/users/${id}/`),

  createUser: (data: Partial<User>) =>
    request<ApiResponse<User>>('/users/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateUser: (id: number, data: Partial<User>) =>
    request<ApiResponse<User>>(`/users/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteUser: (id: number) =>
    request<ApiResponse<void>>(`/users/${id}/`, {
      method: 'DELETE',
    }),

  updateUserRoles: (id: number, roleIds: number[]) =>
    request<ApiResponse<User>>(`/users/${id}/update-roles/`, {
      method: 'POST',
      body: JSON.stringify({ roles: roleIds }),
    }),
};

// 角色管理API
export const roleApi = {
  getRoles: (params?: { page?: number; page_size?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    return request<ApiResponse<PaginatedResponse<Role>>>(`/users/roles/?${queryParams.toString()}`);
  },

  getRole: (id: number) => request<ApiResponse<Role>>(`/users/roles/${id}/`),

  createRole: (data: Partial<Role>) =>
    request<ApiResponse<Role>>('/users/roles/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateRole: (id: number, data: Partial<Role>) =>
    request<ApiResponse<Role>>(`/users/roles/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteRole: (id: number) =>
    request<ApiResponse<void>>(`/users/roles/${id}/`, {
      method: 'DELETE',
    }),

  updateRolePermissions: (id: number, permissionIds: number[]) =>
    request<ApiResponse<Role>>(`/users/roles/${id}/update-permissions/`, {
      method: 'POST',
      body: JSON.stringify({ permissions: permissionIds }),
    }),
};

// 权限管理API
export const permissionApi = {
  getPermissions: () => request<ApiResponse<Permission[]>>('/users/permissions/'),

  getPermissionsByModule: () => request<ApiResponse<Record<string, Permission[]>>>('/users/permissions/by-module/'),
};

// 项目管理API
export const projectApi = {
  getProjects: (params?: { page?: number; page_size?: number; search?: string; status?: string }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.status) queryParams.append('status', params.status);
    return request<ApiResponse<PaginatedResponse<Project>>>(`/projects/?${queryParams.toString()}`);
  },

  getProject: (id: number) => request<ApiResponse<Project>>(`/projects/${id}/`),

  createProject: (data: Partial<Project>) =>
    request<ApiResponse<Project>>('/projects/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateProject: (id: number, data: Partial<Project>) =>
    request<ApiResponse<Project>>(`/projects/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteProject: (id: number) =>
    request<ApiResponse<void>>(`/projects/${id}/`, {
      method: 'DELETE',
    }),

  getProjectMembers: (projectId: number) =>
    request<ApiResponse<any[]>>(`/projects/${projectId}/members/`),

  addProjectMember: (projectId: number, data: { user_id: number; role: string }) =>
    request<ApiResponse<any>>(`/projects/${projectId}/add_member/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  removeProjectMember: (projectId: number, data: { user_id: number }) =>
    request<ApiResponse<any>>(`/projects/${projectId}/remove_member/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getProjectVersions: (projectId: number) =>
    request<ApiResponse<any[]>>(`/projects/versions/?project=${projectId}`),

  getProjectMilestones: (projectId: number) =>
    request<ApiResponse<any[]>>(`/projects/milestones/?project=${projectId}`),

  getProjectEnvironments: (projectId: number) =>
    request<ApiResponse<any[]>>(`/projects/environments/?project=${projectId}`),

  getStatistics: () =>
    request<ApiResponse<any>>('/projects/statistics/'),

  getMyProjects: () =>
    request<ApiResponse<Project[]>>('/projects/my_projects/'),
};

// 测试用例管理API
export const testcaseApi = {
  getTestCases: (params?: { page?: number; page_size?: number; search?: string; project?: number; status?: string }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.project) queryParams.append('project', params.project.toString());
    if (params?.status) queryParams.append('status', params.status);
    return request<ApiResponse<PaginatedResponse<TestCase>>>(`/testcases/cases/?${queryParams.toString()}`);
  },

  getTestCase: (id: number) => request<ApiResponse<TestCase>>(`/testcases/cases/${id}/`),

  createTestCase: (data: Partial<TestCase>) =>
    request<ApiResponse<TestCase>>('/testcases/cases/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateTestCase: (id: number, data: Partial<TestCase>) =>
    request<ApiResponse<TestCase>>(`/testcases/cases/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteTestCase: (id: number) =>
    request<ApiResponse<void>>(`/testcases/cases/${id}/`, {
      method: 'DELETE',
    }),

  executeTestCase: (id: number, data: { result: string; actual_result?: string }) =>
    request<ApiResponse<any>>(`/testcases/cases/${id}/execute/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  batchExecute: (data: { case_ids: number[]; result: string }) =>
    request<ApiResponse<any>>('/testcases/cases/batch_execute/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getTestSuites: (params?: { page?: number; project?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.project) queryParams.append('project', params.project.toString());
    return request<ApiResponse<PaginatedResponse<TestSuite>>>(`/testcases/suites/?${queryParams.toString()}`);
  },

  getTestSuite: (id: number) => request<ApiResponse<TestSuite>>(`/testcases/suites/${id}/`),

  createTestSuite: (data: Partial<TestSuite>) =>
    request<ApiResponse<TestSuite>>('/testcases/suites/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateTestSuite: (id: number, data: Partial<TestSuite>) =>
    request<ApiResponse<TestSuite>>(`/testcases/suites/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteTestSuite: (id: number) =>
    request<ApiResponse<void>>(`/testcases/suites/${id}/`, {
      method: 'DELETE',
    }),

  addCasesToSuite: (suiteId: number, caseIds: number[]) =>
    request<ApiResponse<any>>(`/testcases/suites/${suiteId}/add_cases/`, {
      method: 'POST',
      body: JSON.stringify({ case_ids: caseIds }),
    }),

  removeCasesFromSuite: (suiteId: number, caseIds: number[]) =>
    request<ApiResponse<any>>(`/testcases/suites/${suiteId}/remove_cases/`, {
      method: 'POST',
      body: JSON.stringify({ case_ids: caseIds }),
    }),

  getTestPlans: (params?: { page?: number; project?: number; status?: string }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.project) queryParams.append('project', params.project.toString());
    if (params?.status) queryParams.append('status', params.status);
    return request<ApiResponse<PaginatedResponse<TestPlan>>>(`/testcases/plans/?${queryParams.toString()}`);
  },

  getTestPlan: (id: number) => request<ApiResponse<TestPlan>>(`/testcases/plans/${id}/`),

  createTestPlan: (data: Partial<TestPlan>) =>
    request<ApiResponse<TestPlan>>('/testcases/plans/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateTestPlan: (id: number, data: Partial<TestPlan>) =>
    request<ApiResponse<TestPlan>>(`/testcases/plans/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteTestPlan: (id: number) =>
    request<ApiResponse<void>>(`/testcases/plans/${id}/`, {
      method: 'DELETE',
    }),

  startTestPlan: (id: number) =>
    request<ApiResponse<any>>(`/testcases/plans/${id}/start/`, {
      method: 'POST',
    }),

  completeTestPlan: (id: number) =>
    request<ApiResponse<any>>(`/testcases/plans/${id}/complete/`, {
      method: 'POST',
    }),

  getStatistics: () =>
    request<ApiResponse<any>>('/testcases/cases/statistics/'),
};

// Bug管理API
export const bugApi = {
  getBugs: (params?: { page?: number; page_size?: number; search?: string; project?: number; status?: string; severity?: string }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.project) queryParams.append('project', params.project.toString());
    if (params?.status) queryParams.append('status', params.status);
    if (params?.severity) queryParams.append('severity', params.severity);
    return request<ApiResponse<PaginatedResponse<Bug>>>(`/bugs/?${queryParams.toString()}`);
  },

  getBug: (id: number) => request<ApiResponse<Bug>>(`/bugs/${id}/`),

  createBug: (data: Partial<Bug>) =>
    request<ApiResponse<Bug>>('/bugs/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateBug: (id: number, data: Partial<Bug>) =>
    request<ApiResponse<Bug>>(`/bugs/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteBug: (id: number) =>
    request<ApiResponse<void>>(`/bugs/${id}/`, {
      method: 'DELETE',
    }),

  assignBug: (id: number, data: { assignee_id: number }) =>
    request<ApiResponse<any>>(`/bugs/${id}/assign/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  resolveBug: (id: number, data: { resolution: string; resolved_version_id?: number }) =>
    request<ApiResponse<any>>(`/bugs/${id}/resolve/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  closeBug: (id: number) =>
    request<ApiResponse<any>>(`/bugs/${id}/close/`, {
      method: 'POST',
    }),

  reopenBug: (id: number, data: { reason: string }) =>
    request<ApiResponse<any>>(`/bugs/${id}/reopen/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getBugComments: (bugId: number) =>
    request<ApiResponse<any[]>>(`/bugs/${bugId}/comments/`),

  addBugComment: (bugId: number, data: { content: string; is_internal?: boolean }) =>
    request<ApiResponse<any>>(`/bugs/${bugId}/add_comment/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getBugHistory: (bugId: number) =>
    request<ApiResponse<any[]>>(`/bugs/${bugId}/history/`),

  getStatistics: () =>
    request<ApiResponse<any>>('/bugs/statistics/'),

  getMyBugs: () =>
    request<ApiResponse<Bug[]>>('/bugs/my_bugs/'),

  getReportedByMe: () =>
    request<ApiResponse<Bug[]>>('/bugs/reported_by_me/'),
};

// 接口测试API
export const apiTestApi = {
  getApiDefinitions: (params?: { page?: number; page_size?: number; search?: string; project?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.project) queryParams.append('project', params.project.toString());
    return request<ApiResponse<PaginatedResponse<ApiDefinition>>>(`/apitest/definitions/?${queryParams.toString()}`);
  },

  getApiDefinition: (id: number) => request<ApiResponse<ApiDefinition>>(`/apitest/definitions/${id}/`),

  createApiDefinition: (data: Partial<ApiDefinition>) =>
    request<ApiResponse<ApiDefinition>>('/apitest/definitions/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateApiDefinition: (id: number, data: Partial<ApiDefinition>) =>
    request<ApiResponse<ApiDefinition>>(`/apitest/definitions/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteApiDefinition: (id: number) =>
    request<ApiResponse<void>>(`/apitest/definitions/${id}/`, {
      method: 'DELETE',
    }),

  getApiTestCases: (params?: { page?: number; page_size?: number; search?: string; project?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.project) queryParams.append('project', params.project.toString());
    return request<ApiResponse<PaginatedResponse<ApiTestCase>>>(`/apitest/cases/?${queryParams.toString()}`);
  },

  getApiTestCase: (id: number) => request<ApiResponse<ApiTestCase>>(`/apitest/cases/${id}/`),

  createApiTestCase: (data: Partial<ApiTestCase>) =>
    request<ApiResponse<ApiTestCase>>('/apitest/cases/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateApiTestCase: (id: number, data: Partial<ApiTestCase>) =>
    request<ApiResponse<ApiTestCase>>(`/apitest/cases/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteApiTestCase: (id: number) =>
    request<ApiResponse<void>>(`/apitest/cases/${id}/`, {
      method: 'DELETE',
    }),

  runTest: (caseId: number) =>
    request<ApiResponse<{ success: boolean; message: string }>>(`/apitest/cases/${caseId}/run/`, {
      method: 'POST',
    }),

  getApiTestJobs: (params?: { page?: number; page_size?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    return request<ApiResponse<PaginatedResponse<ApiTestJob>>>(`/apitest/jobs/?${queryParams.toString()}`);
  },

  getApiTestResults: (params?: { job?: number; page?: number; page_size?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.job) queryParams.append('job', params.job.toString());
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    return request<ApiResponse<PaginatedResponse<any>>>(`/apitest/results/?${queryParams.toString()}`);
  },
};

// 性能测试API
export const perfTestApi = {
  getScenarios: (params?: { page?: number; page_size?: number; search?: string; project?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.search) queryParams.append('search', params.search);
    if (params?.project) queryParams.append('project', params.project.toString());
    return request<ApiResponse<PaginatedResponse<PerfTestScenario>>>(`/perftest/scenarios/?${queryParams.toString()}`);
  },

  getScenario: (id: number) => request<ApiResponse<PerfTestScenario>>(`/perftest/scenarios/${id}/`),

  createScenario: (data: Partial<PerfTestScenario>) =>
    request<ApiResponse<PerfTestScenario>>('/perftest/scenarios/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateScenario: (id: number, data: Partial<PerfTestScenario>) =>
    request<ApiResponse<PerfTestScenario>>(`/perftest/scenarios/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteScenario: (id: number) =>
    request<ApiResponse<void>>(`/perftest/scenarios/${id}/`, {
      method: 'DELETE',
    }),

  getPerfTestJobs: (params?: { page?: number; page_size?: number; scenario?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.scenario) queryParams.append('scenario', params.scenario.toString());
    return request<ApiResponse<PaginatedResponse<PerfTestJob>>>(`/perftest/jobs/?${queryParams.toString()}`);
  },

  getPerfTestMetrics: (params?: { job?: number; page?: number; page_size?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.job) queryParams.append('job', params.job.toString());
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    return request<ApiResponse<PaginatedResponse<any>>>(`/perftest/metrics/?${queryParams.toString()}`);
  },
};

// 大模型配置API
export const llmApi = {
  getConfigs: (params?: { page?: number; page_size?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    return request<ApiResponse<PaginatedResponse<LLMConfig>>>(`/llm/configs/?${queryParams.toString()}`);
  },

  getConfig: (id: number) => request<ApiResponse<LLMConfig>>(`/llm/configs/${id}/`),

  createConfig: (data: Partial<LLMConfig>) =>
    request<ApiResponse<LLMConfig>>('/llm/configs/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateConfig: (id: number, data: Partial<LLMConfig>) =>
    request<ApiResponse<LLMConfig>>(`/llm/configs/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteConfig: (id: number) =>
    request<ApiResponse<void>>(`/llm/configs/${id}/`, {
      method: 'DELETE',
    }),

  testConfig: (id: number) =>
    request<ApiResponse<{ success: boolean; message: string }>>(`/llm/configs/${id}/test/`, {
      method: 'POST',
    }),

  setDefaultConfig: (id: number) =>
    request<ApiResponse<LLMConfig>>(`/llm/configs/${id}/set_default/`, {
      method: 'POST',
    }),

  getProviders: () => request<ApiResponse<Array<{ code: string; name: string }>>>('/llm/providers/'),
};

// 飞书配置API
export const feishuApi = {
  getConfigs: (params?: { page?: number; page_size?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    return request<ApiResponse<PaginatedResponse<FeishuConfig>>>(`/feishu/configs/?${queryParams.toString()}`);
  },

  getConfig: (id: number) => request<ApiResponse<FeishuConfig>>(`/feishu/configs/${id}/`),

  createConfig: (data: Partial<FeishuConfig>) =>
    request<ApiResponse<FeishuConfig>>('/feishu/configs/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateConfig: (id: number, data: Partial<FeishuConfig>) =>
    request<ApiResponse<FeishuConfig>>(`/feishu/configs/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteConfig: (id: number) =>
    request<ApiResponse<void>>(`/feishu/configs/${id}/`, {
      method: 'DELETE',
    }),

  testWebhook: (id: number) =>
    request<ApiResponse<{ success: boolean; message: string }>>(`/feishu/configs/${id}/test/`, {
      method: 'POST',
    }),

  getTemplates: () => request<ApiResponse<any[]>>('/feishu/templates/'),

  getBindings: () => request<ApiResponse<any[]>>('/feishu/bindings/'),
};

// 数据库配置API
export const databaseApi = {
  getConfigs: (params?: { page?: number; page_size?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    return request<ApiResponse<PaginatedResponse<DatabaseConfig>>>(`/core/database-configs/?${queryParams.toString()}`);
  },

  getConfig: (id: number) => request<ApiResponse<DatabaseConfig>>(`/core/database-configs/${id}/`),

  createConfig: (data: Partial<DatabaseConfig>) =>
    request<ApiResponse<DatabaseConfig>>('/core/database-configs/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateConfig: (id: number, data: Partial<DatabaseConfig>) =>
    request<ApiResponse<DatabaseConfig>>(`/core/database-configs/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteConfig: (id: number) =>
    request<ApiResponse<void>>(`/core/database-configs/${id}/`, {
      method: 'DELETE',
    }),

  testConnection: (id: number) =>
    request<ApiResponse<{ success: boolean; message: string }>>(`/core/database-configs/${id}/test/`, {
      method: 'POST',
    }),
};

// Redis配置API
export const redisApi = {
  getConfigs: (params?: { page?: number; page_size?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    return request<ApiResponse<PaginatedResponse<RedisConfig>>>(`/core/redis-configs/?${queryParams.toString()}`);
  },

  getConfig: (id: number) => request<ApiResponse<RedisConfig>>(`/core/redis-configs/${id}/`),

  createConfig: (data: Partial<RedisConfig>) =>
    request<ApiResponse<RedisConfig>>('/core/redis-configs/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateConfig: (id: number, data: Partial<RedisConfig>) =>
    request<ApiResponse<RedisConfig>>(`/core/redis-configs/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteConfig: (id: number) =>
    request<ApiResponse<void>>(`/core/redis-configs/${id}/`, {
      method: 'DELETE',
    }),

  testConnection: (id: number) =>
    request<ApiResponse<{ success: boolean; message: string }>>(`/core/redis-configs/${id}/test/`, {
      method: 'POST',
    }),
};

// 系统配置API
export const systemApi = {
  getConfigs: (category?: string) => {
    const url = category ? `/core/system-configs/?category=${category}` : '/core/system-configs/';
    return request<ApiResponse<SystemConfig[]>>(url);
  },

  updateConfig: (id: number, value: string) =>
    request<ApiResponse<SystemConfig>>(`/core/system-configs/${id}/`, {
      method: 'PUT',
      body: JSON.stringify({ value }),
    }),

  getSystemInfo: () => request<ApiResponse<{
    version: string;
    django_version: string;
    python_version: string;
    database_type: string;
    redis_connected: boolean;
  }>>('/core/stats/'),

  getHealthStatus: () => request<ApiResponse<{
    status: string;
    database: boolean;
    redis: boolean;
    celery: boolean;
  }>>('/core/health/'),

  getAuditLogs: (params?: { page?: number; page_size?: number }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    return request<ApiResponse<PaginatedResponse<any>>>(`/core/audit-logs/?${queryParams.toString()}`);
  },
};

// 仪表盘API
export const dashboardApi = {
  getStats: () => request<ApiResponse<any>>('/core/dashboard/'),

  getRecentActivities: () => request<ApiResponse<any>>('/core/dashboard/recent_activities/'),

  getMyTasks: () => request<ApiResponse<any>>('/core/dashboard/my_tasks/'),

  getRecentBugs: () => request<ApiResponse<any>>('/core/dashboard/recent_bugs/'),
};

// 通知API
export const notificationApi = {
  getNotifications: (params?: { page?: number; page_size?: number; unread_only?: boolean }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.unread_only) queryParams.append('unread_only', 'true');
    return request<ApiResponse<PaginatedResponse<Notification>>>(`/core/notifications/?${queryParams.toString()}`);
  },

  getUnreadCount: () =>
    request<ApiResponse<{ count: number }>>('/core/notifications/unread_count/'),

  markAsRead: (id: number) =>
    request<ApiResponse<void>>(`/core/notifications/${id}/mark_read/`, {
      method: 'POST',
    }),

  markAllAsRead: () =>
    request<ApiResponse<void>>('/core/notifications/mark_all_read/', {
      method: 'POST',
    }),

  deleteNotification: (id: number) =>
    request<ApiResponse<void>>(`/core/notifications/${id}/`, {
      method: 'DELETE',
    }),
};

export default {
  auth: authApi,
  user: userApi,
  role: roleApi,
  permission: permissionApi,
  project: projectApi,
  testcase: testcaseApi,
  bug: bugApi,
  llm: llmApi,
  database: databaseApi,
  redis: redisApi,
  system: systemApi,
  feishu: feishuApi,
  dashboard: dashboardApi,
  apitest: apiTestApi,
  perftest: perfTestApi,
  notification: notificationApi,
};
