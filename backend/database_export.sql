-- 数据库导出文件
-- 数据库: testcase_generator
-- 导出时间: 2026-01-25 18:46:26
-- 说明: 包含所有表的建表语句和数据(除operation_logs表无数据)

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;


-- 表结构: ai_messages
DROP TABLE IF EXISTS `ai_messages`;
CREATE TABLE `ai_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL COMMENT '会话ID',
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色: user/assistant/system',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '消息内容',
  `message_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'text' COMMENT '消息类型: text/image/code/table',
  `metadata` text COLLATE utf8mb4_unicode_ci COMMENT '元数据JSON',
  `token_count` int DEFAULT '0' COMMENT 'Token数量',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_session_id` (`session_id`),
  KEY `idx_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI消息表';

-- 表结构: ai_sessions
DROP TABLE IF EXISTS `ai_sessions`;
CREATE TABLE `ai_sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '用户ID',
  `session_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT '新会话' COMMENT '会话名称',
  `session_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'chat' COMMENT '会话类型: chat/analysis/generation',
  `model_id` int DEFAULT NULL COMMENT '使用的模型ID',
  `prompt_id` int DEFAULT NULL COMMENT '使用的提示词ID',
  `knowledge_ids` text COLLATE utf8mb4_unicode_ci COMMENT '关联的知识库ID列表(JSON)',
  `mcp_config_id` int DEFAULT NULL COMMENT '使用的MCP配置ID',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'active' COMMENT '状态: active/archived/deleted',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI会话表';

-- 表结构: chat_messages
DROP TABLE IF EXISTS `chat_messages`;
CREATE TABLE `chat_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL COMMENT '所属会话ID',
  `role` varchar(20) NOT NULL COMMENT '角色: user/assistant/system',
  `content` text NOT NULL COMMENT '消息内容',
  `model` varchar(50) DEFAULT NULL COMMENT '使用的模型名称',
  `tokens_used` int DEFAULT NULL COMMENT '消耗的token数',
  `created_at` datetime DEFAULT NULL COMMENT '发送时间',
  PRIMARY KEY (`id`),
  KEY `session_id` (`session_id`),
  CONSTRAINT `chat_messages_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `chat_sessions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- 表结构: chat_sessions
DROP TABLE IF EXISTS `chat_sessions`;
CREATE TABLE `chat_sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL COMMENT '所属用户ID',
  `session_name` varchar(100) DEFAULT NULL COMMENT '会话名称',
  `is_pinned` tinyint(1) DEFAULT '0' COMMENT '是否置顶',
  `model_id` int DEFAULT NULL COMMENT '关联模型配置ID',
  `prompt_id` int DEFAULT NULL COMMENT '关联提示词ID',
  `mcp_config_id` int DEFAULT NULL COMMENT '关联MCP配置ID',
  `knowledge_ids` json DEFAULT NULL COMMENT '关联知识库ID列表',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `model_id` (`model_id`),
  KEY `prompt_id` (`prompt_id`),
  KEY `mcp_config_id` (`mcp_config_id`),
  CONSTRAINT `chat_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `chat_sessions_ibfk_2` FOREIGN KEY (`model_id`) REFERENCES `llm_configs` (`id`),
  CONSTRAINT `chat_sessions_ibfk_3` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`),
  CONSTRAINT `chat_sessions_ibfk_4` FOREIGN KEY (`mcp_config_id`) REFERENCES `mcp_configs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 表数据: chat_sessions
INSERT INTO `chat_sessions` (id, user_id, session_name, is_pinned, model_id, prompt_id, mcp_config_id, knowledge_ids, created_at, updated_at) VALUES
(1, 1, '新会话', 0, NULL, NULL, NULL, '[]', '2026-01-24 14:34:21', '2026-01-24 14:54:27'),
(2, 3, '持久化测试会话', 0, NULL, NULL, NULL, '[]', '2026-01-24 14:35:20', '2026-01-24 14:35:20'),
(3, 3, '持久化测试会话', 0, NULL, NULL, NULL, '[]', '2026-01-24 14:36:18', '2026-01-24 14:36:20');


