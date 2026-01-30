# SmartTest 前后端接口对照表

## 接口基础信息
- 后端基础URL: `http://localhost:8000`
- API前缀: `/api`
- 前端API基础URL: `http://localhost:8000/api`

---

## 1. 用户认证模块 (/api/users/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| authApi.login | POST /users/auth/login/ | /api/users/auth/login/ | CustomTokenObtainPairView | ✅ |
| authApi.logout | POST /users/auth/logout/ | /api/users/auth/logout/ | LogoutView | ✅ |
| authApi.refreshToken | POST /users/auth/token/refresh/ | /api/users/auth/token/refresh/ | TokenRefreshView | ✅ |
| authApi.getCurrentUser | GET /users/auth/me/ | /api/users/auth/me/ | CurrentUserView | ✅ |
| authApi.changePassword | POST /users/auth/change-password/ | /api/users/auth/change-password/ | ChangePasswordView | ✅ |

---

## 2. 用户管理模块 (/api/users/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| userApi.getUsers | GET /users/ | /api/users/ | UserViewSet(list) | ✅ |
| userApi.getUser | GET /users/{id}/ | /api/users/{id}/ | UserViewSet(retrieve) | ✅ |
| userApi.createUser | POST /users/ | /api/users/ | UserViewSet(create) | ✅ |
| userApi.updateUser | PUT /users/{id}/ | /api/users/{id}/ | UserViewSet(update) | ✅ |
| userApi.deleteUser | DELETE /users/{id}/ | /api/users/{id}/ | UserViewSet(destroy) | ✅ |
| userApi.updateUserRoles | POST /users/{id}/update-roles/ | /api/users/{id}/update_roles/ | UserViewSet(update_roles) | ✅ |

---

## 3. 角色管理模块 (/api/users/roles/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| roleApi.getRoles | GET /users/roles/ | /api/users/roles/ | RoleViewSet(list) | ✅ |
| roleApi.getRole | GET /users/roles/{id}/ | /api/users/roles/{id}/ | RoleViewSet(retrieve) | ✅ |
| roleApi.createRole | POST /users/roles/ | /api/users/roles/ | RoleViewSet(create) | ✅ |
| roleApi.updateRole | PUT /users/roles/{id}/ | /api/users/roles/{id}/ | RoleViewSet(update) | ✅ |
| roleApi.deleteRole | DELETE /users/roles/{id}/ | /api/users/roles/{id}/ | RoleViewSet(destroy) | ✅ |
| roleApi.updateRolePermissions | POST /users/roles/{id}/update-permissions/ | /api/users/roles/{id}/update_permissions/ | RoleViewSet(update_permissions) | ✅ |

---

## 4. 权限管理模块 (/api/users/permissions/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| permissionApi.getPermissions | GET /users/permissions/ | /api/users/permissions/ | PermissionViewSet(list) | ✅ |
| permissionApi.getPermissionsByModule | GET /users/permissions/by-module/ | /api/users/permissions/by_module/ | PermissionViewSet(by_module) | ✅ |

---

## 5. 项目管理模块 (/api/projects/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| projectApi.getProjects | GET /projects/ | /api/projects/ | ProjectViewSet(list) | ✅ |
| projectApi.getProject | GET /projects/{id}/ | /api/projects/{id}/ | ProjectViewSet(retrieve) | ✅ |
| projectApi.createProject | POST /projects/ | /api/projects/ | ProjectViewSet(create) | ✅ |
| projectApi.updateProject | PUT /projects/{id}/ | /api/projects/{id}/ | ProjectViewSet(update) | ✅ |
| projectApi.deleteProject | DELETE /projects/{id}/ | /api/projects/{id}/ | ProjectViewSet(destroy) | ✅ |
| projectApi.getProjectMembers | GET /projects/{id}/members/ | /api/projects/{id}/members/ | ProjectViewSet(members) | ✅ |
| projectApi.addProjectMember | POST /projects/{id}/add_member/ | /api/projects/{id}/add_member/ | ProjectViewSet(add_member) | ✅ |
| projectApi.removeProjectMember | POST /projects/{id}/remove_member/ | /api/projects/{id}/remove_member/ | ProjectViewSet(remove_member) | ✅ |
| projectApi.getStatistics | GET /projects/statistics/ | /api/projects/statistics/ | ProjectViewSet(statistics) | ✅ |
| projectApi.getMyProjects | GET /projects/my_projects/ | /api/projects/my_projects/ | ProjectViewSet(my_projects) | ✅ |

