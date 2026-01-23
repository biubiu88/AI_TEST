"""
数据库初始化脚本
创建默认用户：admin/admin123 和 testuser/123456
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import pymysql

# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'testcase_generator'),
    'charset': 'utf8mb4'
}

# 生成密码哈希
ADMIN_PASSWORD_HASH = generate_password_hash('admin123')
TESTUSER_PASSWORD_HASH = generate_password_hash('123456')

print(f"Admin password hash: {ADMIN_PASSWORD_HASH}")
print(f"Testuser password hash: {TESTUSER_PASSWORD_HASH}")


def init_database():
    """初始化数据库"""
    conn = None
    try:
        # 先连接不指定数据库
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        print(f"\n=== 连接到数据库 {DB_CONFIG['database']} ===")
        
        # 备份 llm_configs 表数据
        llm_configs_data = []
        try:
            cursor.execute("SELECT * FROM llm_configs")
            llm_configs_data = cursor.fetchall()
            cursor.execute("SHOW COLUMNS FROM llm_configs")
            llm_configs_columns = [col[0] for col in cursor.fetchall()]
            print(f"已备份 {len(llm_configs_data)} 条模型配置数据")
        except Exception as e:
            print(f"llm_configs表不存在或为空: {e}")
            llm_configs_columns = []
        
        # 关闭外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # 删除除 llm_configs 外的所有表
        tables_to_drop = [
            'user_roles', 'role_permissions', 'role_menus',
            'testcases', 'requirements', 'users', 'roles', 
            'permissions', 'menus', 'prompts', 'knowledges'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"删除表: {table}")
            except Exception as e:
                print(f"删除表 {table} 失败: {e}")
        
        # 开启外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        print("\n=== 重新创建表结构 ===")
        
        # 创建用户表
        cursor.execute("""
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表'
        """)
        print("创建表: users")
        
        # 创建角色表
        cursor.execute("""
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表'
        """)
        print("创建表: roles")
        
        # 创建权限表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL COMMENT '权限名称',
                code VARCHAR(100) UNIQUE NOT NULL COMMENT '权限编码',
                type VARCHAR(20) DEFAULT 'button' COMMENT '权限类型: menu/button/api',
                description VARCHAR(200) COMMENT '权限描述',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                INDEX idx_code (code),
                INDEX idx_type (type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限表'
        """)
        print("创建表: permissions")
        
        # 创建菜单表
        cursor.execute("""
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜单表'
        """)
        print("创建表: menus")
        
        # 创建关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_roles (
                user_id INT NOT NULL,
                role_id INT NOT NULL,
                PRIMARY KEY (user_id, role_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表'
        """)
        print("创建表: user_roles")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS role_permissions (
                role_id INT NOT NULL,
                permission_id INT NOT NULL,
                PRIMARY KEY (role_id, permission_id),
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
                FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色权限关联表'
        """)
        print("创建表: role_permissions")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS role_menus (
                role_id INT NOT NULL,
                menu_id INT NOT NULL,
                PRIMARY KEY (role_id, menu_id),
                FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
                FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色菜单关联表'
        """)
        print("创建表: role_menus")
        
        # 创建需求表
        cursor.execute("""
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='需求文档表'
        """)
        print("创建表: requirements")
        
        # 创建测试用例表
        cursor.execute("""
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试用例表'
        """)
        print("创建表: testcases")
        
        # 创建提示词表
        cursor.execute("""
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='提示词表'
        """)
        print("创建表: prompts")
        
        # 创建知识库表
        cursor.execute("""
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识库表'
        """)
        print("创建表: knowledges")
        
        # 检查并创建 llm_configs 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_configs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL COMMENT '配置名称',
                provider VARCHAR(50) NOT NULL COMMENT '供应商',
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='大模型配置表'
        """)
        print("创建表: llm_configs (保留原有数据)")
        
        print("\n=== 插入初始数据 ===")
        
        # 插入角色
        cursor.execute("""
            INSERT INTO roles (name, code, description, status, sort) VALUES
            ('超级管理员', 'admin', '系统超级管理员，拥有所有权限', 1, 0),
            ('普通用户', 'user', '普通用户，可使用基本功能', 1, 1)
        """)
        print("插入角色数据")
        
        # 插入权限
        cursor.execute("""
            INSERT INTO permissions (name, code, type, description) VALUES
            ('需求查看', 'requirement:view', 'button', '查看需求列表和详情'),
            ('需求新增', 'requirement:create', 'button', '新增需求'),
            ('需求编辑', 'requirement:edit', 'button', '编辑需求'),
            ('需求删除', 'requirement:delete', 'button', '删除需求'),
            ('用例查看', 'testcase:view', 'button', '查看测试用例'),
            ('用例新增', 'testcase:create', 'button', '新增测试用例'),
            ('用例编辑', 'testcase:edit', 'button', '编辑测试用例'),
            ('用例删除', 'testcase:delete', 'button', '删除测试用例'),
            ('用例导入', 'testcase:import', 'button', '导入测试用例'),
            ('用例导出', 'testcase:export', 'button', '导出测试用例'),
            ('AI生成', 'ai:generate', 'button', '使用AI生成测试用例'),
            ('提示词查看', 'prompt:view', 'button', '查看提示词'),
            ('提示词新增', 'prompt:create', 'button', '新增提示词'),
            ('提示词编辑', 'prompt:edit', 'button', '编辑提示词'),
            ('提示词删除', 'prompt:delete', 'button', '删除提示词'),
            ('知识库查看', 'knowledge:view', 'button', '查看知识库'),
            ('知识库新增', 'knowledge:create', 'button', '新增知识库'),
            ('知识库编辑', 'knowledge:edit', 'button', '编辑知识库'),
            ('知识库删除', 'knowledge:delete', 'button', '删除知识库'),
            ('模型配置查看', 'llm:view', 'button', '查看大模型配置'),
            ('模型配置新增', 'llm:create', 'button', '新增大模型配置'),
            ('模型配置编辑', 'llm:edit', 'button', '编辑大模型配置'),
            ('模型配置删除', 'llm:delete', 'button', '删除大模型配置'),
            ('用户管理', 'system:user', 'menu', '用户管理权限'),
            ('角色管理', 'system:role', 'menu', '角色管理权限'),
            ('菜单管理', 'system:menu', 'menu', '菜单管理权限')
        """)
        print("插入权限数据")
        
        # 插入菜单
        cursor.execute("""
            INSERT INTO menus (parent_id, name, path, component, redirect, icon, title, hidden, always_show, keep_alive, sort, type, permission, status) VALUES
            (0, 'Root', '/', 'Layout', '/requirements', NULL, '首页', FALSE, FALSE, FALSE, 0, 'directory', NULL, 1),
            (1, 'Requirements', '/requirements', 'RequirementView', NULL, 'Document', '需求管理', FALSE, FALSE, TRUE, 1, 'menu', 'requirement:view', 1),
            (1, 'TestCases', '/testcases', 'TestCaseView', NULL, 'List', '测试用例', FALSE, FALSE, TRUE, 2, 'menu', 'testcase:view', 1),
            (1, 'Generate', '/generate', 'GenerateView', NULL, 'MagicStick', '生成用例', FALSE, FALSE, FALSE, 3, 'menu', 'ai:generate', 1),
            (1, 'Prompts', '/prompts', 'PromptView', NULL, 'ChatDotRound', '提示词管理', FALSE, FALSE, TRUE, 4, 'menu', 'prompt:view', 1),
            (1, 'Knowledges', '/knowledges', 'KnowledgeView', NULL, 'Collection', '知识库管理', FALSE, FALSE, TRUE, 5, 'menu', 'knowledge:view', 1),
            (1, 'LLMConfigs', '/llm-configs', 'LLMConfigView', NULL, 'Setting', '大模型配置', FALSE, FALSE, TRUE, 6, 'menu', 'llm:view', 1)
        """)
        print("插入菜单数据")
        
        # 为管理员角色分配所有权限
        cursor.execute("INSERT INTO role_permissions (role_id, permission_id) SELECT 1, id FROM permissions")
        print("为管理员分配所有权限")
        
        # 为管理员角色分配所有菜单
        cursor.execute("INSERT INTO role_menus (role_id, menu_id) SELECT 1, id FROM menus")
        print("为管理员分配所有菜单")
        
        # 为普通用户角色分配基本权限
        cursor.execute("""
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT 2, id FROM permissions WHERE code IN (
                'requirement:view', 'requirement:create', 'requirement:edit',
                'testcase:view', 'testcase:create', 'testcase:edit', 'testcase:export',
                'ai:generate',
                'prompt:view',
                'knowledge:view'
            )
        """)
        print("为普通用户分配基本权限")
        
        # 为普通用户角色分配基本菜单
        cursor.execute("INSERT INTO role_menus (role_id, menu_id) SELECT 2, id FROM menus WHERE id <= 7")
        print("为普通用户分配基本菜单")
        
        # 插入用户
        cursor.execute(f"""
            INSERT INTO users (username, email, password_hash, nickname, status) VALUES
            ('admin', 'admin@example.com', '{ADMIN_PASSWORD_HASH}', '管理员', 'active'),
            ('testuser', 'testuser@example.com', '{TESTUSER_PASSWORD_HASH}', '测试用户', 'active')
        """)
        print("插入用户: admin, testuser")
        
        # 分配用户角色
        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (1, 1)")  # admin -> 超级管理员
        cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (2, 2)")  # testuser -> 普通用户
        print("分配用户角色")
        
        # 插入示例需求
        cursor.execute("""
            INSERT INTO requirements (title, content, module, priority, status) VALUES
            ('用户登录功能', '1. 用户可以使用用户名和密码登录系统\n2. 支持记住密码功能\n3. 登录失败需要显示错误提示\n4. 连续3次登录失败需要输入验证码', '用户模块', 'high', 'in_progress'),
            ('商品搜索功能', '1. 用户可以通过关键词搜索商品\n2. 支持按价格、销量排序\n3. 支持按分类筛选\n4. 搜索结果分页显示，每页20条', '商品模块', 'high', 'pending'),
            ('购物车功能', '1. 用户可以将商品加入购物车\n2. 可以修改商品数量\n3. 可以删除购物车商品\n4. 显示购物车商品总价', '订单模块', 'medium', 'pending')
        """)
        print("插入示例需求")
        
        # 插入默认提示词
        cursor.execute("""
            INSERT INTO prompts (name, content, description, category, is_default, is_active) VALUES
            ('默认测试用例提示词', '你是一位专业的软件测试工程师，擅长根据需求文档编写高质量的测试用例。请确保测试用例具有以下特点：\n1. 测试步骤清晰明确，可执行\n2. 预期结果具体，可验证\n3. 覆盖正常流程和异常场景\n4. 考虑边界条件和特殊情况', '通用的测试用例生成提示词', 'general', TRUE, TRUE),
            ('Web应用测试提示词', '你是一位专业的Web应用测试工程师。请根据需求编写测试用例，特别关注：\n1. 用户界面交互测试\n2. 表单验证和输入校验\n3. 浏览器兼容性\n4. 响应式设计测试\n5. 安全性测试（XSS、CSRF等）', '适用于Web应用的测试用例生成', 'functional', FALSE, TRUE),
            ('API接口测试提示词', '你是一位专业的API测试工程师。请根据需求编写API测试用例，特别关注：\n1. 请求参数验证\n2. 响应状态码检查\n3. 响应数据结构验证\n4. 错误处理和异常场景\n5. 权限和认证测试', '适用于RESTful API的测试用例生成', 'functional', FALSE, TRUE)
        """)
        print("插入默认提示词")
        
        # 插入示例知识库
        cursor.execute("""
            INSERT INTO knowledges (name, content, description, category, file_type, is_active) VALUES
            ('登录功能测试规范', '登录功能测试要点：\n1. 正常登录：正确的用户名和密码\n2. 密码错误：测试错误密码提示\n3. 用户名不存在：测试不存在用户\n4. 空值验证：用户名或密码为空\n5. 特殊字符：包含特殊字符的输入\n6. SQL注入：防止SQL注入攻击\n7. 账户锁定：多次失败后锁定\n8. 验证码：验证码功能测试', '登录功能的测试规范和测试点', 'domain', 'text', TRUE),
            ('表单验证规范', '表单验证测试要点：\n1. 必填字段验证\n2. 字段长度限制\n3. 数据格式验证（邮箱、手机号等）\n4. 数字范围验证\n5. 日期格式验证\n6. 文件上传验证\n7. 密码强度验证\n8. 确认密码一致性', '通用表单验证的测试规范', 'general', 'text', TRUE)
        """)
        print("插入示例知识库")
        
        conn.commit()
        
        print("\n" + "="*50)
        print("数据库初始化完成！")
        print("="*50)
        print("\n默认账号：")
        print("  管理员: admin / admin123")
        print("  测试用户: testuser / 123456")
        print("="*50)
        
    except Exception as e:
        print(f"\n错误: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    init_database()
