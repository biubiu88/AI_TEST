"""
数据库模型
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(120), unique=True, nullable=False, comment='邮箱')
    password_hash = db.Column(db.String(256), nullable=False, comment='密码哈希')
    nickname = db.Column(db.String(80), comment='昵称')
    avatar = db.Column(db.String(256), comment='头像')
    role = db.Column(db.String(20), default='user', comment='角色: admin/user')
    status = db.Column(db.String(20), default='active', comment='状态: active/inactive/banned')
    last_login = db.Column(db.DateTime, comment='最后登录时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nickname': self.nickname or self.username,
            'avatar': self.avatar,
            'role': self.role,
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
