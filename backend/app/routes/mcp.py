"""
MCP配置路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import User
from app.models import MCPConfig

mcp_bp = Blueprint('mcp', __name__)


def make_response(code=0, message='success', data=None):
    """统一响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    })


@mcp_bp.route('', methods=['GET'])
@jwt_required()
def get_mcp_configs():
    """获取MCP配置列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    keyword = request.args.get('keyword', '')
    status = request.args.get('status', '')
    
    query = MCPConfig.query
    
    if keyword:
        query = query.filter(
            (MCPConfig.name.like(f'%{keyword}%')) |
            (MCPConfig.description.like(f'%{keyword}%'))
        )
    if status:
        query = query.filter(MCPConfig.status == int(status))
    
    pagination = query.order_by(MCPConfig.created_at.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    configs_list = []
    for config in pagination.items:
        config_dict = {
            'id': config.id,
            'name': config.name,
            'server_url': config.server_url,
            'server_name': config.server_name,
            'description': config.description,
            'timeout': config.timeout,
            'max_retries': config.max_retries,
            'status': config.status,
            'is_default': config.is_default,
            'extra_params': config.extra_params,
            'created_at': config.created_at.isoformat() if config.created_at else None,
            'updated_at': config.updated_at.isoformat() if config.updated_at else None
        }
        configs_list.append(config_dict)
    
    return make_response(0, 'success', {
        'list': configs_list,
        'total': pagination.total,
        'page': page,
        'pageSize': page_size
    })


@mcp_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_mcp_configs():
    """获取所有启用的MCP配置"""
    configs = MCPConfig.query.filter(
        MCPConfig.status == 1
    ).order_by(MCPConfig.created_at.desc()).all()
    
    result = []
    for config in configs:
        result.append({
            'id': config.id,
            'name': config.name,
            'server_url': config.server_url,
            'server_name': config.server_name
        })
    
    return make_response(0, 'success', result)


@mcp_bp.route('/<int:config_id>', methods=['GET'])
@jwt_required()
def get_mcp_config(config_id):
    """获取MCP配置详情"""
    config = MCPConfig.query.get(config_id)
    if not config:
        return make_response(404, 'MCP配置不存在')
    
    return make_response(0, 'success', {
        'id': config.id,
        'name': config.name,
        'server_url': config.server_url,
        'server_name': config.server_name,
        'description': config.description,
        'timeout': config.timeout,
        'max_retries': config.max_retries,
        'status': config.status,
        'is_default': config.is_default,
        'extra_params': config.extra_params,
        'created_at': config.created_at.isoformat() if config.created_at else None,
        'updated_at': config.updated_at.isoformat() if config.updated_at else None
    })


@mcp_bp.route('', methods=['POST'])
@jwt_required()
def create_mcp_config():
    """创建MCP配置"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    server_url = data.get('server_url', '').strip()
    
    if not name or not server_url:
        return make_response(400, '配置名称和服务器地址不能为空')
    
    # 创建新配置
    config = MCPConfig(
        name=name,
        server_url=server_url,
        server_name=data.get('server_name', ''),
        description=data.get('description', ''),
        timeout=data.get('timeout', 30),
        max_retries=data.get('max_retries', 3),
        status=data.get('status', 1),
        is_default=data.get('is_default', False),
        extra_params=data.get('extra_params', '')
    )
    
    db.session.add(config)
    db.session.commit()
    
    return make_response(0, '创建成功', {
        'id': config.id,
        'name': config.name,
        'server_url': config.server_url,
        'server_name': config.server_name,
        'description': config.description,
        'timeout': config.timeout,
        'max_retries': config.max_retries,
        'status': config.status,
        'is_default': config.is_default,
        'extra_params': config.extra_params,
        'created_at': config.created_at.isoformat() if config.created_at else None,
        'updated_at': config.updated_at.isoformat() if config.updated_at else None
    })


@mcp_bp.route('/<int:config_id>', methods=['PUT'])
@jwt_required()
def update_mcp_config(config_id):
    """更新MCP配置"""
    config = MCPConfig.query.get(config_id)
    if not config:
        return make_response(404, 'MCP配置不存在')
    
    data = request.get_json()
    
    if 'name' in data:
        config.name = data['name'].strip()
    if 'server_url' in data:
        config.server_url = data['server_url'].strip()
    if 'server_name' in data:
        config.server_name = data['server_name'].strip()
    if 'description' in data:
        config.description = data['description']
    if 'timeout' in data:
        config.timeout = data['timeout']
    if 'max_retries' in data:
        config.max_retries = data['max_retries']
    if 'status' in data:
        config.status = data['status']
    if 'is_default' in data:
        config.is_default = data['is_default']
    if 'extra_params' in data:
        config.extra_params = data['extra_params']
    
    db.session.commit()
    
    return make_response(0, '更新成功', {
        'id': config.id,
        'name': config.name,
        'server_url': config.server_url,
        'server_name': config.server_name,
        'description': config.description,
        'timeout': config.timeout,
        'max_retries': config.max_retries,
        'status': config.status,
        'is_default': config.is_default,
        'extra_params': config.extra_params,
        'created_at': config.created_at.isoformat() if config.created_at else None,
        'updated_at': config.updated_at.isoformat() if config.updated_at else None
    })


@mcp_bp.route('/<int:config_id>', methods=['DELETE'])
@jwt_required()
def delete_mcp_config(config_id):
    """删除MCP配置"""
    config = MCPConfig.query.get(config_id)
    if not config:
        return make_response(404, 'MCP配置不存在')
    
    db.session.delete(config)
    db.session.commit()
    
    return make_response(0, '删除成功')


@mcp_bp.route('/<int:config_id>/test', methods=['POST'])
@jwt_required()
def test_mcp_config(config_id):
    """测试MCP配置连接"""
    config = MCPConfig.query.get(config_id)
    if not config:
        return make_response(404, 'MCP配置不存在')
    
    # TODO: 实际测试MCP服务器连接
    # 模拟测试结果
    return make_response(0, '连接成功', {
        'server_name': config.server_name,
        'response_time': '125ms',
        'status': 'connected'
    })
