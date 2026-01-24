"""
数据库模型
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


# 用户角色关联表
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

# 角色权限关联表
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

# 角色菜单关联表
role_menus = db.Table('role_menus',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('menu_id', db.Integer, db.ForeignKey('menus.id'), primary_key=True)
)


class Role(db.Model):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment='角色名称')
    code = db.Column(db.String(50), unique=True, nullable=False, comment='角色编码')
    description = db.Column(db.String(200), comment='角色描述')
    status = db.Column(db.Integer, default=1, comment='状态: 1启用 0禁用')
    sort = db.Column(db.Integer, default=0, comment='排序')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联权限
    permissions = db.relationship('Permission', secondary=role_permissions, backref=db.backref('roles', lazy='dynamic'))
    # 关联菜单
    menus = db.relationship('Menu', secondary=role_menus, backref=db.backref('roles', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'status': self.status,
            'sort': self.sort,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'permissions': [p.code for p in self.permissions],
            'menus': [m.id for m in self.menus]
        }


class Permission(db.Model):
    """权限模型"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, comment='权限名称')
    code = db.Column(db.String(100), unique=True, nullable=False, comment='权限编码')
    type = db.Column(db.String(20), default='button', comment='权限类型: menu/button/api')
    description = db.Column(db.String(200), comment='权限描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'type': self.type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Menu(db.Model):
    """菜单模型"""
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_id = db.Column(db.Integer, default=0, comment='父菜单ID')
    name = db.Column(db.String(50), nullable=False, comment='菜单名称')
    path = db.Column(db.String(200), comment='路由路径')
    component = db.Column(db.String(200), comment='组件路径')
    redirect = db.Column(db.String(200), comment='重定向路径')
    icon = db.Column(db.String(50), comment='菜单图标')
    title = db.Column(db.String(50), comment='菜单标题')
    hidden = db.Column(db.Boolean, default=False, comment='是否隐藏')
    always_show = db.Column(db.Boolean, default=False, comment='是否总是显示')
    keep_alive = db.Column(db.Boolean, default=False, comment='是否缓存')
    sort = db.Column(db.Integer, default=0, comment='排序')
    type = db.Column(db.String(20), default='menu', comment='类型: directory/menu/button')
    permission = db.Column(db.String(100), comment='权限标识')
    status = db.Column(db.Integer, default=1, comment='状态: 1启用 0禁用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'parentId': self.parent_id,
            'name': self.name,
            'path': self.path,
            'component': self.component,
            'redirect': self.redirect,
            'meta': {
                'icon': self.icon,
                'title': self.title,
                'hidden': self.hidden,
                'alwaysShow': self.always_show,
                'keepAlive': self.keep_alive,
                'permission': self.permission
            },
            'sort': self.sort,
            'type': self.type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def build_tree(menus, parent_id=0):
        """构建菜单树"""
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                node = menu.to_dict()
                children = Menu.build_tree(menus, menu.id)
                if children:
                    node['children'] = children
                tree.append(node)
        return sorted(tree, key=lambda x: x['sort'])

    @staticmethod
    def build_tree_with_parents(menus):
        """构建菜单树，自动包含父菜单"""
        # 收集所有菜单ID和父菜单ID
        menu_ids = {menu.id for menu in menus}
        parent_ids = {menu.parent_id for menu in menus if menu.parent_id != 0}

        # 递归获取所有父菜单
        all_menu_ids = set(menu_ids)
        current_parent_ids = set(parent_ids)

        while current_parent_ids:
            # 查找当前父菜单的父菜单
            new_parent_ids = set()
            for parent_id in current_parent_ids:
                if parent_id not in all_menu_ids:
                    parent_menu = Menu.query.get(parent_id)
                    if parent_menu and parent_menu.status == 1:
                        all_menu_ids.add(parent_menu.id)
                        if parent_menu.parent_id != 0:
                            new_parent_ids.add(parent_menu.parent_id)

            current_parent_ids = new_parent_ids

        # 获取所有需要的菜单
        all_menus = Menu.query.filter(Menu.id.in_(all_menu_ids), Menu.status == 1).all()

        # 构建菜单树
        return Menu.build_tree(all_menus, parent_id=0)


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(120), unique=True, nullable=False, comment='邮箱')
    password_hash = db.Column(db.String(256), nullable=False, comment='密码哈希')
    nickname = db.Column(db.String(80), comment='昵称')
    avatar = db.Column(db.String(256), comment='头像')
    status = db.Column(db.String(20), default='active', comment='状态: active/inactive/banned')
    last_login = db.Column(db.DateTime, comment='最后登录时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联角色
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def get_permissions(self):
        """获取用户所有权限"""
        permissions = set()
        for role in self.roles:
            if role.status == 1:
                for perm in role.permissions:
                    permissions.add(perm.code)
        return list(permissions)
    
    def get_menus(self):
        """获取用户所有菜单"""
        menus = []
        menu_ids = set()
        for role in self.roles:
            if role.status == 1:
                for menu in role.menus:
                    if menu.status == 1 and menu.id not in menu_ids:
                        menus.append(menu)
                        menu_ids.add(menu.id)
        return menus
    
    def get_role_codes(self):
        """获取用户角色编码列表"""
        return [role.code for role in self.roles if role.status == 1]
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nickname': self.nickname or self.username,
            'avatar': self.avatar,
            'roles': self.get_role_codes(),
            'status': self.status,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Requirement(db.Model):
    """需求文档模型"""
    __tablename__ = 'requirements'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False, comment='需求标题')
    content = db.Column(db.Text, nullable=False, comment='需求内容')
    module = db.Column(db.String(100), comment='所属模块')
    priority = db.Column(db.String(20), default='medium', comment='优先级: high/medium/low')
    status = db.Column(db.String(20), default='pending', comment='状态: pending/in_progress/completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联测试用例
    testcases = db.relationship('TestCase', backref='requirement', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'module': self.module,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'testcase_count': self.testcases.count()
        }


class TestCase(db.Model):
    """测试用例模型"""
    __tablename__ = 'testcases'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requirement_id = db.Column(db.Integer, db.ForeignKey('requirements.id'), nullable=True, comment='关联需求ID，可为空')
    title = db.Column(db.String(255), nullable=False, comment='用例标题')
    precondition = db.Column(db.Text, comment='前置条件')
    steps = db.Column(db.Text, nullable=False, comment='测试步骤')
    expected_result = db.Column(db.Text, nullable=False, comment='预期结果')
    case_type = db.Column(db.String(50), default='functional', comment='用例类型: functional/boundary/exception/performance')
    priority = db.Column(db.String(20), default='medium', comment='优先级: high/medium/low')
    status = db.Column(db.String(20), default='pending', comment='状态: pending/passed/failed/blocked')
    is_ai_generated = db.Column(db.Boolean, default=False, comment='是否AI生成')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'requirement_id': self.requirement_id,
            'requirement_title': self.requirement.title if self.requirement else None,
            'title': self.title,
            'precondition': self.precondition,
            'steps': self.steps,
            'expected_result': self.expected_result,
            'case_type': self.case_type,
            'priority': self.priority,
            'status': self.status,
            'is_ai_generated': self.is_ai_generated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Prompt(db.Model):
    """提示词模型"""
    __tablename__ = 'prompts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='提示词名称')
    content = db.Column(db.Text, nullable=False, comment='提示词内容')
    description = db.Column(db.String(500), comment='提示词描述')
    category = db.Column(db.String(50), default='general', comment='分类: general/functional/boundary/exception/performance')
    is_default = db.Column(db.Boolean, default=False, comment='是否默认提示词')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'description': self.description,
            'category': self.category,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Knowledge(db.Model):
    """知识库模型"""
    __tablename__ = 'knowledges'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='知识库名称')
    content = db.Column(db.Text, nullable=False, comment='知识库内容')
    description = db.Column(db.String(500), comment='知识库描述')
    category = db.Column(db.String(50), default='general', comment='分类: general/domain/api/ui/database')
    file_type = db.Column(db.String(20), default='text', comment='文件类型: text/markdown/json')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'description': self.description,
            'category': self.category,
            'file_type': self.file_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class LLMConfig(db.Model):
    """大模型配置模型"""
    __tablename__ = 'llm_configs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='配置名称')
    provider = db.Column(db.String(50), nullable=False, comment='供应商: openai/azure/anthropic/qwen/zhipu/moonshot/deepseek/ollama/custom')
    api_base = db.Column(db.String(500), nullable=False, comment='API基础URL')
    api_key = db.Column(db.String(500), nullable=False, comment='API密钥')
    model = db.Column(db.String(100), comment='模型名称')
    description = db.Column(db.String(500), comment='配置描述')
    is_default = db.Column(db.Boolean, default=False, comment='是否默认配置')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    extra_params = db.Column(db.Text, comment='额外参数JSON')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self, include_key=False):
        result = {
            'id': self.id,
            'name': self.name,
            'provider': self.provider,
            'api_base': self.api_base,
            'model': self.model,
            'description': self.description,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'extra_params': self.extra_params,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_key:
            # 只显示部分API密钥
            if self.api_key and len(self.api_key) > 8:
                result['api_key'] = self.api_key[:4] + '****' + self.api_key[-4:]
            else:
                result['api_key'] = '****'
        return result


class MCPConfig(db.Model):
    """MCP配置模型"""
    __tablename__ = 'mcp_configs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, comment='配置名称')
    server_url = db.Column(db.String(500), nullable=False, comment='MCP服务器地址')
    server_name = db.Column(db.String(100), comment='服务器名称')
    description = db.Column(db.String(500), comment='配置描述')
    timeout = db.Column(db.Integer, default=30, comment='超时时间(秒)')
    max_retries = db.Column(db.Integer, default=3, comment='最大重试次数')
    status = db.Column(db.Integer, default=1, comment='状态: 1启用 0禁用')
    is_default = db.Column(db.Boolean, default=False, comment='是否默认配置')
    extra_params = db.Column(db.Text, comment='额外参数JSON')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'server_url': self.server_url,
            'server_name': self.server_name,
            'description': self.description,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'status': self.status,
            'is_default': self.is_default,
            'extra_params': self.extra_params,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class OperationLog(db.Model):
    """操作日志模型"""
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='用户ID')
    username = db.Column(db.String(80), comment='用户名')
    action = db.Column(db.String(50), nullable=False, comment='操作类型: login/logout/create/update/delete/query/export')
    module = db.Column(db.String(50), nullable=False, comment='模块名称')
    description = db.Column(db.String(500), comment='操作描述')
    
    # 请求信息
    method = db.Column(db.String(10), comment='请求方法: GET/POST/PUT/DELETE')
    path = db.Column(db.String(500), comment='请求路径')
    params = db.Column(db.Text, comment='请求参数JSON')
    
    # 响应信息
    status_code = db.Column(db.Integer, comment='响应状态码')
    response_time = db.Column(db.Float, comment='响应时间(毫秒)')
    error_msg = db.Column(db.Text, comment='错误信息')
    
    # 客户端信息
    ip = db.Column(db.String(50), comment='IP地址')
    user_agent = db.Column(db.String(500), comment='User-Agent')
    browser = db.Column(db.String(100), comment='浏览器')
    browser_version = db.Column(db.String(50), comment='浏览器版本')
    os = db.Column(db.String(100), comment='操作系统')
    os_version = db.Column(db.String(50), comment='系统版本')
    device = db.Column(db.String(50), comment='设备类型: desktop/mobile/tablet')
    
    # 状态
    status = db.Column(db.String(20), default='success', comment='操作状态: success/fail/error')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间', index=True)
    
    # 关联用户
    user = db.relationship('User', backref=db.backref('operation_logs', lazy='dynamic'))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'module': self.module,
            'description': self.description,
            'method': self.method,
            'path': self.path,
            'params': self.params,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'error_msg': self.error_msg,
            'ip': self.ip,
            'user_agent': self.user_agent,
            'browser': self.browser,
            'browser_version': self.browser_version,
            'os': self.os,
            'os_version': self.os_version,
            'device': self.device,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
