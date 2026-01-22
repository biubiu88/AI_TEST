-- 创建数据库
CREATE DATABASE IF NOT EXISTS testcase_generator
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE testcase_generator;

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
  requirement_id INT NOT NULL COMMENT '关联需求ID',
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
  FOREIGN KEY (requirement_id) REFERENCES requirements(id) ON DELETE CASCADE,
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

-- 插入默认提示词
INSERT INTO prompts (name, content, description, category, is_default, is_active) VALUES
('默认测试用例提示词', '你是一位专业的软件测试工程师，擅长根据需求文档编写高质量的测试用例。请确保测试用例具有以下特点：\n1. 测试步骤清晰明确，可执行\n2. 预期结果具体，可验证\n3. 覆盖正常流程和异常场景\n4. 考虑边界条件和特殊情况', '通用的测试用例生成提示词', 'general', TRUE, TRUE),
('Web应用测试提示词', '你是一位专业的Web应用测试工程师。请根据需求编写测试用例，特别关注：\n1. 用户界面交互测试\n2. 表单验证和输入校验\n3. 浏览器兼容性\n4. 响应式设计测试\n5. 安全性测试（XSS、CSRF等）', '适用于Web应用的测试用例生成', 'functional', FALSE, TRUE),
('API接口测试提示词', '你是一位专业的API测试工程师。请根据需求编写API测试用例，特别关注：\n1. 请求参数验证\n2. 响应状态码检查\n3. 响应数据结构验证\n4. 错误处理和异常场景\n5. 权限和认证测试', '适用于RESTful API的测试用例生成', 'functional', FALSE, TRUE);

-- 插入示例知识库
INSERT INTO knowledges (name, content, description, category, file_type, is_active) VALUES
('登录功能测试规范', '登录功能测试要点：\n1. 正常登录：正确的用户名和密码\n2. 密码错误：测试错误密码提示\n3. 用户名不存在：测试不存在用户\n4. 空值验证：用户名或密码为空\n5. 特殊字符：包含特殊字符的输入\n6. SQL注入：防止SQL注入攻击\n7. 账户锁定：多次失败后锁定\n8. 验证码：验证码功能测试', '登录功能的测试规范和测试点', 'domain', 'text', TRUE),
('表单验证规范', '表单验证测试要点：\n1. 必填字段验证\n2. 字段长度限制\n3. 数据格式验证（邮箱、手机号等）\n4. 数字范围验证\n5. 日期格式验证\n6. 文件上传验证\n7. 密码强度验证\n8. 确认密码一致性', '通用表单验证的测试规范', 'general', 'text', TRUE);
