"""
权限管理路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Role, Permission, Menu, User
from app.middlewares import log_operation

permission_bp = Blueprint('permission', __name__)


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


# ============ 角色管理 ============

@permission_bp.route('/roles', methods=['GET'])
@jwt_required()
@log_operation
def get_roles():
    """获取角色列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    name = request.args.get('name', '')
    status = request.args.get('status', type=int)
    
    query = Role.query
    
    if name:
        query = query.filter(Role.name.like(f'%{name}%'))
    if status is not None:
        query = query.filter(Role.status == status)
    
    query = query.order_by(Role.sort.asc(), Role.id.asc())
    
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    return make_response(0, 'success', {
        'list': [role.to_dict() for role in pagination.items],
        'total': pagination.total,
        'page': page,
        'pageSize': page_size
    })


@permission_bp.route('/roles/all', methods=['GET'])
@jwt_required()
@log_operation
def get_all_roles():
    """获取所有启用的角色"""
    roles = Role.query.filter(Role.status == 1).order_by(Role.sort.asc()).all()
    return make_response(0, 'success', [role.to_dict() for role in roles])


@permission_bp.route('/roles/<int:role_id>', methods=['GET'])
@jwt_required()
@log_operation
def get_role(role_id):
    """获取角色详情"""
    role = Role.query.get(role_id)
    if not role:
        return make_response(404, '角色不存在')
    return make_response(0, 'success', role.to_dict())


@permission_bp.route('/roles', methods=['POST'])
@admin_required
@log_operation
def create_role():
    """创建角色"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    code = data.get('code', '').strip()
    
    if not name or not code:
        return make_response(400, '角色名称和编码不能为空')
    
    if Role.query.filter_by(name=name).first():
        return make_response(400, '角色名称已存在')
    
    if Role.query.filter_by(code=code).first():
        return make_response(400, '角色编码已存在')
    
    role = Role(
        name=name,
        code=code,
        description=data.get('description', ''),
        status=data.get('status', 1),
        sort=data.get('sort', 0)
    )
    
    # 设置权限
    permission_ids = data.get('permissions', [])
    if permission_ids:
        permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
        role.permissions = permissions
    
    # 设置菜单
    menu_ids = data.get('menus', [])
    if menu_ids:
        menus = Menu.query.filter(Menu.id.in_(menu_ids)).all()
        role.menus = menus
    
    db.session.add(role)
    db.session.commit()
    
    return make_response(0, '创建成功', role.to_dict())


@permission_bp.route('/roles/<int:role_id>', methods=['PUT'])
@admin_required
@log_operation
def update_role(role_id):
    """更新角色"""
    role = Role.query.get(role_id)
    if not role:
        return make_response(404, '角色不存在')
    
    # admin角色不可修改编码
    if role.code == 'admin' and role_id == 1:
        data = request.get_json()
        if data.get('code') and data.get('code') != 'admin':
            return make_response(400, '超级管理员角色编码不可修改')
    
    data = request.get_json()
    
    if 'name' in data:
        name = data['name'].strip()
        existing = Role.query.filter(Role.name == name, Role.id != role_id).first()
        if existing:
            return make_response(400, '角色名称已存在')
        role.name = name
    
    if 'code' in data:
        code = data['code'].strip()
        existing = Role.query.filter(Role.code == code, Role.id != role_id).first()
        if existing:
            return make_response(400, '角色编码已存在')
        role.code = code
    
    if 'description' in data:
        role.description = data['description']
    if 'status' in data:
        role.status = data['status']
    if 'sort' in data:
        role.sort = data['sort']
    
    # 更新权限
    if 'permissions' in data:
        permission_ids = data['permissions']
        permissions = Permission.query.filter(Permission.id.in_(permission_ids)).all()
        role.permissions = permissions
    
    # 更新菜单
    if 'menus' in data:
        menu_ids = data['menus']
        menus = Menu.query.filter(Menu.id.in_(menu_ids)).all()
        role.menus = menus
    
    db.session.commit()
    
    return make_response(0, '更新成功', role.to_dict())


@permission_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@admin_required
@log_operation
def delete_role(role_id):
    """删除角色"""
    role = Role.query.get(role_id)
    if not role:
        return make_response(404, '角色不存在')
    
    if role.code == 'admin':
        return make_response(400, '系统角色不可删除')
    
    db.session.delete(role)
    db.session.commit()
    
    return make_response(0, '删除成功')


# ============ 权限管理 ============

@permission_bp.route('/permissions', methods=['GET'])
@jwt_required()
@log_operation
def get_permissions():
    """获取权限列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    name = request.args.get('name', '')
    type_ = request.args.get('type', '')
    
    query = Permission.query
    
    if name:
        query = query.filter(Permission.name.like(f'%{name}%'))
    if type_:
        query = query.filter(Permission.type == type_)
    
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)
    
    return make_response(0, 'success', {
        'list': [perm.to_dict() for perm in pagination.items],
        'total': pagination.total,
        'page': page,
        'pageSize': page_size
    })


