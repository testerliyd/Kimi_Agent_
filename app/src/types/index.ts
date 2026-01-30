// 用户相关类型
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
  last_login: string;
  roles: Role[];
}

export interface Role {
  id: number;
  name: string;
  code: string;
  description: string;
  permissions: Permission[];
  created_at: string;
  updated_at: string;
}

export interface Permission {
  id: number;
  name: string;
  code: string;
  description: string;
  module: string;
}

// 认证相关类型
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

// API响应类型
export interface ApiResponse<T = unknown> {
  code: number;
  message: string;
  data: T;
}

export interface PaginatedResponse<T = unknown> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// 大模型配置类型
export interface LLMConfig {
  id: number;
  name: string;
  provider: string;
  api_key: string;
  api_base: string;
  model_name: string;
  temperature: number;
  max_tokens: number;
  timeout: number;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export type LLMProvider = 'openai' | 'azure' | 'anthropic' | 'baidu' | 'alibaba' | 'zhipu' | 'moonshot' | 'custom';

// 数据库配置类型
export interface DatabaseConfig {
  id: number;
  name: string;
  db_type: 'mysql' | 'postgresql' | 'sqlite';
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

// Redis配置类型
export interface RedisConfig {
  id: number;
  name: string;
  host: string;
  port: number;
  password: string;
  db: number;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

// 系统配置类型
export interface SystemConfig {
  id: number;
  key: string;
  value: string;
  description: string;
  category: string;
  is_editable: boolean;
  created_at: string;
  updated_at: string;
}

// 项目类型
export interface Project {
  id: number;
  name: string;
  code: string;
  description: string;
  status: 'active' | 'archived' | 'deleted';
  owner: User;
  members: User[];
  created_at: string;
  updated_at: string;
}

// 测试用例类型
export interface TestCase {
  id: number;
  title: string;
  description: string;
  precondition: string;
  steps: TestStep[];
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'draft' | 'ready' | 'disabled';
  project: Project;
  creator: User;
  created_at: string;
  updated_at: string;
}

export interface TestStep {
  step_number: number;
  action: string;
  expected_result: string;
}

// Bug类型
export interface Bug {
  id: number;
  title: string;
  description: string;
  severity: 'minor' | 'major' | 'critical' | 'blocker';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'new' | 'confirmed' | 'in_progress' | 'fixed' | 'rejected' | 'closed';
  reporter: User;
  assignee: User | null;
  project: Project;
  test_case: TestCase | null;
  created_at: string;
  updated_at: string;
}

// 飞书配置类型
export interface FeishuConfig {
  id: number;
  name: string;
  webhook_url: string;
  secret: string;
  notify_on_bug: boolean;
  notify_on_report: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 仪表盘数据类型
export interface DashboardStats {
  total_projects: number;
  total_test_cases: number;
  total_bugs: number;
  pending_bugs: number;
  recent_bugs: Bug[];
  recent_activities: Activity[];
}

export interface Activity {
  id: number;
  user: User;
  action: string;
  target_type: string;
  target_name: string;
  created_at: string;
}

// 测试套件类型
export interface TestSuite {
  id: number;
  name: string;
  description: string;
  project: Project;
  test_cases: TestCase[];
  case_count: number;
  creator: User;
  created_at: string;
  updated_at: string;
}

// 测试计划类型
export interface TestPlan {
  id: number;
  name: string;
  description: string;
  project: Project;
  version: any;
  manager: User;
  status: 'pending' | 'running' | 'completed' | 'cancelled';
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
  blocked_cases: number;
  planned_start_date: string;
  planned_end_date: string;
  actual_start_date: string;
  actual_end_date: string;
  created_at: string;
  updated_at: string;
}

// API定义类型
export interface ApiDefinition {
  id: number;
  name: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  description: string;
  project: Project;
  headers: Record<string, string>;
  request_body: any;
  response_schema: any;
  created_at: string;
  updated_at: string;
}

// API测试用例类型
export interface ApiTestCase {
  id: number;
  name: string;
  api_definition: ApiDefinition;
  method: string;
  url: string;
  headers: Record<string, string>;
  body: any;
  expected_response: any;
  status: 'pending' | 'passed' | 'failed';
  last_executed_at: string;
  created_at: string;
  updated_at: string;
}

// API测试任务类型
export interface ApiTestJob {
  id: number;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
  created_at: string;
  updated_at: string;
}

// 性能测试场景类型
export interface PerfTestScenario {
  id: number;
  name: string;
  description: string;
  project: Project;
  target_url: string;
  concurrent_users: number;
  duration: number;
  ramp_up: number;
  think_time: number;
  status: 'draft' | 'ready' | 'running' | 'completed';
  created_at: string;
  updated_at: string;
}

// 性能测试任务类型
export interface PerfTestJob {
  id: number;
  name: string;
  scenario: PerfTestScenario;
  status: 'pending' | 'running' | 'completed' | 'failed';
  tps: number;
  avg_response_time: number;
  error_rate: number;
  concurrent_users: number;
  duration: number;
  created_at: string;
  updated_at: string;
}

// 通知类型
export interface Notification {
  id: number;
  title: string;
  content: string;
  type: 'bug' | 'testcase' | 'report' | 'system' | 'perftest';
  is_read: boolean;
  sender: User;
  receiver: User;
  related_object_type: string;
  related_object_id: number;
  created_at: string;
}
