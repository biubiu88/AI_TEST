"""
提示词管理路由
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models import Prompt

prompt_bp = Blueprint('prompt', __name__)


@prompt_bp.route('', methods=['GET'])
def get_prompts():
    """获取提示词列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    is_active = request.args.get('is_active', '')
    
    query = Prompt.query
    
    if keyword:
        query = query.filter(
            db.or_(
                Prompt.name.contains(keyword),
                Prompt.description.contains(keyword)
            )
        )
    if category:
        query = query.filter(Prompt.category == category)
    if is_active:
        query = query.filter(Prompt.is_active == (is_active == 'true'))
    
    query = query.order_by(Prompt.is_default.desc(), Prompt.created_at.desc())
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


@prompt_bp.route('/all', methods=['GET'])
def get_all_prompts():
    """获取所有启用的提示词（用于下拉选择）"""
    prompts = Prompt.query.filter(Prompt.is_active == True).order_by(
        Prompt.is_default.desc(), Prompt.name
    ).all()
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': [item.to_dict() for item in prompts]
    })


@prompt_bp.route('/<int:prompt_id>', methods=['GET'])
def get_prompt(prompt_id):
    """获取提示词详情"""
    prompt = Prompt.query.get_or_404(prompt_id)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': prompt.to_dict()
    })


@prompt_bp.route('', methods=['POST'])
def create_prompt():
    """创建提示词"""
    data = request.get_json()
    
    required_fields = ['name', 'content']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'code': 400, 'message': f'{field}不能为空'}), 400
    
    # 如果设置为默认，先取消其他默认
    if data.get('is_default'):
        Prompt.query.filter(Prompt.is_default == True).update({'is_default': False})
    
    prompt = Prompt(
        name=data['name'],
        content=data['content'],
        description=data.get('description', ''),
        category=data.get('category', 'general'),
        is_default=data.get('is_default', False),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(prompt)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '创建成功',
        'data': prompt.to_dict()
    })


@prompt_bp.route('/<int:prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    """更新提示词"""
    prompt = Prompt.query.get_or_404(prompt_id)
    data = request.get_json()
    
    # 如果设置为默认，先取消其他默认
    if data.get('is_default') and not prompt.is_default:
        Prompt.query.filter(Prompt.id != prompt_id, Prompt.is_default == True).update({'is_default': False})
    
    if 'name' in data:
        prompt.name = data['name']
    if 'content' in data:
        prompt.content = data['content']
    if 'description' in data:
        prompt.description = data['description']
    if 'category' in data:
        prompt.category = data['category']
    if 'is_default' in data:
        prompt.is_default = data['is_default']
    if 'is_active' in data:
        prompt.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '更新成功',
        'data': prompt.to_dict()
    })


@prompt_bp.route('/<int:prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    """删除提示词"""
    prompt = Prompt.query.get_or_404(prompt_id)
    
    db.session.delete(prompt)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '删除成功'
    })


@prompt_bp.route('/<int:prompt_id>/default', methods=['PUT'])
def set_default_prompt(prompt_id):
    """设置默认提示词"""
    prompt = Prompt.query.get_or_404(prompt_id)
    
    # 取消其他默认
    Prompt.query.filter(Prompt.is_default == True).update({'is_default': False})
    
    # 设置当前为默认
    prompt.is_default = True
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '设置成功',
        'data': prompt.to_dict()
    })