@permission_bp.route('/permissions/all', methods=['GET'])
@jwt_required()
@log_operation
def get_all_permissions():
    """获取所有权限"""
    permissions = Permission.query.all()
    return make_response(0, 'success', [perm.to_dict() for perm in permissions])


@permission_bp.route('/permissions', methods=['POST'])
@admin_required
@log_operation
def create_permission():
    """创建权限"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    code = data.get('code', '').strip()
    
    if not name or not code:
        return make_response(400, '权限名称和编码不能为空')
    
    if Permission.query.filter_by(code=code).first():
        return make_response(400, '权限编码已存在')
    
    permission = Permission(
        name=name,
        code=code,
        type=data.get('type', 'button'),
        description=data.get('description', '')
    )
    
    db.session.add(permission)
    db.session.commit()
    
    return make_response(0, '创建成功', permission.to_dict())


@permission_bp.route('/permissions/<int:perm_id>', methods=['PUT'])
@admin_required
@log_operation
def update_permission(perm_id):
    """更新权限"""
    permission = Permission.query.get(perm_id)
    if not permission:
        return make_response(404, '权限不存在')
    
    data = request.get_json()
    
    if 'name' in data:
        permission.name = data['name'].strip()
    if 'code' in data:
        code = data['code'].strip()
        existing = Permission.query.filter(Permission.code == code, Permission.id != perm_id).first()
        if existing:
            return make_response(400, '权限编码已存在')
        permission.code = code
    if 'type' in data:
        permission.type = data['type']
    if 'description' in data:
        permission.description = data['description']
    
    db.session.commit()
    
    return make_response(0, '更新成功', permission.to_dict())


@permission_bp.route('/permissions/<int:perm_id>', methods=['DELETE'])
@admin_required
@log_operation
def delete_permission(perm_id):
    """删除权限"""
    permission = Permission.query.get(perm_id)
    if not permission:
        return make_response(404, '权限不存在')
    
    db.session.delete(permission)
    db.session.commit()
    
    return make_response(0, '删除成功')


# ============ 菜单管理 ============

@permission_bp.route('/menus', methods=['GET'])
@jwt_required()
@log_operation
def get_menus():
    """获取菜单列表（树形结构）"""
    menus = Menu.query.filter(Menu.status == 1).order_by(Menu.sort.asc()).all()
    tree = Menu.build_tree(menus)
    return make_response(0, 'success', tree)


@permission_bp.route('/menus/all', methods=['GET'])
@jwt_required()
@log_operation
def get_all_menus():
    """获取所有菜单（平铺）"""
    menus = Menu.query.order_by(Menu.sort.asc()).all()
    return make_response(0, 'success', [menu.to_dict() for menu in menus])


@permission_bp.route('/menus/<int:menu_id>', methods=['GET'])
@jwt_required()
@log_operation
def get_menu(menu_id):
    """获取菜单详情"""
    menu = Menu.query.get(menu_id)
    if not menu:
        return make_response(404, '菜单不存在')
    return make_response(0, 'success', menu.to_dict())


@permission_bp.route('/menus', methods=['POST'])
@admin_required
@log_operation
def create_menu():
    """创建菜单"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    if not name:
        return make_response(400, '菜单名称不能为空')
    
    menu = Menu(
        parent_id=data.get('parentId', 0),
        name=name,
        path=data.get('path', ''),
        component=data.get('component', ''),
        redirect=data.get('redirect', ''),
        icon=data.get('icon', ''),
        title=data.get('title', name),
        hidden=data.get('hidden', False),
        always_show=data.get('alwaysShow', False),
        keep_alive=data.get('keepAlive', False),
        sort=data.get('sort', 0),
        type=data.get('type', 'menu'),
        permission=data.get('permission', ''),
        status=data.get('status', 1)
    )
    
    db.session.add(menu)
    db.session.commit()
    
    return make_response(0, '创建成功', menu.to_dict())


