"""
知识库管理路由
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Knowledge

knowledge_bp = Blueprint('knowledge', __name__)


@knowledge_bp.route('', methods=['GET'])
def get_knowledges():
    """获取知识库列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    is_active = request.args.get('is_active', '')
    
    query = Knowledge.query
    
    if keyword:
        query = query.filter(
            db.or_(
                Knowledge.name.contains(keyword),
                Knowledge.description.contains(keyword)
            )
        )
    if category:
        query = query.filter(Knowledge.category == category)
    if is_active:
        query = query.filter(Knowledge.is_active == (is_active == 'true'))
    
    query = query.order_by(Knowledge.created_at.desc())
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


@knowledge_bp.route('/all', methods=['GET'])
def get_all_knowledges():
    """获取所有启用的知识库（用于下拉选择）"""
    knowledges = Knowledge.query.filter(Knowledge.is_active == True).order_by(
        Knowledge.name
    ).all()
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': [item.to_dict() for item in knowledges]
    })


@knowledge_bp.route('/<int:knowledge_id>', methods=['GET'])
def get_knowledge(knowledge_id):
    """获取知识库详情"""
    knowledge = Knowledge.query.get_or_404(knowledge_id)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': knowledge.to_dict()
    })


@knowledge_bp.route('', methods=['POST'])
def create_knowledge():
    """创建知识库"""
    data = request.get_json()
    
    required_fields = ['name', 'content']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'code': 400, 'message': f'{field}不能为空'}), 400
    
    knowledge = Knowledge(
        name=data['name'],
        content=data['content'],
        description=data.get('description', ''),
        category=data.get('category', 'general'),
        file_type=data.get('file_type', 'text'),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(knowledge)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '创建成功',
        'data': knowledge.to_dict()
    })


@knowledge_bp.route('/<int:knowledge_id>', methods=['PUT'])
def update_knowledge(knowledge_id):
    """更新知识库"""
    knowledge = Knowledge.query.get_or_404(knowledge_id)
    data = request.get_json()
    
    if 'name' in data:
        knowledge.name = data['name']
    if 'content' in data:
        knowledge.content = data['content']
    if 'description' in data:
        knowledge.description = data['description']
    if 'category' in data:
        knowledge.category = data['category']
    if 'file_type' in data:
        knowledge.file_type = data['file_type']
    if 'is_active' in data:
        knowledge.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '更新成功',
        'data': knowledge.to_dict()
    })


@knowledge_bp.route('/<int:knowledge_id>', methods=['DELETE'])
def delete_knowledge(knowledge_id):
    """删除知识库"""
    knowledge = Knowledge.query.get_or_404(knowledge_id)
    
    db.session.delete(knowledge)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '删除成功'
    })


@knowledge_bp.route('/batch', methods=['GET'])
def get_knowledges_by_ids():
    """根据ID列表获取知识库内容"""
    ids_str = request.args.get('ids', '')
    if not ids_str:
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': []
        })
    
    ids = [int(id) for id in ids_str.split(',') if id.strip().isdigit()]
    knowledges = Knowledge.query.filter(
        Knowledge.id.in_(ids),
        Knowledge.is_active == True
    ).all()
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': [item.to_dict() for item in knowledges]
    })