-- 表结构: knowledges
DROP TABLE IF EXISTS `knowledges`;
CREATE TABLE `knowledges` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '知识库名称',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '知识库内容',
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '知识库描述',
  `category` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'general' COMMENT '分类: general/domain/api/ui/database',
  `file_type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'text' COMMENT '文件类型: text/markdown/json',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否启用',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_category` (`category`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库表';

-- 表数据: knowledges
INSERT INTO `knowledges` (id, name, content, description, category, file_type, is_active, created_at, updated_at) VALUES
(1, '登录功能测试规范', '登录功能测试要点：
1. 正常登录：正确的用户名和密码
2. 密码错误：测试错误密码提示
3. 用户名不存在：测试不存在用户
4. 空值验证：用户名或密码为空
5. 特殊字符：包含特殊字符的输入
6. SQL注入：防止SQL注入攻击
7. 账户锁定：多次失败后锁定
8. 验证码：验证码功能测试', '登录功能的测试规范和测试点', 'domain', 'text', 1, '2026-01-23 17:34:52', '2026-01-23 17:34:52'),
(2, '表单验证规范', '表单验证测试要点：
1. 必填字段验证
2. 字段长度限制
3. 数据格式验证（邮箱、手机号等）
4. 数字范围验证
5. 日期格式验证
6. 文件上传验证
7. 密码强度验证
8. 确认密码一致性', '通用表单验证的测试规范', 'general', 'text', 1, '2026-01-23 17:34:52', '2026-01-23 17:34:52');


-- 表结构: llm_configs
DROP TABLE IF EXISTS `llm_configs`;
CREATE TABLE `llm_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL COMMENT '配置名称',
  `provider` varchar(50) NOT NULL COMMENT '供应商: openai/azure/anthropic/qwen/zhipu/moonshot/deepseek/ollama/custom',
  `api_base` varchar(500) NOT NULL COMMENT 'API基础URL',
  `api_key` varchar(500) NOT NULL COMMENT 'API密钥',
  `model` varchar(100) DEFAULT NULL COMMENT '模型名称',
  `description` varchar(500) DEFAULT NULL COMMENT '配置描述',
  `is_default` tinyint(1) DEFAULT NULL COMMENT '是否默认配置',
  `is_active` tinyint(1) DEFAULT NULL COMMENT '是否启用',
  `extra_params` text COMMENT '额外参数JSON',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 表数据: llm_configs
INSERT INTO `llm_configs` (id, name, provider, api_base, api_key, model, description, is_default, is_active, extra_params, created_at, updated_at) VALUES
(1, 'deepseek', 'deepseek', 'https://api.deepseek.com/v1', 'sk-7aa59b4d1df64817aad55188a11391d2', 'deepseek-chat', '', 1, 1, NULL, '2026-01-23 16:30:00', '2026-01-23 16:30:05');


-- 表结构: mcp_configs
DROP TABLE IF EXISTS `mcp_configs`;
CREATE TABLE `mcp_configs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置名称',
  `server_url` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'MCP服务器地址',
  `server_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '服务器名称',
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '配置描述',
  `timeout` int DEFAULT '30' COMMENT '超时时间(秒)',
  `max_retries` int DEFAULT '3' COMMENT '最大重试次数',
  `status` int DEFAULT '1' COMMENT '状态: 1启用 0禁用',
  `is_default` tinyint(1) DEFAULT '0' COMMENT '是否默认配置',
  `extra_params` text COLLATE utf8mb4_unicode_ci COMMENT '额外参数JSON',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_status` (`status`),
  KEY `idx_is_default` (`is_default`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='MCP配置表';

-- 表结构: menus
DROP TABLE IF EXISTS `menus`;
CREATE TABLE `menus` (
  `id` int NOT NULL AUTO_INCREMENT,
  `parent_id` int DEFAULT '0' COMMENT '父菜单ID',
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '菜单名称',
  `path` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '路由路径',
  `component` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '组件路径',
  `redirect` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '重定向路径',
  `icon` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '菜单图标',
  `title` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '菜单标题',
  `hidden` tinyint(1) DEFAULT '0' COMMENT '是否隐藏',
  `always_show` tinyint(1) DEFAULT '0' COMMENT '是否总是显示',
  `keep_alive` tinyint(1) DEFAULT '0' COMMENT '是否缓存',
  `sort` int DEFAULT '0' COMMENT '排序',
  `type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'menu' COMMENT '类型: directory/menu/button',
  `permission` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '权限标识',
  `status` int DEFAULT '1' COMMENT '状态: 1启用 0禁用',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜单表';

-- 表数据: menus
INSERT INTO `menus` (id, parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status, created_at, updated_at) VALUES
(10, 0, 'Home', '/dashboard', 'DashboardView', '', 'DataBoard', '首页', 0, 0, 1, 0, 'menu', 'dashboard:view', 1, '2026-01-24 05:58:03', '2026-01-24 06:54:51'),
(11, 0, 'Testing', '/testing', 'Layout', '/testing/testcases', 'Tools', '测试核心', 0, 0, 0, 1, 'directory', '', 1, '2026-01-24 05:58:03', '2026-01-24 07:03:26'),
(12, 11, 'TestCases', '/testing/testcases', 'TestCaseView', '', 'List', '用例管理', 0, 0, 1, 1, 'menu', 'testcase:view', 1, '2026-01-24 05:58:03', '2026-01-24 07:26:25'),
(13, 11, 'Generate', '/testing/generate', 'GenerateView', '', 'MagicStick', '生成用例', 0, 0, 0, 2, 'menu', 'ai:generate', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03'),
(14, 11, 'Requirements', '/testing/requirements', 'RequirementView', '', 'Document', '需求管理', 0, 0, 1, 3, 'menu', 'requirement:view', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03'),
(15, 16, 'Prompts', '/knowledge/prompts', 'PromptView', '', 'ChatDotRound', '提示词管理', 0, 0, 1, 1, 'menu', 'prompt:view', 1, '2026-01-24 05:58:03', '2026-01-24 07:30:35'),
(16, 0, 'Knowledge', '/knowledge', 'Layout', '/knowledge/knowledges', 'Collection', '知识资产', 0, 0, 0, 2, 'directory', '', 1, '2026-01-24 05:58:03', '2026-01-24 07:30:35'),
(17, 16, 'Knowledges', '/knowledge/knowledges', 'KnowledgeView', '', 'Reading', '知识库管理', 0, 0, 1, 0, 'menu', 'knowledge:view', 1, '2026-01-24 05:58:03', '2026-01-24 07:30:35'),
(19, 0, 'System', '/system', 'Layout', '/system/users', 'Setting', '系统配置', 0, 0, 0, 4, 'directory', '', 1, '2026-01-24 05:58:03', '2026-01-24 08:05:01'),
(20, 19, 'Users', '/system/users', 'UserView', '', 'User', '用户管理', 0, 0, 1, 1, 'menu', 'system:user', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03'),
(21, 19, 'Roles', '/system/roles', 'RoleView', '', 'UserFilled', '角色管理', 0, 0, 1, 2, 'menu', 'system:role', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03'),
(22, 19, 'Menus', '/system/menus', 'MenuView', '', 'Menu', '菜单管理', 0, 0, 1, 3, 'menu', 'system:menu', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03'),
(23, 19, 'LLMConfigs', '/system/llm-configs', 'LLMConfigView', '', 'Connection', '大模型配置', 0, 0, 1, 4, 'menu', 'llm:view', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03'),
(24, 19, 'Logs', '/system/logs', 'LogView', '', 'DocumentCopy', '日志与审计', 0, 0, 0, 5, 'menu', 'system:log', 1, '2026-01-24 05:58:03', '2026-01-24 05:58:03'),
(25, 19, 'MCPConfigs', '/system/mcp-configs', 'MCPConfigView', '', 'Connection', 'MCP配置', 0, 0, 1, 6, 'menu', 'mcp:view', 1, '2026-01-24 07:41:49', '2026-01-24 07:41:49'),
(26, 0, 'AIAssistant', '/ai-assistant', 'AIAssistantView', '', 'ChatLineRound', 'AI助手', 0, 0, 1, 3, 'menu', 'ai:assistant', 1, '2026-01-24 08:05:01', '2026-01-24 08:05:01'),
(29,11,'DataFactory','/testing/datafactory','DataFactory','','List','造数工厂',0,0,1,5,'menu','testcase:view',1,'2026-02-03 13:30:08','2026-02-03 13:30:08'),
(28, 11, 'Reviews', '/testing/reviews', 'ReviewView', NULL, 'Checked', '用例评审', 0, 0, 1, 4, 'menu', 'review:view', 1, '2026-01-25 02:51:04', '2026-01-25 02:51:04');


-- 表结构: operation_logs
DROP TABLE IF EXISTS `operation_logs`;
CREATE TABLE `operation_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL COMMENT '用户ID',
  `username` varchar(80) DEFAULT NULL COMMENT '用户名',
  `action` varchar(50) NOT NULL COMMENT '操作类型: login/logout/create/update/delete/query/export',
  `module` varchar(50) NOT NULL COMMENT '模块名称',
  `description` varchar(500) DEFAULT NULL COMMENT '操作描述',
  `method` varchar(10) DEFAULT NULL COMMENT '请求方法: GET/POST/PUT/DELETE',
  `path` varchar(500) DEFAULT NULL COMMENT '请求路径',
  `params` text COMMENT '请求参数JSON',
  `status_code` int DEFAULT NULL COMMENT '响应状态码',
  `response_time` float DEFAULT NULL COMMENT '响应时间(毫秒)',
  `error_msg` text COMMENT '错误信息',
  `ip` varchar(50) DEFAULT NULL COMMENT 'IP地址',
  `user_agent` varchar(500) DEFAULT NULL COMMENT 'User-Agent',
  `browser` varchar(100) DEFAULT NULL COMMENT '浏览器',
  `browser_version` varchar(50) DEFAULT NULL COMMENT '浏览器版本',
  `os` varchar(100) DEFAULT NULL COMMENT '操作系统',
  `os_version` varchar(50) DEFAULT NULL COMMENT '系统版本',
  `device` varchar(50) DEFAULT NULL COMMENT '设备类型: desktop/mobile/tablet',
  `status` varchar(20) DEFAULT NULL COMMENT '操作状态: success/fail/error',
  `created_at` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_operation_logs_created_at` (`created_at`),
  CONSTRAINT `operation_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=867 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 表 operation_logs 的数据不导出

-- 表结构: permissions
DROP TABLE IF EXISTS `permissions`;
CREATE TABLE `permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '权限名称',
  `code` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '权限编码',
  `type` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'button' COMMENT '权限类型: menu/button/api',
  `description` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '权限描述',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `idx_code` (`code`),
  KEY `idx_type` (`type`)
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限表';

-- 表数据: permissions
INSERT INTO `permissions` (id, name, code, type, description, created_at) VALUES
(1, '需求查看', 'requirement:view', 'button', '查看需求列表和详情', '2026-01-23 17:34:52'),
(2, '需求新增', 'requirement:create', 'button', '新增需求', '2026-01-23 17:34:52'),
(3, '需求编辑', 'requirement:edit', 'button', '编辑需求', '2026-01-23 17:34:52'),
(4, '需求删除', 'requirement:delete', 'button', '删除需求', '2026-01-23 17:34:52'),
(5, '用例查看', 'testcase:view', 'button', '查看测试用例', '2026-01-23 17:34:52'),
(6, '用例新增', 'testcase:create', 'button', '新增测试用例', '2026-01-23 17:34:52'),
(7, '用例编辑', 'testcase:edit', 'button', '编辑测试用例', '2026-01-23 17:34:52'),
(8, '用例删除', 'testcase:delete', 'button', '删除测试用例', '2026-01-23 17:34:52'),
(9, '用例导入', 'testcase:import', 'button', '导入测试用例', '2026-01-23 17:34:52'),
(10, '用例导出', 'testcase:export', 'button', '导出测试用例', '2026-01-23 17:34:52'),
(11, 'AI生成', 'ai:generate', 'button', '使用AI生成测试用例', '2026-01-23 17:34:52'),
(12, '提示词查看', 'prompt:view', 'button', '查看提示词', '2026-01-23 17:34:52'),
(13, '提示词新增', 'prompt:create', 'button', '新增提示词', '2026-01-23 17:34:52'),
(14, '提示词编辑', 'prompt:edit', 'button', '编辑提示词', '2026-01-23 17:34:52'),
(15, '提示词删除', 'prompt:delete', 'button', '删除提示词', '2026-01-23 17:34:52'),
(16, '知识库查看', 'knowledge:view', 'button', '查看知识库', '2026-01-23 17:34:52'),
(17, '知识库新增', 'knowledge:create', 'button', '新增知识库', '2026-01-23 17:34:52'),
(18, '知识库编辑', 'knowledge:edit', 'button', '编辑知识库', '2026-01-23 17:34:52'),
(19, '知识库删除', 'knowledge:delete', 'button', '删除知识库', '2026-01-23 17:34:52'),
(20, '模型配置查看', 'llm:view', 'button', '查看大模型配置', '2026-01-23 17:34:52'),
(21, '模型配置新增', 'llm:create', 'button', '新增大模型配置', '2026-01-23 17:34:52'),
(22, '模型配置编辑', 'llm:edit', 'button', '编辑大模型配置', '2026-01-23 17:34:52'),
(23, '模型配置删除', 'llm:delete', 'button', '删除大模型配置', '2026-01-23 17:34:52'),
(24, '用户管理', 'system:user', 'menu', '用户管理权限', '2026-01-23 17:34:52'),
(25, '角色管理', 'system:role', 'menu', '角色管理权限', '2026-01-23 17:34:52'),
(26, '菜单管理', 'system:menu', 'menu', '菜单管理权限', '2026-01-23 17:34:52'),
(27, '概览仪表盘', 'dashboard:view', 'menu', '概览仪表盘权限', '2026-01-24 05:58:03'),
(28, '公共组件库', 'component:view', 'menu', '公共组件库权限', '2026-01-24 05:58:03'),
(29, '日志与审计', 'system:log', 'menu', '日志与审计权限', '2026-01-24 05:58:03'),
(30, 'MCP配置查看', 'mcp:view', 'button', '查看MCP配置', '2026-01-24 07:41:49'),
(31, 'MCP配置新增', 'mcp:create', 'button', '新增MCP配置', '2026-01-24 07:41:49'),
(32, 'MCP配置编辑', 'mcp:edit', 'button', '编辑MCP配置', '2026-01-24 07:41:49'),
(33, 'MCP配置删除', 'mcp:delete', 'button', '删除MCP配置', '2026-01-24 07:41:49'),
(34, 'AI助手使用', 'ai:assistant', 'menu', '使用AI助手功能', '2026-01-24 08:05:01'),
(35, 'AI会话管理', 'ai:session', 'button', '管理AI会话', '2026-01-24 08:05:01'),
(36, 'AI消息查看', 'ai:message:view', 'button', '查看AI消息', '2026-01-24 08:05:01'),
(48, '评审查看', 'review:view', 'button', '查看评审列表和详情', '2026-01-25 02:51:04'),
(49, '评审新增', 'review:create', 'button', '新增评审记录', '2026-01-25 02:51:04'),
(50, '评审编辑', 'review:edit', 'button', '编辑评审记录', '2026-01-25 02:51:04'),
(51, '评审删除', 'review:delete', 'button', '删除评审记录', '2026-01-25 02:51:04'),
(52, '评审提交', 'review:submit', 'button', '提交评审结果', '2026-01-25 02:51:04'),
(53, '评审评论', 'review:comment', 'button', '添加评审评论', '2026-01-25 02:51:04'),
(54, '评审模板查看', 'review:template:view', 'button', '查看评审模板', '2026-01-25 02:51:04'),
(55, '评审模板新增', 'review:template:create', 'button', '新增评审模板', '2026-01-25 02:51:04'),
(56, '评审模板编辑', 'review:template:edit', 'button', '编辑评审模板', '2026-01-25 02:51:04'),
(57, '评审模板删除', 'review:template:delete', 'button', '删除评审模板', '2026-01-25 02:51:04');


-- 表结构: prompts
DROP TABLE IF EXISTS `prompts`;
CREATE TABLE `prompts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '提示词名称',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '提示词内容',
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '提示词描述',
  `category` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'general' COMMENT '分类: general/functional/boundary/exception/performance',
  `is_default` tinyint(1) DEFAULT '0' COMMENT '是否默认提示词',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否启用',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_category` (`category`),
  KEY `idx_is_default` (`is_default`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='提示词表';

-- 表数据: prompts
INSERT INTO `prompts` (id, name, content, description, category, is_default, is_active, created_at, updated_at) VALUES
(1, '默认测试用例提示词', '你是一位专业的软件测试工程师，擅长根据需求文档编写高质量的测试用例。请确保测试用例具有以下特点：
1. 测试步骤清晰明确，可执行
2. 预期结果具体，可验证
3. 覆盖正常流程和异常场景
4. 考虑边界条件和特殊情况', '通用的测试用例生成提示词', 'general', 1, 1, '2026-01-23 17:34:52', '2026-01-23 17:34:52'),
(2, 'Web应用测试提示词', '你是一位专业的Web应用测试工程师。请根据需求编写测试用例，特别关注：
1. 用户界面交互测试
2. 表单验证和输入校验
3. 浏览器兼容性
4. 响应式设计测试
5. 安全性测试（XSS、CSRF等）', '适用于Web应用的测试用例生成', 'functional', 0, 1, '2026-01-23 17:34:52', '2026-01-23 17:34:52'),
(3, 'API接口测试提示词', '你是一位专业的API测试工程师。请根据需求编写API测试用例，特别关注：
1. 请求参数验证
2. 响应状态码检查
3. 响应数据结构验证
4. 错误处理和异常场景
5. 权限和认证测试', '适用于RESTful API的测试用例生成', 'functional', 0, 1, '2026-01-23 17:34:52', '2026-01-23 17:34:52'),
(4, '证券行业资深测试专家', '请作为证券行业资深测试专家，为以下模块设计详细的测试用例：

**模块名称**：[填写具体模块，如：股票交易、行情推送、风险控制等]
**核心功能**：[简要描述主要功能点]
**测试重点**：[特别关注的方面，如：合规性、实时性、数据准确性等]
**测试类型**：[功能测试/性能测试/安全测试/兼容性测试等]

请按以下格式生成测试用例：
1. 用例编号、标题、优先级
2. 前置条件
3. 测试步骤
4. 预期结果
5. 相关合规要求（如适用）', '证券行业资深测试专家', 'general', 0, 1, '2026-01-24 08:39:51', '2026-01-24 08:39:51');


-- 表结构: requirements
DROP TABLE IF EXISTS `requirements`;
CREATE TABLE `requirements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '需求标题',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '需求内容',
  `module` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '所属模块',
  `priority` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'medium' COMMENT '优先级: high/medium/low',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'pending' COMMENT '状态: pending/in_progress/completed',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_module` (`module`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='需求文档表';


-- 表结构: review_comments
DROP TABLE IF EXISTS `review_comments`;
CREATE TABLE `review_comments` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '评论ID',
  `review_id` int NOT NULL COMMENT '评审ID',
  `user_id` int NOT NULL COMMENT '评论人ID',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '评论内容',
  `is_reply` tinyint(1) DEFAULT '0' COMMENT '是否为回复',
  `parent_id` int DEFAULT NULL COMMENT '父评论ID（用于回复）',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_review_id` (`review_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_parent_id` (`parent_id`),
  CONSTRAINT `review_comments_ibfk_1` FOREIGN KEY (`review_id`) REFERENCES `testcase_reviews` (`id`) ON DELETE CASCADE,
  CONSTRAINT `review_comments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评审评论表';

-- 表结构: review_templates
DROP TABLE IF EXISTS `review_templates`;
CREATE TABLE `review_templates` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '模板ID',
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '模板名称',
  `description` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '模板描述',
  `category` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'general' COMMENT '分类: general/web/api/performance/security',
  `checklist` text COLLATE utf8mb4_unicode_ci COMMENT '评审检查点JSON',
  `scoring_criteria` text COLLATE utf8mb4_unicode_ci COMMENT '评分标准JSON',
  `is_default` tinyint(1) DEFAULT '0' COMMENT '是否默认模板',
  `is_active` tinyint(1) DEFAULT '1' COMMENT '是否启用',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_category` (`category`),
  KEY `idx_is_default` (`is_default`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评审模板表';

-- 表数据: review_templates
INSERT INTO `review_templates` (id, name, description, category, checklist, scoring_criteria, is_default, is_active, created_at, updated_at) VALUES
(1, '通用测试用例评审模板', '适用于各类测试用例的通用评审模板', 'general', '[
                {\"id\": 1, \"item\": \"用例标题是否清晰明确？\", \"required\": true},
                {\"id\": 2, \"item\": \"前置条件是否完整？\", \"required\": true},
                {\"id\": 3, \"item\": \"测试步骤是否清晰可执行？\", \"required\": true},
                {\"id\": 4, \"item\": \"预期结果是否明确可验证？\", \"required\": true},
                {\"id\": 5, \"item\": \"用例是否覆盖了需求的关键点？\", \"required\": true},
                {\"id\": 6, \"item\": \"用例优先级是否合理？\", \"required\": false},
                {\"id\": 7, \"item\": \"用例类型分类是否准确？\", \"required\": false}
             ]', '{
                \"clarity\": {\"name\": \"清晰度\", \"description\": \"用例描述是否清晰易懂\", \"max\": 5},
                \"completeness\": {\"name\": \"完整性\", \"description\": \"用例要素是否完整\", \"max\": 5},
                \"feasibility\": {\"name\": \"可执行性\", \"description\": \"用例是否可以被执行\", \"max\": 5},
                \"coverage\": {\"name\": \"覆盖度\", \"description\": \"用例覆盖范围是否充分\", \"max\": 5}
             }', 1, 1, '2026-01-25 02:54:53', '2026-01-25 02:54:53'),
(2, 'Web应用测试用例评审模板', '适用于Web应用的测试用例评审', 'web', '[
                {\"id\": 1, \"item\": \"用例标题是否清晰明确？\", \"required\": true},
                {\"id\": 2, \"item\": \"前置条件是否完整？\", \"required\": true},
                {\"id\": 3, \"item\": \"测试步骤是否清晰可执行？\", \"required\": true},
                {\"id\": 4, \"item\": \"预期结果是否明确可验证？\", \"required\": true},
                {\"id\": 5, \"item\": \"是否考虑了浏览器兼容性？\", \"required\": false},
                {\"id\": 6, \"item\": \"是否考虑了响应式设计？\", \"required\": false},
                {\"id\": 7, \"item\": \"是否考虑了安全性测试？\", \"required\": false},
                {\"id\": 8, \"item\": \"是否考虑了性能测试？\", \"required\": false}
             ]', '{
                \"clarity\": {\"name\": \"清晰度\", \"description\": \"用例描述是否清晰易懂\", \"max\": 5},
                \"completeness\": {\"name\": \"完整性\", \"description\": \"用例要素是否完整\", \"max\": 5},
                \"feasibility\": {\"name\": \"可执行性\", \"description\": \"用例是否可以被执行\", \"max\": 5},
                \"coverage\": {\"name\": \"覆盖度\", \"description\": \"用例覆盖范围是否充分\", \"max\": 5}
             }', 0, 1, '2026-01-25 02:54:53', '2026-01-25 02:54:53'),
(3, 'API接口测试用例评审模板', '适用于API接口的测试用例评审', 'api', '[
                {\"id\": 1, \"item\": \"用例标题是否清晰明确？\", \"required\": true},
                {\"id\": 2, \"item\": \"前置条件是否完整？\", \"required\": true},
                {\"id\": 3, \"item\": \"请求参数是否完整？\", \"required\": true},
                {\"id\": 4, \"item\": \"预期响应是否明确？\", \"required\": true},
                {\"id\": 5, \"item\": \"是否验证了响应状态码？\", \"required\": true},
                {\"id\": 6, \"item\": \"是否验证了响应数据结构？\", \"required\": true},
                {\"id\": 7, \"item\": \"是否考虑了异常场景？\", \"required\": true},
                {\"id\": 8, \"item\": \"是否考虑了权限验证？\", \"required\": false}
             ]', '{
                \"clarity\": {\"name\": \"清晰度\", \"description\": \"用例描述是否清晰易懂\", \"max\": 5},
                \"completeness\": {\"name\": \"完整性\", \"description\": \"用例要素是否完整\", \"max\": 5},
                \"feasibility\": {\"name\": \"可执行性\", \"description\": \"用例是否可以被执行\", \"max\": 5},
                \"coverage\": {\"name\": \"覆盖度\", \"description\": \"用例覆盖范围是否充分\", \"max\": 5}
             }', 0, 1, '2026-01-25 02:54:53', '2026-01-25 02:54:53'),
(4, '通用测试用例评审模板', '适用于各类测试用例的通用评审模板', 'general', '[
                {\"id\": 1, \"item\": \"用例标题是否清晰明确？\", \"required\": true},
                {\"id\": 2, \"item\": \"前置条件是否完整？\", \"required\": true},
                {\"id\": 3, \"item\": \"测试步骤是否清晰可执行？\", \"required\": true},
                {\"id\": 4, \"item\": \"预期结果是否明确可验证？\", \"required\": true},
                {\"id\": 5, \"item\": \"用例是否覆盖了需求的关键点？\", \"required\": true},
                {\"id\": 6, \"item\": \"用例优先级是否合理？\", \"required\": false},
                {\"id\": 7, \"item\": \"用例类型分类是否准确？\", \"required\": false}
             ]', '{
                \"clarity\": {\"name\": \"清晰度\", \"description\": \"用例描述是否清晰易懂\", \"max\": 5},
                \"completeness\": {\"name\": \"完整性\", \"description\": \"用例要素是否完整\", \"max\": 5},
                \"feasibility\": {\"name\": \"可执行性\", \"description\": \"用例是否可以被执行\", \"max\": 5},
                \"coverage\": {\"name\": \"覆盖度\", \"description\": \"用例覆盖范围是否充分\", \"max\": 5}
             }', 1, 1, '2026-01-25 02:55:50', '2026-01-25 02:55:50'),
(5, 'Web应用测试用例评审模板', '适用于Web应用的测试用例评审', 'web', '[
                {\"id\": 1, \"item\": \"用例标题是否清晰明确？\", \"required\": true},
                {\"id\": 2, \"item\": \"前置条件是否完整？\", \"required\": true},
                {\"id\": 3, \"item\": \"测试步骤是否清晰可执行？\", \"required\": true},
                {\"id\": 4, \"item\": \"预期结果是否明确可验证？\", \"required\": true},
                {\"id\": 5, \"item\": \"是否考虑了浏览器兼容性？\", \"required\": false},
                {\"id\": 6, \"item\": \"是否考虑了响应式设计？\", \"required\": false},
                {\"id\": 7, \"item\": \"是否考虑了安全性测试？\", \"required\": false},
                {\"id\": 8, \"item\": \"是否考虑了性能测试？\", \"required\": false}
             ]', '{
                \"clarity\": {\"name\": \"清晰度\", \"description\": \"用例描述是否清晰易懂\", \"max\": 5},
                \"completeness\": {\"name\": \"完整性\", \"description\": \"用例要素是否完整\", \"max\": 5},
                \"feasibility\": {\"name\": \"可执行性\", \"description\": \"用例是否可以被执行\", \"max\": 5},
                \"coverage\": {\"name\": \"覆盖度\", \"description\": \"用例覆盖范围是否充分\", \"max\": 5}
             }', 0, 1, '2026-01-25 02:55:50', '2026-01-25 02:55:50'),
(6, 'API接口测试用例评审模板', '适用于API接口的测试用例评审', 'api', '[
                {\"id\": 1, \"item\": \"用例标题是否清晰明确？\", \"required\": true},
                {\"id\": 2, \"item\": \"前置条件是否完整？\", \"required\": true},
                {\"id\": 3, \"item\": \"请求参数是否完整？\", \"required\": true},
                {\"id\": 4, \"item\": \"预期响应是否明确？\", \"required\": true},
                {\"id\": 5, \"item\": \"是否验证了响应状态码？\", \"required\": true},
                {\"id\": 6, \"item\": \"是否验证了响应数据结构？\", \"required\": true},
                {\"id\": 7, \"item\": \"是否考虑了异常场景？\", \"required\": true},
                {\"id\": 8, \"item\": \"是否考虑了权限验证？\", \"required\": false}
             ]', '{
                \"clarity\": {\"name\": \"清晰度\", \"description\": \"用例描述是否清晰易懂\", \"max\": 5},
                \"completeness\": {\"name\": \"完整性\", \"description\": \"用例要素是否完整\", \"max\": 5},
                \"feasibility\": {\"name\": \"可执行性\", \"description\": \"用例是否可以被执行\", \"max\": 5},
                \"coverage\": {\"name\": \"覆盖度\", \"description\": \"用例覆盖范围是否充分\", \"max\": 5}
             }', 0, 1, '2026-01-25 02:55:50', '2026-01-25 02:55:50');


-- 表结构: role_menus
DROP TABLE IF EXISTS `role_menus`;
CREATE TABLE `role_menus` (
  `role_id` int NOT NULL,
  `menu_id` int NOT NULL,
  PRIMARY KEY (`role_id`,`menu_id`),
  KEY `menu_id` (`menu_id`),
  CONSTRAINT `role_menus_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `role_menus_ibfk_2` FOREIGN KEY (`menu_id`) REFERENCES `menus` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色菜单关联表';

-- 表数据: role_menus
INSERT INTO `role_menus` (role_id, menu_id) VALUES
(1, 10),
(2, 10),
(1, 11),
(2, 11),
(1, 12),
(2, 12),
(1, 13),
(2, 13),
(1, 14),
(2, 14),
(1, 15),
(2, 15),
(1, 16),
(2, 16),
(1, 17),
(2, 17),
(1, 19),
(2, 19),
(1, 20),
(1, 21),
(1, 22),
(1, 23),
(1, 24),
(1, 25),
(2, 25),
(1, 26),
(2, 26),
(1, 28),
(2, 28);


-- 表结构: role_permissions
DROP TABLE IF EXISTS `role_permissions`;
CREATE TABLE `role_permissions` (
  `role_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`role_id`,`permission_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色权限关联表';

-- 表数据: role_permissions
INSERT INTO `role_permissions` (role_id, permission_id) VALUES
(1, 1),
(2, 1),
(1, 2),
(2, 2),
(1, 3),
(2, 3),
(1, 4),
(1, 5),
(2, 5),
(1, 6),
(2, 6),
(1, 7),
(2, 7),
(1, 8),
(1, 9),
(2, 9),
(1, 10),
(2, 10),
(1, 11),
(2, 11),
(1, 12),
(2, 12),
(1, 13),
(2, 13),
(1, 14),
(2, 14),
(1, 15),
(1, 16),
(2, 16),
(1, 17),
(2, 17),
(1, 18),
(2, 18),
(1, 19),
(1, 20),
(2, 20),
(1, 21),
(2, 21),
(1, 22),
(1, 23),
(1, 24),
(1, 25),
(1, 26),
(1, 27),
(2, 27),
(1, 28),
(1, 29),
(1, 30),
(2, 30),
(1, 31),
(1, 32),
(1, 33),
(1, 34),
(2, 34),
(1, 35),
(2, 35),
(1, 36),
(2, 36),
(1, 48),
(2, 48),
(1, 49),
(2, 49),
(1, 50),
(2, 50),
(1, 51),
(1, 52),
(2, 52),
(1, 53),
(2, 53),
(1, 54),
(2, 54),
(1, 55),
(1, 56),
(1, 57);


-- 表结构: roles
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色名称',
  `code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色编码',
  `description` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '角色描述',
  `status` int DEFAULT '1' COMMENT '状态: 1启用 0禁用',
  `sort` int DEFAULT '0' COMMENT '排序',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `code` (`code`),
  KEY `idx_code` (`code`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- 表数据: roles
INSERT INTO `roles` (id, name, code, description, status, sort, created_at, updated_at) VALUES
(1, '超级管理员', 'admin', '系统超级管理员，拥有所有权限', 1, 0, '2026-01-23 17:34:52', '2026-01-23 17:34:52'),
(2, '普通用户', 'user', '普通用户，可使用基本功能', 1, 1, '2026-01-23 17:34:52', '2026-01-23 17:34:52');


-- 表结构: testcase_reviews
DROP TABLE IF EXISTS `testcase_reviews`;
CREATE TABLE `testcase_reviews` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '评审ID',
  `testcase_id` int NOT NULL COMMENT '测试用例ID',
  `reviewer_id` int NOT NULL COMMENT '评审人ID',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'pending' COMMENT '评审状态: pending-待评审, approved-通过, rejected-拒绝, need_revision-需要修改',
  `overall_rating` int DEFAULT NULL COMMENT '整体评分: 1-5分',
  `comments` text COLLATE utf8mb4_unicode_ci COMMENT '评审意见',
  `improvement_suggestions` text COLLATE utf8mb4_unicode_ci COMMENT '改进建议',
  `clarity_score` int DEFAULT NULL COMMENT '清晰度评分: 1-5分',
  `completeness_score` int DEFAULT NULL COMMENT '完整性评分: 1-5分',
  `feasibility_score` int DEFAULT NULL COMMENT '可执行性评分: 1-5分',
  `coverage_score` int DEFAULT NULL COMMENT '覆盖度评分: 1-5分',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `reviewed_at` datetime DEFAULT NULL COMMENT '评审时间',
  PRIMARY KEY (`id`),
  KEY `idx_testcase_id` (`testcase_id`),
  KEY `idx_reviewer_id` (`reviewer_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `testcase_reviews_ibfk_1` FOREIGN KEY (`testcase_id`) REFERENCES `testcases` (`id`) ON DELETE CASCADE,
  CONSTRAINT `testcase_reviews_ibfk_2` FOREIGN KEY (`reviewer_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试用例评审表';

-- 表数据: testcase_reviews
INSERT INTO `testcase_reviews` (id, testcase_id, reviewer_id, status, overall_rating, comments, improvement_suggestions, clarity_score, completeness_score, feasibility_score, coverage_score, created_at, reviewed_at) VALUES
(1, 1, 1, 'need_revision', 3, '该测试用例是一个核心功能的正向测试场景，步骤和预期结果基本清晰，可执行性高。但用例要素不够完整，覆盖度严重不足，仅覆盖了最基础的正常流程，缺乏对异常场景、边界条件和特殊情况的考虑。', '1. 补充测试数据：建议在步骤中明确具体的测试数据（如：用户名：test_user，密码：Test@123），或说明使用已注册的特定账户。
2. 完善预期结果：增加对登录后状态（如Cookie/Session）、页面元素（如退出按钮）的验证点。
3. 增加覆盖度：强烈建议基于此用例，补充一系列相关测试用例，例如：
   - 用户名正确，密码错误
   - 用户名不存在
   - 用户名或密码为空
   - 密码输入框是否显示为密文
   - 登录失败后的错误提示信息
   - 登录成功后，点击浏览器后退按钮的行为
   - 多次登录失败后的账户锁定机制（如有）
   - 记住密码功能（如有）
4. 考虑将标题修改为更具体的描述，例如：\"TC-LOGIN-001: 使用有效凭证成功登录系统\"。', 4, 3, 5, 2, '2026-01-25 02:56:58', '2026-01-25 03:49:06'),
(2, 2, 1, 'need_revision', 3, '用例设计思路很好，覆盖了重要的安全边界场景（登录失败次数限制）。步骤描述基本清晰，预期结果包含了关键验证点。', '1. 前置条件“当前登录失败次数为0”难以直接验证和保证，建议修改为更可操作的条件，例如“确保测试账号在本次测试前未进行过失败登录”或“通过后台重置该账号的登录失败计数”。2. 测试步骤4“重复步骤1-3两次”描述可以更精确，建议明确写出第二次和第三次的具体操作。3. 预期结果2可以更具体，例如描述验证码输入框出现的位置（如在密码框下方）或要求（如必须输入正确的验证码）。4. 建议增加一个验证点：触发验证码后，输入正确用户名、密码和验证码，应能成功登录。', 4, 3, 3, 4, '2026-01-25 02:56:58', '2026-01-25 03:50:07'),
(3, 3, 1, 'need_revision', 3, '用例覆盖了重要的异常场景（用户名不存在）。步骤简单明了。但预期结果的第三点“登录失败计数器应增加1”存在与用例2类似的可执行性问题。', '1. 预期结果3“登录失败计数器应增加1”通常无法在前端直接验证，属于后台逻辑。建议修改为更前端可验证的结果，或明确指出需要结合后台日志/数据库进行验证。2. 错误提示信息“用户名或密码错误”是通用安全提示，用例可以说明这是可接受的设计。3. 可以补充测试密码为空、用户名为空等更多异常场景的测试用例，以形成更完整的异常测试集。4. 建议明确“任意密码”的示例（如“test123”），或说明密码格式要求（如符合复杂度规则）。', 4, 3, 3, 3, '2026-01-25 02:56:58', '2026-01-25 03:50:07'),
(4, 1, 1, 'approved', 4, '用例结构清晰，步骤明确，预期结果具体，覆盖了核心的正常登录流程。前置条件、步骤和预期结果要素完整。', '1. 预期结果可以更具体，例如明确跳转后的具体页面URL或页面标题。2. 可以考虑增加对登录后会话状态（如Cookie/Session）的验证。3. 可以补充测试数据（例如具体的用户名示例），使用例更具可读性。', 5, 4, 5, 3, '2026-01-25 03:50:07', '2026-01-25 03:50:07'),
(5, 4, 2, 'need_revision', 3, '用例覆盖了核心的未登录引导场景，但步骤和预期结果过于笼统，缺乏具体的验证点和可执行细节。', '1. 测试步骤应更具体，例如：\'1.1 点击App首页的PAY按钮。1.2 观察页面是否跳转至被扫主页，或是否弹出登录弹窗/跳转至登录页。\' 2. 预期结果应更具体且可验证，例如：\'2.1 系统检测到用户无登录态，应弹出登录弹窗或跳转至登录页。2.2 登录弹窗/页面应包含明确的登录引导文案（如\'请先登录\'）。2.3 用户输入正确凭据登录后，应自动跳转回被扫主页并正常展示二维码。\' 3. 可考虑增加异常场景，如用户取消登录后的行为。', 3, 3, 3, 3, '2026-01-25 05:06:09', '2026-01-25 05:06:09'),
(6, 5, 2, 'approved', 4, '用例设计良好，步骤清晰，覆盖了正常流程的主要环节，预期结果具体且可验证。', '1. 可增加一个步骤，验证用户取消soft token验证或输入错误密码时的处理流程。2. 在预期结果中，可以更明确地说明\'开卡成功页面\'应包含的关键信息（如VDC卡号后四位、绑定账户信息等）。3. 考虑增加前置条件中网络状态的说明（如网络正常）。', 5, 4, 5, 4, '2026-01-25 05:06:09', '2026-01-25 05:06:09'),
(7, 6, 2, 'need_revision', 3, '用例覆盖了无绑定账户的场景，逻辑清晰。但步骤和预期结果中关于\'开户流程\'的描述过于笼统，这是一个独立的复杂子流程，不应在本用例中一笔带过。', '1. 明确本用例的测试重点应为\'检测无可绑定账户\'和\'引导开户\'的环节，而非完整的开户流程。建议将步骤4和5修改为：\'4. 用户点击其中一种账户类型（如Saving）的开通按钮。5. 观察系统响应。\' 2. 相应调整预期结果：\'3. 用户点击开通按钮后，应跳转至对应的银行账户开户流程页面（或启动开户流程）。\' 3. 可增加一个场景：用户从开户流程中途返回，观察是否回到VDC开通引导页。', 4, 3, 3, 3, '2026-01-25 05:06:09', '2026-01-25 05:06:09'),
(8, 7, 2, 'need_revision', 3, '用例覆盖了重要的安全异常场景，方向正确。但步骤和预期结果不够精确，且覆盖不全。', '1. 测试步骤应更具体：\'2.1 尝试使用物理按键组合（电源+音量下）截图。2.2 尝试使用系统下拉菜单的截图按钮（如有）。2.3 尝试使用三指下滑等手势截图（如设备支持）。\' 2. 预期结果应更具体：\'2.1 对于所有截图方式，操作应被拦截，系统相册中不应出现该页面的截图。2.2 屏幕应出现Toast提示，提示文案需与产品需求一致（需明确具体文案）。\' 3. 应增加iOS设备的测试用例，因为实现机制可能不同。4. 可考虑增加录屏场景的测试。', 4, 3, 4, 2, '2026-01-25 05:06:09', '2026-01-25 05:06:09'),
(9, 8, 2, 'approved', 5, '用例设计优秀，是典型的边界条件测试。步骤分解细致（59秒，60秒，61秒），预期结果明确且可量化验证，覆盖了刷新触发点前后的状态。', '1. 在步骤1中，\'记录二维码信息\'的方法可以更具体，例如：\'记录二维码中心部分图案的截图，或通过调试工具获取二维码对应的唯一字符串/令牌。\' 2. 可考虑增加网络异常场景下的测试：在59秒时断网，观察60秒时刷新行为（是否失败、是否有重试机制）。', 5, 5, 5, 5, '2026-01-25 05:06:09', '2026-01-25 05:06:09');


-- 表结构: testcases
DROP TABLE IF EXISTS `testcases`;
CREATE TABLE `testcases` (
  `id` int NOT NULL AUTO_INCREMENT,
  `requirement_id` int DEFAULT NULL COMMENT '关联需求ID，可为空',
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用例标题',
  `precondition` text COLLATE utf8mb4_unicode_ci COMMENT '前置条件',
  `steps` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '测试步骤',
  `expected_result` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '预期结果',
  `case_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'functional' COMMENT '用例类型: functional/boundary/exception/performance',
  `priority` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'medium' COMMENT '优先级: high/medium/low',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'pending' COMMENT '状态: pending/passed/failed/blocked',
  `is_ai_generated` tinyint(1) DEFAULT '0' COMMENT '是否AI生成',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_requirement_id` (`requirement_id`),
  KEY `idx_case_type` (`case_type`),
  KEY `idx_status` (`status`),
  KEY `idx_is_ai_generated` (`is_ai_generated`),
  CONSTRAINT `testcases_ibfk_1` FOREIGN KEY (`requirement_id`) REFERENCES `requirements` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试用例表';

-- 表数据: testcases
INSERT INTO `testcases` (id, requirement_id, title, precondition, steps, expected_result, case_type, priority, status, is_ai_generated, created_at, updated_at) VALUES
(1, 1, '功能测试-使用正确的用户名和密码成功登录', '1. 用户已注册，拥有有效的用户名和密码。
2. 登录页面可正常访问。', '1. 在登录页面的用户名输入框中输入正确的用户名。
2. 在密码输入框中输入对应的正确密码。
3. 点击“登录”按钮。', '1. 登录成功，页面跳转至系统主页或用户个人中心。
2. 页面顶部显示欢迎信息或用户名。', 'functional', 'high', 'passed', 1, '2026-01-24 07:23:15', '2026-01-25 04:01:12'),
(2, 1, '边界值测试-连续3次登录失败后触发验证码输入', '1. 用户已注册，拥有有效的用户名和密码。
2. 登录页面可正常访问。
3. 当前登录失败次数为0。', '1. 在登录页面的用户名输入框中输入正确的用户名。
2. 在密码输入框中输入错误的密码。
3. 点击“登录”按钮。
4. 重复步骤1-3两次（共进行三次错误的登录尝试）。
5. 第四次尝试时，在用户名和密码输入框输入信息后，观察页面。', '1. 前三次登录失败，页面应显示“用户名或密码错误”的提示。
2. 第四次尝试时，登录页面应出现验证码输入框，要求用户输入验证码后才能继续尝试登录。', 'boundary', 'high', 'pending', 1, '2026-01-24 07:23:15', '2026-01-24 07:23:15'),
(3, 1, '异常测试-使用不存在的用户名进行登录', '1. 登录页面可正常访问。
2. 准备一个系统中不存在的用户名。', '1. 在登录页面的用户名输入框中输入一个不存在的用户名（例如：`nonexistent_user_123`）。
2. 在密码输入框中输入任意密码。
3. 点击“登录”按钮。', '1. 登录失败，页面不跳转。
2. 页面应清晰显示错误提示信息，例如“用户名或密码错误”。
3. 登录失败计数器应增加1。', 'exception', 'medium', 'pending', 1, '2026-01-24 07:23:15', '2026-01-24 07:23:15'),
(4, NULL, '用户首次进入被扫主页，未登录，验证登录引导流程', '用户已安装Livi App，但未登录。用户点击PAY按钮进入被扫主页。', '1. 用户点击App内的PAY按钮。
2. 观察页面跳转和提示。', '1. 系统检测到用户无登录态。
2. 页面跳转或弹出提示，引导用户完成登录。
3. 用户完成登录后，应能继续进入被扫主页流程。', 'functional', 'high', 'pending', 1, '2026-01-25 05:03:51', '2026-01-25 05:03:51'),
(5, NULL, '用户有可绑定账户，在独立流程中开通VDC（已设置soft token）', '用户已登录Livi App，且至少有一个可绑定VDC的银行账户（如Saving或Credit）。用户已设置soft token。用户通过广告位进入VDC开通流程。', '1. 用户点击VDC开通入口（如广告位）。
2. 系统判断用户有可绑定账户，展示VDC开通协议和引导页面。
3. 用户确认协议（复选框默认勾选），并选择一个银行账户进行绑定。
4. 用户点击确认（Done）按钮。
5. 系统检测到用户已设置soft token，进行soft token核身验证。
6. 用户输入正确的soft token密码。', '1. 页面正确展示VDC开通协议和可绑定的账户列表。
2. 协议复选框默认勾选，Done按钮可点击。
3. 用户选择账户并确认后，触发soft token验证。
4. soft token验证通过后，成功开通VDC并绑定所选账户，跳转至开卡成功页面。', 'functional', 'high', 'pending', 1, '2026-01-25 05:03:51', '2026-01-25 05:03:51'),
(6, NULL, '用户无任何可绑定VDC的账户，在独立流程中开通VDC', '用户已登录Livi App，且没有任何可绑定VDC的银行账户（无Saving、Credit、Livi-Buy账户）。用户通过广告位进入VDC开通流程。', '1. 用户点击VDC开通入口（如广告位）。
2. 观察系统页面展示。
3. 系统应引导用户开通一个可绑定VDC的账户。
4. 用户选择一种账户类型（如Saving）并完成开户流程。
5. 开户成功后，观察页面跳转。', '1. 系统检测到用户无可绑定账户，展示可绑定VDC的银行账户类型列表（如Saving和Credit），并附有文字说明。
2. 用户选择一种账户类型后，进入对应的开户流程。
3. 用户成功开户后，自动返回到VDC开卡流程，并展示VDC开通协议和引导页面，且新开的账户作为可绑定选项。', 'functional', 'medium', 'pending', 1, '2026-01-25 05:03:51', '2026-01-25 05:03:51'),
(7, NULL, '用户在被扫二维码页面尝试截图（Android设备）', '用户已登录Livi App，且已开通二维码被扫功能。用户进入被扫主页，二维码正常展示。测试设备为Android手机。', '1. 用户停留在被扫主页。
2. 用户使用设备自带的截图功能（如电源键+音量下键）进行截图。
3. 观察屏幕提示。', '1. 截图操作被应用拦截。
2. 屏幕出现Toast提示，内容为\'为了交易安全，暂不支持截图\'或类似文案。
3. 用户无法成功保存包含二维码的截图。', 'exception', 'medium', 'pending', 1, '2026-01-25 05:03:51', '2026-01-25 05:03:51'),
(8, NULL, '被扫主页二维码自动刷新时间边界测试（60秒）', '用户已登录Livi App，且已开通二维码被扫功能。网络连接正常。用户进入被扫主页。', '1. 进入被扫主页，记录当前显示的二维码信息（如部分编码或截图时间戳）。
2. 停留在该页面，不做任何操作，等待60秒。
3. 观察60秒前后二维码是否发生变化。
4. 在等待59秒时，观察二维码是否未刷新。
5. 在等待61秒时，观察二维码是否已刷新。', '1. 进入页面时，显示一个有效的二维码。
2. 在59秒时，二维码未刷新，与初始二维码一致。
3. 在60秒（或60-61秒之间），二维码自动向服务端拉取并刷新为新的二维码，与旧二维码不同。
4. 刷新过程无页面卡顿或错误提示。', 'boundary', 'low', 'pending', 1, '2026-01-25 05:03:51', '2026-01-25 05:03:51');


-- 表结构: user_roles
DROP TABLE IF EXISTS `user_roles`;
CREATE TABLE `user_roles` (
  `user_id` int NOT NULL,
  `role_id` int NOT NULL,
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表';

-- 表数据: user_roles
INSERT INTO `user_roles` (user_id, role_id) VALUES
(1, 1),
(2, 2);


-- 表结构: users
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `email` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '邮箱',
  `password_hash` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '密码哈希',
  `nickname` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '昵称',
  `avatar` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '头像',
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'active' COMMENT '状态: active/inactive/banned',
  `last_login` datetime DEFAULT NULL COMMENT '最后登录时间',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 表数据: users
INSERT INTO `users` (id, username, email, password_hash, nickname, avatar, status, last_login, created_at, updated_at) VALUES
(1, 'admin', 'admin@example.com', 'scrypt:32768:8:1$eryBIDwmPi2kYug3$1d0a23aa4853a070bbbf9d8bc90da015ce755a106979cb295a39e2695af508dc19c2c2a47ef81f41e8dccb6d6f3e43b9070b3de87bac6e7374f20755d4cb02e2', '管理员', NULL, 'active', '2026-01-25 06:46:06', '2026-01-23 17:34:52', '2026-01-25 06:46:06'),
(2, 'testuser', 'testuser@example.com', 'scrypt:32768:8:1$3vE8QFk9A0UOknBJ$e16543b6dc374e9341083a0aeb061e738c1c139b2d93a8996de97ec15ebfb5e826002db4d17d8e88626cceb35a0750ff5159116ee78957b7d6b18de8286cc5c0', '测试用户', NULL, 'active', '2026-01-25 07:00:43', '2026-01-23 17:34:52', '2026-01-25 07:00:43'),
(3, 'persistence_test', 'test@example.com', 'scrypt:32768:8:1$yHu27kzY5RRwaxHM$ae5426fb2964e1a123912eb1a559dc5caaf5d9f9bac6ea67334273934fa3408997e8b04df06b8f8f5651391b0d53eb967785bcb949bd364679994a946c055eee', NULL, NULL, 'active', '2026-01-24 14:36:16', '2026-01-24 14:34:58', '2026-01-24 14:36:16');


SET FOREIGN_KEY_CHECKS = 1;