@permission_bp.route('/menus/<int:menu_id>', methods=['PUT'])
@admin_required
@log_operation
def update_menu(menu_id):
    """更新菜单"""
    menu = Menu.query.get(menu_id)
    if not menu:
        return make_response(404, '菜单不存在')
    
    data = request.get_json()
    
    if 'parentId' in data:
        menu.parent_id = data['parentId']
    if 'name' in data:
        menu.name = data['name'].strip()
    if 'path' in data:
        menu.path = data['path']
    if 'component' in data:
        menu.component = data['component']
    if 'redirect' in data:
        menu.redirect = data['redirect']
    if 'icon' in data:
        menu.icon = data['icon']
    if 'title' in data:
        menu.title = data['title']
    if 'hidden' in data:
        menu.hidden = data['hidden']
    if 'alwaysShow' in data:
        menu.always_show = data['alwaysShow']
    if 'keepAlive' in data:
        menu.keep_alive = data['keepAlive']
    if 'sort' in data:
        menu.sort = data['sort']
    if 'type' in data:
        menu.type = data['type']
    if 'permission' in data:
        menu.permission = data['permission']
    if 'status' in data:
        menu.status = data['status']
    
    db.session.commit()
    
    return make_response(0, '更新成功', menu.to_dict())


@permission_bp.route('/menus/<int:menu_id>', methods=['DELETE'])
@admin_required
@log_operation
def delete_menu(menu_id):
    """删除菜单"""
    menu = Menu.query.get(menu_id)
    if not menu:
        return make_response(404, '菜单不存在')
    
    # 检查是否有子菜单
    children = Menu.query.filter_by(parent_id=menu_id).first()
    if children:
        return make_response(400, '请先删除子菜单')
    
    db.session.delete(menu)
    db.session.commit()
    
    return make_response(0, '删除成功')


# ============ 用户角色管理 ============

@permission_bp.route('/users/<int:user_id>/roles', methods=['GET'])
@admin_required
@log_operation
def get_user_roles(user_id):
    """获取用户角色"""
    user = User.query.get(user_id)
    if not user:
        return make_response(404, '用户不存在')
    return make_response(0, 'success', [role.to_dict() for role in user.roles])


@permission_bp.route('/users/<int:user_id>/roles', methods=['PUT'])
@admin_required
@log_operation
def set_user_roles(user_id):
    """设置用户角色"""
    user = User.query.get(user_id)
    if not user:
        return make_response(404, '用户不存在')
    
    data = request.get_json()
    role_ids = data.get('roleIds', [])
    
    roles = Role.query.filter(Role.id.in_(role_ids)).all()
    user.roles = roles
    
    db.session.commit()
    
    return make_response(0, '设置成功', [role.to_dict() for role in user.roles])


# ============ 获取当前用户菜单和权限 ============

@permission_bp.route('/user/menus', methods=['GET'])
@jwt_required()
@log_operation
def get_user_menus():
    """获取当前用户的菜单"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return make_response(401, '用户不存在')
    
    # admin用户返回所有菜单
    if 'admin' in user.get_role_codes():
        menus = Menu.query.filter(Menu.status == 1).order_by(Menu.sort.asc()).all()
    else:
        menus = user.get_menus()
    
    tree = Menu.build_tree(menus)
    return make_response(0, 'success', tree)


@permission_bp.route('/user/permissions', methods=['GET'])
@jwt_required()
@log_operation
def get_user_permissions():
    """获取当前用户的权限"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return make_response(401, '用户不存在')
    
    # admin用户返回所有权限
    if 'admin' in user.get_role_codes():
        permissions = [p.code for p in Permission.query.all()]
    else:
        permissions = user.get_permissions()
    
    return make_response(0, 'success', permissions)
