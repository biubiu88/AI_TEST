-- 创建数据库
CREATE DATABASE IF NOT EXISTS testcase_generator
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE testcase_generator;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL COMMENT '用户名',
  email VARCHAR(120) UNIQUE NOT NULL COMMENT '邮箱',
  password_hash VARCHAR(256) NOT NULL COMMENT '密码哈希',
  nickname VARCHAR(80) COMMENT '昵称',
  avatar VARCHAR(256) COMMENT '头像',
  status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/inactive/banned',
  last_login DATETIME COMMENT '最后登录时间',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_username (username),
  INDEX idx_email (email),
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 角色表
CREATE TABLE IF NOT EXISTS roles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL COMMENT '角色名称',
  code VARCHAR(50) UNIQUE NOT NULL COMMENT '角色编码',
  description VARCHAR(200) COMMENT '角色描述',
  status INT DEFAULT 1 COMMENT '状态: 1启用 0禁用',
  sort INT DEFAULT 0 COMMENT '排序',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_code (code),
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- 权限表
CREATE TABLE IF NOT EXISTS permissions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL COMMENT '权限名称',
  code VARCHAR(100) UNIQUE NOT NULL COMMENT '权限编码',
  type VARCHAR(20) DEFAULT 'button' COMMENT '权限类型: menu/button/api',
  description VARCHAR(200) COMMENT '权限描述',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_code (code),
  INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限表';