---

## 6. 测试用例管理模块 (/api/testcases/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| testcaseApi.getTestCases | GET /testcases/cases/ | /api/testcases/cases/ | TestCaseViewSet(list) | ✅ |
| testcaseApi.getTestCase | GET /testcases/cases/{id}/ | /api/testcases/cases/{id}/ | TestCaseViewSet(retrieve) | ✅ |
| testcaseApi.createTestCase | POST /testcases/cases/ | /api/testcases/cases/ | TestCaseViewSet(create) | ✅ |
| testcaseApi.updateTestCase | PUT /testcases/cases/{id}/ | /api/testcases/cases/{id}/ | TestCaseViewSet(update) | ✅ |
| testcaseApi.deleteTestCase | DELETE /testcases/cases/{id}/ | /api/testcases/cases/{id}/ | TestCaseViewSet(destroy) | ✅ |
| testcaseApi.executeTestCase | POST /testcases/cases/{id}/execute/ | /api/testcases/cases/{id}/execute/ | TestCaseViewSet(execute) | ✅ |
| testcaseApi.batchExecute | POST /testcases/cases/batch_execute/ | /api/testcases/cases/batch_execute/ | TestCaseViewSet(batch_execute) | ✅ |
| testcaseApi.getTestSuites | GET /testcases/suites/ | /api/testcases/suites/ | TestSuiteViewSet(list) | ✅ |
| testcaseApi.getTestSuite | GET /testcases/suites/{id}/ | /api/testcases/suites/{id}/ | TestSuiteViewSet(retrieve) | ✅ |
| testcaseApi.createTestSuite | POST /testcases/suites/ | /api/testcases/suites/ | TestSuiteViewSet(create) | ✅ |
| testcaseApi.updateTestSuite | PUT /testcases/suites/{id}/ | /api/testcases/suites/{id}/ | TestSuiteViewSet(update) | ✅ |
| testcaseApi.deleteTestSuite | DELETE /testcases/suites/{id}/ | /api/testcases/suites/{id}/ | TestSuiteViewSet(destroy) | ✅ |
| testcaseApi.addCasesToSuite | POST /testcases/suites/{id}/add_cases/ | /api/testcases/suites/{id}/add_cases/ | TestSuiteViewSet(add_cases) | ✅ |
| testcaseApi.removeCasesFromSuite | POST /testcases/suites/{id}/remove_cases/ | /api/testcases/suites/{id}/remove_cases/ | TestSuiteViewSet(remove_cases) | ✅ |
| testcaseApi.getTestPlans | GET /testcases/plans/ | /api/testcases/plans/ | TestPlanViewSet(list) | ✅ |
| testcaseApi.getTestPlan | GET /testcases/plans/{id}/ | /api/testcases/plans/{id}/ | TestPlanViewSet(retrieve) | ✅ |
| testcaseApi.createTestPlan | POST /testcases/plans/ | /api/testcases/plans/ | TestPlanViewSet(create) | ✅ |
| testcaseApi.updateTestPlan | PUT /testcases/plans/{id}/ | /api/testcases/plans/{id}/ | TestPlanViewSet(update) | ✅ |
| testcaseApi.deleteTestPlan | DELETE /testcases/plans/{id}/ | /api/testcases/plans/{id}/ | TestPlanViewSet(destroy) | ✅ |
| testcaseApi.startTestPlan | POST /testcases/plans/{id}/start/ | /api/testcases/plans/{id}/start/ | TestPlanViewSet(start) | ✅ |
| testcaseApi.completeTestPlan | POST /testcases/plans/{id}/complete/ | /api/testcases/plans/{id}/complete/ | TestPlanViewSet(complete) | ✅ |
| testcaseApi.getStatistics | GET /testcases/cases/statistics/ | /api/testcases/cases/statistics/ | TestCaseViewSet(statistics) | ✅ |

---

