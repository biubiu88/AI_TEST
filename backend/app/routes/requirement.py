"""
需求文档路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Requirement
from app.middlewares import log_operation

requirement_bp = Blueprint('requirement', __name__)


@requirement_bp.route('', methods=['GET'])
@jwt_required()
@log_operation
def get_requirements():
    """获取需求列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '')
    module = request.args.get('module', '')
    status = request.args.get('status', '')
    
    query = Requirement.query
    
    if keyword:
        query = query.filter(
            db.or_(
                Requirement.title.contains(keyword),
                Requirement.content.contains(keyword)
            )
        )
    if module:
        query = query.filter(Requirement.module == module)
    if status:
        query = query.filter(Requirement.status == status)
    
    query = query.order_by(Requirement.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {
            'list': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


@requirement_bp.route('/<int:requirement_id>', methods=['GET'])
@jwt_required()
@log_operation
def get_requirement(requirement_id):
    """获取需求详情"""
    requirement = Requirement.query.get_or_404(requirement_id)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': requirement.to_dict()
    })


@requirement_bp.route('', methods=['POST'])
@jwt_required()
@log_operation
def create_requirement():
    """创建需求"""
    data = request.get_json()
    
    if not data.get('title') or not data.get('content'):
        return jsonify({'code': 400, 'message': '标题和内容不能为空'}), 400
    
    requirement = Requirement(
        title=data['title'],
        content=data['content'],
        module=data.get('module', ''),
        priority=data.get('priority', 'medium'),
        status=data.get('status', 'pending')
    )
    
    db.session.add(requirement)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '创建成功',
        'data': requirement.to_dict()
    })


@requirement_bp.route('/<int:requirement_id>', methods=['PUT'])
@jwt_required()
@log_operation
def update_requirement(requirement_id):
    """更新需求"""
    requirement = Requirement.query.get_or_404(requirement_id)
    data = request.get_json()
    
    if 'title' in data:
        requirement.title = data['title']
    if 'content' in data:
        requirement.content = data['content']
    if 'module' in data:
        requirement.module = data['module']
    if 'priority' in data:
        requirement.priority = data['priority']
    if 'status' in data:
        requirement.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '更新成功',
        'data': requirement.to_dict()
    })


@requirement_bp.route('/<int:requirement_id>', methods=['DELETE'])
@jwt_required()
@log_operation
def delete_requirement(requirement_id):
    """删除需求"""
    requirement = Requirement.query.get_or_404(requirement_id)
    db.session.delete(requirement)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '删除成功'
    })


@requirement_bp.route('/modules', methods=['GET'])
@jwt_required()
@log_operation
def get_modules():
    """获取所有模块"""
    modules = db.session.query(Requirement.module).distinct().filter(
        Requirement.module.isnot(None),
        Requirement.module != ''
    ).all()
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': [m[0] for m in modules]
    })