-- 菜单表
CREATE TABLE IF NOT EXISTS menus (
  id INT AUTO_INCREMENT PRIMARY KEY,
  parent_id INT DEFAULT 0 COMMENT '父菜单ID',
  name VARCHAR(50) NOT NULL COMMENT '菜单名称',
  path VARCHAR(200) COMMENT '路由路径',
  component VARCHAR(200) COMMENT '组件路径',
  redirect VARCHAR(200) COMMENT '重定向路径',
  icon VARCHAR(50) COMMENT '菜单图标',
  title VARCHAR(50) COMMENT '菜单标题',
  hidden BOOLEAN DEFAULT FALSE COMMENT '是否隐藏',
  always_show BOOLEAN DEFAULT FALSE COMMENT '是否总是显示',
  keep_alive BOOLEAN DEFAULT FALSE COMMENT '是否缓存',
  sort INT DEFAULT 0 COMMENT '排序',
  type VARCHAR(20) DEFAULT 'menu' COMMENT '类型: directory/menu/button',
  permission VARCHAR(100) COMMENT '权限标识',
  status INT DEFAULT 1 COMMENT '状态: 1启用 0禁用',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_parent_id (parent_id),
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜单表';

-- 用户角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
  user_id INT NOT NULL,
  role_id INT NOT NULL,
  PRIMARY KEY (user_id, role_id),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表';

-- 角色权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
  role_id INT NOT NULL,
  permission_id INT NOT NULL,
  PRIMARY KEY (role_id, permission_id),
  FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色权限关联表';

-- 角色菜单关联表
CREATE TABLE IF NOT EXISTS role_menus (
  role_id INT NOT NULL,
  menu_id INT NOT NULL,
  PRIMARY KEY (role_id, menu_id),
  FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
  FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色菜单关联表';

-- 需求表
CREATE TABLE IF NOT EXISTS requirements (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL COMMENT '需求标题',
  content TEXT NOT NULL COMMENT '需求内容',
  module VARCHAR(100) COMMENT '所属模块',
  priority VARCHAR(20) DEFAULT 'medium' COMMENT '优先级: high/medium/low',
  status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/in_progress/completed',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_module (module),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='需求文档表';

-- 测试用例表
CREATE TABLE IF NOT EXISTS testcases (
  id INT AUTO_INCREMENT PRIMARY KEY,
  requirement_id INT COMMENT '关联需求ID，可为空',
  title VARCHAR(255) NOT NULL COMMENT '用例标题',
  precondition TEXT COMMENT '前置条件',
  steps TEXT NOT NULL COMMENT '测试步骤',
  expected_result TEXT NOT NULL COMMENT '预期结果',
  case_type VARCHAR(50) DEFAULT 'functional' COMMENT '用例类型: functional/boundary/exception/performance',
  priority VARCHAR(20) DEFAULT 'medium' COMMENT '优先级: high/medium/low',
  status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/passed/failed/blocked',
  is_ai_generated BOOLEAN DEFAULT FALSE COMMENT '是否AI生成',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE SET NULL,
  INDEX idx_requirement_id (requirement_id),
  INDEX idx_case_type (case_type),
  INDEX idx_status (status),
  INDEX idx_is_ai_generated (is_ai_generated)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试用例表';

-- 插入示例数据
INSERT INTO requirements (title, content, module, priority, status) VALUES
('用户登录功能', '1. 用户可以使用用户名和密码登录系统\n2. 支持记住密码功能\n3. 登录失败需要显示错误提示\n4. 连续3次登录失败需要输入验证码', '用户模块', 'high', 'in_progress'),
('商品搜索功能', '1. 用户可以通过关键词搜索商品\n2. 支持按价格、销量排序\n3. 支持按分类筛选\n4. 搜索结果分页显示，每页20条', '商品模块', 'high', 'pending'),
('购物车功能', '1. 用户可以将商品加入购物车\n2. 可以修改商品数量\n3. 可以删除购物车商品\n4. 显示购物车商品总价', '订单模块', 'medium', 'pending');

-- 提示词表
CREATE TABLE IF NOT EXISTS prompts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL COMMENT '提示词名称',
  content TEXT NOT NULL COMMENT '提示词内容',
  description VARCHAR(500) COMMENT '提示词描述',
  category VARCHAR(50) DEFAULT 'general' COMMENT '分类: general/functional/boundary/exception/performance',
  is_default BOOLEAN DEFAULT FALSE COMMENT '是否默认提示词',
  is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_category (category),
  INDEX idx_is_default (is_default),
  INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='提示词表';

-- 知识库表
CREATE TABLE IF NOT EXISTS knowledges (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL COMMENT '知识库名称',
  content TEXT NOT NULL COMMENT '知识库内容',
  description VARCHAR(500) COMMENT '知识库描述',
  category VARCHAR(50) DEFAULT 'general' COMMENT '分类: general/domain/api/ui/database',
  file_type VARCHAR(20) DEFAULT 'text' COMMENT '文件类型: text/markdown/json',
  is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_category (category),
  INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库表';

-- 大模型配置表
CREATE TABLE IF NOT EXISTS llm_configs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL COMMENT '配置名称',
  provider VARCHAR(50) NOT NULL COMMENT '供应商: openai/azure/anthropic/qwen/zhipu/moonshot/deepseek/ollama/custom',
  api_base VARCHAR(500) NOT NULL COMMENT 'API基础URL',
  api_key VARCHAR(500) NOT NULL COMMENT 'API密钥',
  model VARCHAR(100) COMMENT '模型名称',
  description VARCHAR(500) COMMENT '配置描述',
  is_default BOOLEAN DEFAULT FALSE COMMENT '是否默认配置',
  is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  extra_params TEXT COMMENT '额外参数JSON',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_provider (provider),
  INDEX idx_is_default (is_default),
  INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='大模型配置表';

-- 插入默认提示词
INSERT INTO prompts (name, content, description, category, is_default, is_active) VALUES
('默认测试用例提示词', '你是一位专业的软件测试工程师，擅长根据需求文档编写高质量的测试用例。请确保测试用例具有以下特点：\n1. 测试步骤清晰明确，可执行\n2. 预期结果具体，可验证\n3. 覆盖正常流程和异常场景\n4. 考虑边界条件和特殊情况', '通用的测试用例生成提示词', 'general', TRUE, TRUE),
('Web应用测试提示词', '你是一位专业的Web应用测试工程师。请根据需求编写测试用例，特别关注：\n1. 用户界面交互测试\n2. 表单验证和输入校验\n3. 浏览器兼容性\n4. 响应式设计测试\n5. 安全性测试（XSS、CSRF等）', '适用于Web应用的测试用例生成', 'functional', FALSE, TRUE),
('API接口测试提示词', '你是一位专业的API测试工程师。请根据需求编写API测试用例，特别关注：\n1. 请求参数验证\n2. 响应状态码检查\n3. 响应数据结构验证\n4. 错误处理和异常场景\n5. 权限和认证测试', '适用于RESTful API的测试用例生成', 'functional', FALSE, TRUE);

-- 插入示例知识库
INSERT INTO knowledges (name, content, description, category, file_type, is_active) VALUES
('登录功能测试规范', '登录功能测试要点：\n1. 正常登录：正确的用户名和密码\n2. 密码错误：测试错误密码提示\n3. 用户名不存在：测试不存在用户\n4. 空值验证：用户名或密码为空\n5. 特殊字符：包含特殊字符的输入\n6. SQL注入：防止SQL注入攻击\n7. 账户锁定：多次失败后锁定\n8. 验证码：验证码功能测试', '登录功能的测试规范和测试点', 'domain', 'text', TRUE),
('表单验证规范', '表单验证测试要点：\n1. 必填字段验证\n2. 字段长度限制\n3. 数据格式验证（邮箱、手机号等）\n4. 数字范围验证\n5. 日期格式验证\n6. 文件上传验证\n7. 密码强度验证\n8. 确认密码一致性', '通用表单验证的测试规范', 'general', 'text', TRUE);

-- 插入默认角色
INSERT INTO roles (name, code, description, status, sort) VALUES
('超级管理员', 'admin', '系统超级管理员，拥有所有权限', 1, 0),
('普通用户', 'user', '普通用户，可使用基本功能', 1, 1);

-- 插入默认权限
INSERT INTO permissions (name, code, type, description) VALUES
-- 需求管理权限
('需求查看', 'requirement:view', 'button', '查看需求列表和详情'),
('需求新增', 'requirement:create', 'button', '新增需求'),
('需求编辑', 'requirement:edit', 'button', '编辑需求'),
('需求删除', 'requirement:delete', 'button', '删除需求'),
-- 测试用例权限
('用例查看', 'testcase:view', 'button', '查看测试用例'),
('用例新增', 'testcase:create', 'button', '新增测试用例'),
('用例编辑', 'testcase:edit', 'button', '编辑测试用例'),
('用例删除', 'testcase:delete', 'button', '删除测试用例'),
('用例导入', 'testcase:import', 'button', '导入测试用例'),
('用例导出', 'testcase:export', 'button', '导出测试用例'),
-- AI生成权限
('AI生成', 'ai:generate', 'button', '使用AI生成测试用例'),
-- 提示词管理权限
('提示词查看', 'prompt:view', 'button', '查看提示词'),
('提示词新增', 'prompt:create', 'button', '新增提示词'),
('提示词编辑', 'prompt:edit', 'button', '编辑提示词'),
('提示词删除', 'prompt:delete', 'button', '删除提示词'),
-- 知识库管理权限
('知识库查看', 'knowledge:view', 'button', '查看知识库'),
('知识库新增', 'knowledge:create', 'button', '新增知识库'),
('知识库编辑', 'knowledge:edit', 'button', '编辑知识库'),
('知识库删除', 'knowledge:delete', 'button', '删除知识库'),
-- 大模型配置权限
('模型配置查看', 'llm:view', 'button', '查看大模型配置'),
('模型配置新增', 'llm:create', 'button', '新增大模型配置'),
('模型配置编辑', 'llm:edit', 'button', '编辑大模型配置'),
('模型配置删除', 'llm:delete', 'button', '删除大模型配置'),
-- 系统管理权限
('用户管理', 'system:user', 'menu', '用户管理权限'),
('角色管理', 'system:role', 'menu', '角色管理权限'),
('菜单管理', 'system:menu', 'menu', '菜单管理权限');

-- 插入默认菜单
INSERT INTO menus (parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status) VALUES
-- 一级菜单
(0, 'Root', '/', 'Layout', '/requirements', NULL, '首页', FALSE, FALSE, FALSE, 0, 'directory', NULL, 1),
-- 二级菜单（在Root下）
(1, 'Requirements', '/requirements', 'RequirementView', NULL, 'Document', '需求管理', FALSE, FALSE, TRUE, 1, 'menu', 'requirement:view', 1),
(1, 'TestCases', '/testcases', 'TestCaseView', NULL, 'List', '测试用例', FALSE, FALSE, TRUE, 2, 'menu', 'testcase:view', 1),
(1, 'Generate', '/generate', 'GenerateView', NULL, 'MagicStick', '生成用例', FALSE, FALSE, FALSE, 3, 'menu', 'ai:generate', 1),
(1, 'Prompts', '/prompts', 'PromptView', NULL, 'ChatDotRound', '提示词管理', FALSE, FALSE, TRUE, 4, 'menu', 'prompt:view', 1),
(1, 'Knowledges', '/knowledges', 'KnowledgeView', NULL, 'Collection', '知识库管理', FALSE, FALSE, TRUE, 5, 'menu', 'knowledge:view', 1),
(1, 'LLMConfigs', '/llm-configs', 'LLMConfigView', NULL, 'Setting', '大模型配置', FALSE, FALSE, TRUE, 6, 'menu', 'llm:view', 1);

-- 为管理员角色分配所有权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 1, id FROM permissions;

-- 为管理员角色分配所有菜单
INSERT INTO role_menus (role_id, menu_id)
SELECT 1, id FROM menus;

-- 为普通用户角色分配基本权限
INSERT INTO role_permissions (role_id, permission_id)
SELECT 2, id FROM permissions WHERE code IN (
    'requirement:view', 'requirement:create', 'requirement:edit',
    'testcase:view', 'testcase:create', 'testcase:edit', 'testcase:export',
    'ai:generate',
    'prompt:view',
    'knowledge:view'
);

-- 为普通用户角色分配基本菜单
INSERT INTO role_menus (role_id, menu_id)
SELECT 2, id FROM menus WHERE id <= 7;

-- 插入默认用户
-- admin用户（密码: admin123）
INSERT INTO users (username, email, password_hash, nickname, status) VALUES
('admin', 'admin@example.com', 'scrypt:32768:8:1$eryBIDwmPi2kYug3$1d0a23aa4853a070bbbf9d8bc90da015ce755a106979cb295a39e2695af508dc19c2c2a47ef81f41e8dccb6d6f3e43b9070b3de87bac6e7374f20755d4cb02e2', '管理员', 'active'),
('testuser', 'testuser@example.com', 'scrypt:32768:8:1$3vE8QFk9A0UOknBJ$e16543b6dc374e9341083a0aeb061e738c1c139b2d93a8996de97ec15ebfb5e826002db4d17d8e88626cceb35a0750ff5159116ee78957b7d6b18de8286cc5c0', '测试用户', 'active');

-- 分配用户角色
-- admin -> 超级管理员
INSERT INTO user_roles (user_id, role_id) VALUES (1, 1);
-- testuser -> 普通用户
INSERT INTO user_roles (user_id, role_id) VALUES (2, 2);


INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (10, 0, 'Home', '/dashboard', 'DashboardView', '', 'DataBoard', '首页', 0, 0, 1, 0, 'menu', 'dashboard:view', 1, '2026-01-24 05:58:03', '2026-01-24 06:54:51');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (11, 0, 'Testing', '/testing', 'Layout', '/testing/testcases', 'Tools', '测试核心', 0, 0, 0, 1, 'directory', '', 1, '2026-01-24 05:58:03', '2026-01-24 07:03:26');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (12, 11, 'TestCases', '/testing/testcases', 'TestCaseView', '', 'List', '用例管理', 0, 0, 1, 1, 'menu', 'testcase:view', 1, '2026-01-24 05:58:03', '2026-01-24 07:26:25');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (13, 11, 'Generate', '/testing/generate', 'GenerateView', '', 'MagicStick', '生成用例', 0, 0, 0, 2, 'menu', 'ai:generate', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (14, 11, 'Requirements', '/testing/requirements', 'RequirementView', '', 'Document', '需求管理', 0, 0, 1, 3, 'menu', 'requirement:view', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (15, 16, 'Prompts', '/knowledge/prompts', 'PromptView', '', 'ChatDotRound', '提示词管理', 0, 0, 1, 1, 'menu', 'prompt:view', 1, '2026-01-24 05:58:03', '2026-01-24 07:30:35');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (16, 0, 'Knowledge', '/knowledge', 'Layout', '/knowledge/knowledges', 'Collection', '知识资产', 0, 0, 0, 2, 'directory', '', 1, '2026-01-24 05:58:03', '2026-01-24 07:30:35');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (17, 16, 'Knowledges', '/knowledge/knowledges', 'KnowledgeView', '', 'Reading', '知识库管理', 0, 0, 1, 0, 'menu', 'knowledge:view', 1, '2026-01-24 05:58:03', '2026-01-24 07:30:35');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (19, 0, 'System', '/system', 'Layout', '/system/users', 'Setting', '系统配置', 0, 0, 0, 4, 'directory', '', 1, '2026-01-24 05:58:03', '2026-01-24 08:05:01');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (20, 19, 'Users', '/system/users', 'UserView', '', 'User', '用户管理', 0, 0, 1, 1, 'menu', 'system:user', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (21, 19, 'Roles', '/system/roles', 'RoleView', '', 'UserFilled', '角色管理', 0, 0, 1, 2, 'menu', 'system:role', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (22, 19, 'Menus', '/system/menus', 'MenuView', '', 'Menu', '菜单管理', 0, 0, 1, 3, 'menu', 'system:menu', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (23, 19, 'LLMConfigs', '/system/llm-configs', 'LLMConfigView', '', 'Connection', '大模型配置', 0, 0, 1, 4, 'menu', 'llm:view', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (24, 19, 'Logs', '/system/logs', 'LogView', '', 'DocumentCopy', '日志与审计', 0, 0, 0, 5, 'menu', 'system:log', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (25, 19, 'MCPConfigs', '/system/mcp-configs', 'MCPConfigView', '', 'Connection', 'MCP配置', 0, 0, 1, 6, 'menu', 'mcp:view', 1, '2026-01-24 07:41:49', '2026-01-24 07:41:49');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (26, 0, 'AIAssistant', '/ai-assistant', 'AIAssistantView', '', 'ChatLineRound', 'AI助手', 0, 0, 1, 3, 'menu', 'ai:assistant', 1, '2026-01-24 08:05:01', '2026-01-24 08:05:01');
INSERT INTO testcase_generator.menus (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES (28, 11, 'Reviews', '/testing/reviews', 'ReviewView', null, 'Checked', '用例评审', 0, 0, 1, 4, 'menu', 'review:view', 1, '2026-01-25 02:51:04', '2026-01-25 02:51:04');