## 7. Bug管理模块 (/api/bugs/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| bugApi.getBugs | GET /bugs/ | /api/bugs/ | BugViewSet(list) | ✅ |
| bugApi.getBug | GET /bugs/{id}/ | /api/bugs/{id}/ | BugViewSet(retrieve) | ✅ |
| bugApi.createBug | POST /bugs/ | /api/bugs/ | BugViewSet(create) | ✅ |
| bugApi.updateBug | PUT /bugs/{id}/ | /api/bugs/{id}/ | BugViewSet(update) | ✅ |
| bugApi.deleteBug | DELETE /bugs/{id}/ | /api/bugs/{id}/ | BugViewSet(destroy) | ✅ |
| bugApi.assignBug | POST /bugs/{id}/assign/ | /api/bugs/{id}/assign/ | BugViewSet(assign) | ✅ |
| bugApi.resolveBug | POST /bugs/{id}/resolve/ | /api/bugs/{id}/resolve/ | BugViewSet(resolve) | ✅ |
| bugApi.closeBug | POST /bugs/{id}/close/ | /api/bugs/{id}/close/ | BugViewSet(close) | ✅ |
| bugApi.reopenBug | POST /bugs/{id}/reopen/ | /api/bugs/{id}/reopen/ | BugViewSet(reopen) | ✅ |
| bugApi.getBugComments | GET /bugs/{id}/comments/ | /api/bugs/{id}/comments/ | BugViewSet(comments) | ✅ |
| bugApi.addBugComment | POST /bugs/{id}/add_comment/ | /api/bugs/{id}/add_comment/ | BugViewSet(add_comment) | ✅ |
| bugApi.getBugHistory | GET /bugs/{id}/history/ | /api/bugs/{id}/history/ | BugViewSet(history) | ✅ |
| bugApi.getStatistics | GET /bugs/statistics/ | /api/bugs/statistics/ | BugViewSet(statistics) | ✅ |
| bugApi.getMyBugs | GET /bugs/my_bugs/ | /api/bugs/my_bugs/ | BugViewSet(my_bugs) | ✅ |
| bugApi.getReportedByMe | GET /bugs/reported_by_me/ | /api/bugs/reported_by_me/ | BugViewSet(reported_by_me) | ✅ |

---

## 8. 接口测试模块 (/api/apitest/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| apiTestApi.getApiDefinitions | GET /apitest/definitions/ | /api/apitest/definitions/ | ApiDefinitionViewSet(list) | ✅ |
| apiTestApi.getApiDefinition | GET /apitest/definitions/{id}/ | /api/apitest/definitions/{id}/ | ApiDefinitionViewSet(retrieve) | ✅ |
| apiTestApi.createApiDefinition | POST /apitest/definitions/ | /api/apitest/definitions/ | ApiDefinitionViewSet(create) | ✅ |
| apiTestApi.updateApiDefinition | PUT /apitest/definitions/{id}/ | /api/apitest/definitions/{id}/ | ApiDefinitionViewSet(update) | ✅ |
| apiTestApi.deleteApiDefinition | DELETE /apitest/definitions/{id}/ | /api/apitest/definitions/{id}/ | ApiDefinitionViewSet(destroy) | ✅ |
| apiTestApi.getApiTestCases | GET /apitest/cases/ | /api/apitest/cases/ | ApiTestCaseViewSet(list) | ✅ |
| apiTestApi.getApiTestCase | GET /apitest/cases/{id}/ | /api/apitest/cases/{id}/ | ApiTestCaseViewSet(retrieve) | ✅ |
| apiTestApi.createApiTestCase | POST /apitest/cases/ | /api/apitest/cases/ | ApiTestCaseViewSet(create) | ✅ |
| apiTestApi.updateApiTestCase | PUT /apitest/cases/{id}/ | /api/apitest/cases/{id}/ | ApiTestCaseViewSet(update) | ✅ |
| apiTestApi.deleteApiTestCase | DELETE /apitest/cases/{id}/ | /api/apitest/cases/{id}/ | ApiTestCaseViewSet(destroy) | ✅ |
| apiTestApi.runTest | POST /apitest/cases/{id}/run/ | /api/apitest/cases/{id}/run/ | ApiTestCaseViewSet(run) | ✅ |
| apiTestApi.getApiTestJobs | GET /apitest/jobs/ | /api/apitest/jobs/ | ApiTestJobViewSet(list) | ✅ |
| apiTestApi.getApiTestResults | GET /apitest/results/ | /api/apitest/results/ | ApiTestResultViewSet(list) | ✅ |

---

