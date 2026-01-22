"""
用户认证路由
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


def make_response(code=0, message='success', data=None):
    """统一响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    })


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    # 验证必填字段
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirmPassword', '')
    
    if not username or not email or not password:
        return make_response(400, '用户名、邮箱和密码不能为空')
    
    if len(username) < 3 or len(username) > 20:
        return make_response(400, '用户名长度应在3-20个字符之间')
    
    if len(password) < 6:
        return make_response(400, '密码长度不能少于6位')
    
    if password != confirm_password:
        return make_response(400, '两次输入的密码不一致')
    
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
        nickname=data.get('nickname', username)
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return make_response(0, '注册成功', {'id': user.id, 'username': user.username})


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    account = data.get('account', '').strip()  # 可以是用户名或邮箱
    password = data.get('password', '')
    
    if not account or not password:
        return make_response(400, '账号和密码不能为空')
    
    # 通过用户名或邮箱查找用户
    user = User.query.filter(
        (User.username == account) | (User.email == account)
    ).first()
    
    if not user:
        return make_response(400, '用户不存在')
    
    if not user.check_password(password):
        return make_response(400, '密码错误')
    
    if user.status != 'active':
        return make_response(400, '账号已被禁用')
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # 创建JWT令牌
    access_token = create_access_token(
        identity=user.id,
        additional_claims={'username': user.username, 'role': user.role}
    )
    refresh_token = create_refresh_token(identity=user.id)
    
    return make_response(0, '登录成功', {
        'accessToken': access_token,
        'refreshToken': refresh_token,
        'user': user.to_dict()
    })


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return make_response(401, '用户不存在')
    
    access_token = create_access_token(
        identity=user.id,
        additional_claims={'username': user.username, 'role': user.role}
    )
    
    return make_response(0, '刷新成功', {'accessToken': access_token})


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取当前用户信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return make_response(401, '用户不存在')
    
    return make_response(0, 'success', user.to_dict())


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return make_response(401, '用户不存在')
    
    data = request.get_json()
    
    # 更新允许修改的字段
    if 'nickname' in data:
        user.nickname = data['nickname']
    if 'avatar' in data:
        user.avatar = data['avatar']
    
    db.session.commit()
    
    return make_response(0, '更新成功', user.to_dict())


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return make_response(401, '用户不存在')
    
    data = request.get_json()
    old_password = data.get('oldPassword', '')
    new_password = data.get('newPassword', '')
    confirm_password = data.get('confirmPassword', '')
    
    if not old_password or not new_password:
        return make_response(400, '请填写完整信息')
    
    if not user.check_password(old_password):
        return make_response(400, '原密码错误')
    
    if len(new_password) < 6:
        return make_response(400, '新密码长度不能少于6位')
    
    if new_password != confirm_password:
        return make_response(400, '两次输入的新密码不一致')
    
    user.set_password(new_password)
    db.session.commit()
    
    return make_response(0, '密码修改成功')


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码（通过邮箱）"""
    data = request.get_json()
    
    email = data.get('email', '').strip()
    new_password = data.get('newPassword', '')
    confirm_password = data.get('confirmPassword', '')
    
    if not email:
        return make_response(400, '请输入邮箱')
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return make_response(400, '该邮箱未注册')
    
    if not new_password:
        return make_response(400, '请输入新密码')
    
    if len(new_password) < 6:
        return make_response(400, '密码长度不能少于6位')
    
    if new_password != confirm_password:
        return make_response(400, '两次输入的密码不一致')
    
    user.set_password(new_password)
    db.session.commit()
    
    return make_response(0, '密码重置成功，请使用新密码登录')


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    # JWT是无状态的，这里可以实现黑名单机制
    # 简单实现：前端清除token即可
    return make_response(0, '登出成功')
