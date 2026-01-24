"""
用户管理路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Role

users_bp = Blueprint('users', __name__)


def make_response(code=0, message='success', data=None):
    """统一响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    })


def admin_required(fn):
    """管理员权限装饰器"""
    from functools import wraps
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return make_response(401, '用户不存在')
        if 'admin' not in user.get_role_codes():
            return make_response(403, '没有管理员权限')
        return fn(*args, **kwargs)
    return wrapper


@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    
    query = User.query
    
    if keyword:
        query = query.filter(
            (User.username.like(f'%{keyword}%')) |
            (User.email.like(f'%{keyword}%')) |
            (User.nickname.like(f'%{keyword}%'))
        )
    if status:
        query = query.filter(User.status == status)
    
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    users_list = []
    for user in pagination.items:
        user_dict = user.to_dict()
        # 添加角色信息
        user_dict['roles'] = [role.to_dict() for role in user.roles]
        users_list.append(user_dict)
    
    return make_response(0, 'success', {
        'list': users_list,
        'total': pagination.total,
        'page': page,
        'pageSize': page_size
    })


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """获取用户详情"""
    user = User.query.get(user_id)
    if not user:
        return make_response(404, '用户不存在')
    
    user_dict = user.to_dict()
    user_dict['roles'] = [role.to_dict() for role in user.roles]
    return make_response(0, 'success', user_dict)


@users_bp.route('', methods=['POST'])
@admin_required
def create_user():
    """创建用户"""
    data = request.get_json()
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    nickname = data.get('nickname', '').strip()
    
    if not username or not email or not password:
        return make_response(400, '用户名、邮箱和密码不能为空')
    
    if len(username) < 3 or len(username) > 20:
        return make_response(400, '用户名长度应在3-20个字符之间')
    
    if len(password) < 6:
        return make_response(400, '密码长度不能少于6位')
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return make_response(400, '用户名已被注册')
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=email).first():
        return make_response(400, '邮箱已被注册')
    
    # 创建新用户
    user = User(
        username=username,
        email=email,
        nickname=nickname or username,
        status=data.get('status', 'active')
    )
    user.set_password(password)
    
    # 分配默认角色
    default_role = Role.query.filter_by(code='user').first()
    if default_role:
        user.roles.append(default_role)
    
    db.session.add(user)
    db.session.commit()
    
    user_dict = user.to_dict()
    user_dict['roles'] = [role.to_dict() for role in user.roles]
    
    return make_response(0, '创建成功', user_dict)


@users_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """更新用户"""
    user = User.query.get(user_id)
    if not user:
        return make_response(404, '用户不存在')
    
    data = request.get_json()
    
    # 更新允许修改的字段
    if 'email' in data:
        email = data['email'].strip()
        existing = User.query.filter(User.email == email, User.id != user_id).first()
        if existing:
            return make_response(400, '邮箱已被注册')
        user.email = email
    
    if 'nickname' in data:
        user.nickname = data['nickname'].strip()
    
    if 'status' in data:
        user.status = data['status']
    
    # 更新密码（如果提供）
    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            return make_response(400, '密码长度不能少于6位')
        user.set_password(data['password'])
    
    db.session.commit()
    
    user_dict = user.to_dict()
    user_dict['roles'] = [role.to_dict() for role in user.roles]
    
    return make_response(0, '更新成功', user_dict)


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """删除用户"""
    user = User.query.get(user_id)
    if not user:
        return make_response(404, '用户不存在')
    
    # 不允许删除admin用户
    if user.username == 'admin':
        return make_response(400, '系统用户不可删除')
    
    db.session.delete(user)
    db.session.commit()
    
    return make_response(0, '删除成功')


@users_bp.route('/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_password(user_id):
    """重置用户密码"""
    user = User.query.get(user_id)
    if not user:
        return make_response(404, '用户不存在')
    
    data = request.get_json()
    new_password = data.get('password', '').strip()
    
    if not new_password:
        return make_response(400, '请输入新密码')
    
    if len(new_password) < 6:
        return make_response(400, '密码长度不能少于6位')
    
    user.set_password(new_password)
    db.session.commit()
    
    return make_response(0, '密码重置成功')