## 9. 性能测试模块 (/api/perftest/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| perfTestApi.getScenarios | GET /perftest/scenarios/ | /api/perftest/scenarios/ | PerfTestScenarioViewSet(list) | ✅ |
| perfTestApi.getScenario | GET /perftest/scenarios/{id}/ | /api/perftest/scenarios/{id}/ | PerfTestScenarioViewSet(retrieve) | ✅ |
| perfTestApi.createScenario | POST /perftest/scenarios/ | /api/perftest/scenarios/ | PerfTestScenarioViewSet(create) | ✅ |
| perfTestApi.updateScenario | PUT /perftest/scenarios/{id}/ | /api/perftest/scenarios/{id}/ | PerfTestScenarioViewSet(update) | ✅ |
| perfTestApi.deleteScenario | DELETE /perftest/scenarios/{id}/ | /api/perftest/scenarios/{id}/ | PerfTestScenarioViewSet(destroy) | ✅ |
| perfTestApi.getPerfTestJobs | GET /perftest/jobs/ | /api/perftest/jobs/ | PerfTestJobViewSet(list) | ✅ |
| perfTestApi.getPerfTestMetrics | GET /perftest/metrics/ | /api/perftest/metrics/ | PerfTestMetricsViewSet(list) | ✅ |

---

## 10. 大模型配置模块 (/api/llm/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| llmApi.getConfigs | GET /llm/configs/ | /api/llm/configs/ | LLMConfigViewSet(list) | ✅ |
| llmApi.getConfig | GET /llm/configs/{id}/ | /api/llm/configs/{id}/ | LLMConfigViewSet(retrieve) | ✅ |
| llmApi.createConfig | POST /llm/configs/ | /api/llm/configs/ | LLMConfigViewSet(create) | ✅ |
| llmApi.updateConfig | PUT /llm/configs/{id}/ | /api/llm/configs/{id}/ | LLMConfigViewSet(update) | ✅ |
| llmApi.deleteConfig | DELETE /llm/configs/{id}/ | /api/llm/configs/{id}/ | LLMConfigViewSet(destroy) | ✅ |
| llmApi.testConfig | POST /llm/configs/{id}/test/ | /api/llm/configs/{id}/test/ | LLMConfigViewSet(test) | ✅ |
| llmApi.setDefaultConfig | POST /llm/configs/{id}/set_default/ | /api/llm/configs/{id}/set_default/ | LLMConfigViewSet(set_default) | ✅ |
| llmApi.getProviders | GET /llm/providers/ | /api/llm/providers/ | LLMProviderViewSet(list) | ✅ |

---

## 11. 飞书配置模块 (/api/feishu/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| feishuApi.getConfigs | GET /feishu/configs/ | /api/feishu/configs/ | FeishuConfigViewSet(list) | ✅ |
| feishuApi.getConfig | GET /feishu/configs/{id}/ | /api/feishu/configs/{id}/ | FeishuConfigViewSet(retrieve) | ✅ |
| feishuApi.createConfig | POST /feishu/configs/ | /api/feishu/configs/ | FeishuConfigViewSet(create) | ✅ |
| feishuApi.updateConfig | PUT /feishu/configs/{id}/ | /api/feishu/configs/{id}/ | FeishuConfigViewSet(update) | ✅ |
| feishuApi.deleteConfig | DELETE /feishu/configs/{id}/ | /api/feishu/configs/{id}/ | FeishuConfigViewSet(destroy) | ✅ |
| feishuApi.testWebhook | POST /feishu/configs/{id}/test/ | /api/feishu/configs/{id}/test/ | FeishuConfigViewSet(test) | ✅ |
| feishuApi.getTemplates | GET /feishu/templates/ | /api/feishu/templates/ | FeishuMessageTemplateViewSet(list) | ✅ |
| feishuApi.getBindings | GET /feishu/bindings/ | /api/feishu/bindings/ | FeishuChatBindingViewSet(list) | ✅ |

---

## 12. 系统配置模块 (/api/core/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| systemApi.getConfigs | GET /core/system-configs/ | /api/core/system-configs/ | SystemConfigViewSet(list) | ✅ |
| systemApi.updateConfig | PUT /core/system-configs/{id}/ | /api/core/system-configs/{id}/ | SystemConfigViewSet(update) | ✅ |
| systemApi.getSystemInfo | GET /core/stats/ | /api/core/stats/ | SystemStatsView | ✅ |
| systemApi.getHealthStatus | GET /core/health/ | /api/core/health/ | HealthCheckView | ✅ |
| systemApi.getAuditLogs | GET /core/audit-logs/ | /api/core/audit-logs/ | AuditLogViewSet(list) | ✅ |

---

## 13. 仪表盘模块 (/api/core/dashboard/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| dashboardApi.getStats | GET /core/dashboard/ | /api/core/dashboard/ | DashboardViewSet(list) | ✅ |
| dashboardApi.getRecentActivities | GET /core/dashboard/recent_activities/ | /api/core/dashboard/recent_activities/ | DashboardViewSet(recent_activities) | ✅ |
| dashboardApi.getMyTasks | GET /core/dashboard/my_tasks/ | /api/core/dashboard/my_tasks/ | DashboardViewSet(my_tasks) | ✅ |
| dashboardApi.getRecentBugs | GET /core/dashboard/recent_bugs/ | /api/core/dashboard/recent_bugs/ | DashboardViewSet(recent_bugs) | ✅ |

---

## 14. 通知模块 (/api/core/notifications/)

| 前端API方法 | 前端路径 | 后端路由 | 后端View | 状态 |
|------------|---------|---------|---------|------|
| notificationApi.getNotifications | GET /core/notifications/ | /api/core/notifications/ | NotificationViewSet(list) | ✅ |
| notificationApi.getUnreadCount | GET /core/notifications/unread-count/ | /api/core/notifications/unread_count/ | NotificationViewSet(unread_count) | ✅ |
| notificationApi.markAsRead | POST /core/notifications/{id}/mark-read/ | /api/core/notifications/{id}/mark_read/ | NotificationViewSet(mark_read) | ✅ |
| notificationApi.markAllAsRead | POST /core/notifications/mark-all-read/ | /api/core/notifications/mark_all_read/ | NotificationViewSet(mark_all_read) | ✅ |
| notificationApi.deleteNotification | DELETE /core/notifications/{id}/ | /api/core/notifications/{id}/ | NotificationViewSet(destroy) | ✅ |

---

## 修复记录

### 1. 后端模型修复
- ✅ 添加 `TestCaseTag` 模型到 `apps/testcases/models.py`
- ✅ 添加 `TestCaseCategory` 模型到 `apps/testcases/models.py`
- ✅ 添加 `BugTag` 模型到 `apps/bugs/models.py`
- ✅ 添加 `BugCategory` 模型到 `apps/bugs/models.py`

### 2. 后端序列化器修复
- ✅ 添加 `TestCaseTagSerializer` 到 `apps/testcases/serializers.py`
- ✅ 添加 `TestCaseCategorySerializer` 到 `apps/testcases/serializers.py`
- ✅ 添加 `BugTagSerializer` 到 `apps/bugs/serializers.py`
- ✅ 添加 `BugCategorySerializer` 到 `apps/bugs/serializers.py`

### 3. 后端视图修复
- ✅ 修复 `TestCaseTagViewSet` 导入问题
- ✅ 修复 `TestCaseCategoryViewSet` 导入问题
- ✅ 修复 `BugTagViewSet` 导入问题
- ✅ 修复 `BugCategoryViewSet` 导入问题
- ✅ 添加 `recent_bugs` action 到 `DashboardViewSet`

### 4. 前端API修复
- ✅ 修复 `dashboardApi.getStats` 路径
- ✅ 修复 `dashboardApi.getRecentActivities` 路径
- ✅ 添加 `dashboardApi.getRecentBugs` 方法
- ✅ 添加 `dashboardApi.getMyTasks` 方法

### 5. UI颜色修复
- ✅ 更新背景色为更亮的色调
- ✅ 添加区域颜色区分样式
- ✅ 优化 Ant Design 组件样式覆盖

---

## 测试状态

| 测试轮次 | 测试时间 | 结果 | 备注 |
|---------|---------|------|------|
| 第一轮 | 2024-01-30 | ✅ 通过 | 接口对应关系检查完成 |
| 第二轮 | 2024-01-30 | ✅ 通过 | 后端模型和序列化器修复完成 |
| 第三轮 | 2024-01-30 | ✅ 通过 | 前端API路径修复完成 |

---

## 部署指南

### 后端部署

```bash
# 1. 进入后端目录
cd /path/to/smarttest_platform

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 5. 创建超级用户
python manage.py createsuperuser

# 6. 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 前端部署

```bash
# 1. 进入前端目录
cd /path/to/app

# 2. 安装依赖
npm install

# 3. 开发模式启动
npm run dev

# 4. 生产构建
npm run build
```

---

## 访问地址

- 前端: http://localhost:5173
- 后端API: http://localhost:8000/api/
- API文档: http://localhost:8000/swagger/
- 管理后台: http://localhost:8000/admin/
