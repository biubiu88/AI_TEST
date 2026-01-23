"""
大模型配置路由
"""
from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import LLMConfig

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

llm_config_bp = Blueprint('llm_config', __name__)

# 主流大模型供应商配置
PROVIDERS = {
    'openai': {
        'name': 'OpenAI',
        'api_base': 'https://api.openai.com/v1',
        'models_endpoint': '/models',
        'description': 'OpenAI GPT系列模型'
    },
    'azure': {
        'name': 'Azure OpenAI',
        'api_base': 'https://{resource}.openai.azure.com',
        'description': '微软Azure托管的OpenAI服务'
    },
    'anthropic': {
        'name': 'Anthropic Claude',
        'api_base': 'https://api.anthropic.com/v1',
        'description': 'Claude系列模型'
    },
    'qwen': {
        'name': '通义千问',
        'api_base': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'description': '阿里云通义千问大模型'
    },
    'zhipu': {
        'name': '智谱AI',
        'api_base': 'https://open.bigmodel.cn/api/paas/v4',
        'description': '智谱GLM系列模型'
    },
    'moonshot': {
        'name': 'Moonshot',
        'api_base': 'https://api.moonshot.cn/v1',
        'description': 'Moonshot Kimi大模型'
    },
    'deepseek': {
        'name': 'DeepSeek',
        'api_base': 'https://api.deepseek.com/v1',
        'description': 'DeepSeek大模型'
    },
    'doubao': {
        'name': '豆包(字节)',
        'api_base': 'https://ark.cn-beijing.volces.com/api/v3',
        'description': '字节跳动豆包大模型'
    },
    'baichuan': {
        'name': '百川',
        'api_base': 'https://api.baichuan-ai.com/v1',
        'description': '百川大模型'
    },
    'minimax': {
        'name': 'MiniMax',
        'api_base': 'https://api.minimax.chat/v1',
        'description': 'MiniMax大模型'
    },
    'ollama': {
        'name': 'Ollama(本地)',
        'api_base': 'http://localhost:11434/v1',
        'description': '本地部署的Ollama服务'
    },
    'custom': {
        'name': '自定义',
        'api_base': '',
        'description': '自定义OpenAI兼容接口'
    }
}


@llm_config_bp.route('', methods=['GET'])
def get_llm_configs():
    """获取大模型配置列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    is_active = request.args.get('is_active', None)
    
    query = LLMConfig.query
    
    if is_active is not None:
        query = query.filter(LLMConfig.is_active == (is_active.lower() == 'true'))
    
    pagination = query.order_by(LLMConfig.is_default.desc(), LLMConfig.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': {
            'items': [c.to_dict(include_key=True) for c in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }
    })


@llm_config_bp.route('/all', methods=['GET'])
def get_all_llm_configs():
    """获取所有启用的大模型配置（用于下拉选择）"""
    configs = LLMConfig.query.filter(
        LLMConfig.is_active == True
    ).order_by(LLMConfig.is_default.desc(), LLMConfig.name).all()
    
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': [c.to_dict() for c in configs]
    })


@llm_config_bp.route('/providers', methods=['GET'])
def get_providers():
    """获取支持的大模型供应商列表"""
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': PROVIDERS
    })


@llm_config_bp.route('/<int:id>', methods=['GET'])
def get_llm_config(id):
    """获取单个大模型配置"""
    config = LLMConfig.query.get_or_404(id)
    return jsonify({
        'code': 0,
        'message': 'success',
        'data': config.to_dict(include_key=True)
    })


@llm_config_bp.route('', methods=['POST'])
def create_llm_config():
    """创建大模型配置"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['name', 'provider', 'api_base', 'api_key']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'code': 400, 'message': f'{field} 不能为空'}), 400
    
    # 验证供应商
    if data['provider'] not in PROVIDERS and data['provider'] != 'custom':
        return jsonify({'code': 400, 'message': '不支持的供应商类型'}), 400
    
    config = LLMConfig(
        name=data['name'],
        provider=data['provider'],
        api_base=data['api_base'].rstrip('/'),
        api_key=data['api_key'],
        model=data.get('model', ''),
        description=data.get('description', ''),
        is_default=data.get('is_default', False),
        is_active=data.get('is_active', True),
        extra_params=data.get('extra_params')
    )
    
    # 如果设置为默认，取消其他默认配置
    if config.is_default:
        LLMConfig.query.filter(LLMConfig.is_default == True).update({'is_default': False})
    
    db.session.add(config)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '创建成功',
        'data': config.to_dict(include_key=True)
    })


@llm_config_bp.route('/<int:id>', methods=['PUT'])
def update_llm_config(id):
    """更新大模型配置"""
    config = LLMConfig.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        config.name = data['name']
    if 'provider' in data:
        config.provider = data['provider']
    if 'api_base' in data:
        config.api_base = data['api_base'].rstrip('/')
    if 'api_key' in data and data['api_key']:
        # 只有传入了新的API key才更新
        config.api_key = data['api_key']
    if 'model' in data:
        config.model = data['model']
    if 'description' in data:
        config.description = data['description']
    if 'is_active' in data:
        config.is_active = data['is_active']
    if 'extra_params' in data:
        config.extra_params = data['extra_params']
    
    # 处理默认配置
    if data.get('is_default'):
        # 取消其他默认配置
        LLMConfig.query.filter(
            LLMConfig.id != id,
            LLMConfig.is_default == True
        ).update({'is_default': False})
        config.is_default = True
    elif 'is_default' in data:
        config.is_default = data['is_default']
    
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '更新成功',
        'data': config.to_dict(include_key=True)
    })


@llm_config_bp.route('/<int:id>', methods=['DELETE'])
def delete_llm_config(id):
    """删除大模型配置"""
    config = LLMConfig.query.get_or_404(id)
    db.session.delete(config)
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '删除成功'
    })


@llm_config_bp.route('/<int:id>/default', methods=['PUT'])
def set_default_config(id):
    """设置为默认配置"""
    config = LLMConfig.query.get_or_404(id)
    
    # 取消其他默认配置
    LLMConfig.query.filter(LLMConfig.is_default == True).update({'is_default': False})
    
    config.is_default = True
    db.session.commit()
    
    return jsonify({
        'code': 0,
        'message': '设置成功',
        'data': config.to_dict()
    })


@llm_config_bp.route('/models', methods=['POST'])
def fetch_models():
    """根据配置获取可用模型列表"""
    data = request.get_json()
    api_base = data.get('api_base', '').rstrip('/')
    api_key = data.get('api_key', '')
    
    if not api_base or not api_key:
        return jsonify({'code': 400, 'message': '请提供API地址和密钥'}), 400
    
    if not OPENAI_AVAILABLE:
        return jsonify({'code': 500, 'message': 'OpenAI库未安装'}), 500
    
    try:
        client = OpenAI(api_key=api_key, base_url=api_base)
        models_response = client.models.list()
        
        # 提取模型ID列表
        models = []
        for model in models_response.data:
            model_id = model.id
            # 过滤一些常用的聊天模型
            models.append({
                'id': model_id,
                'name': model_id
            })
        
        # 按名称排序
        models.sort(key=lambda x: x['name'])
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': models
        })
    except Exception as e:
        current_app.logger.error(f'获取模型列表失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'获取模型列表失败: {str(e)}'
        }), 500


@llm_config_bp.route('/test', methods=['POST'])
def test_config():
    """测试大模型配置连接"""
    data = request.get_json()
    api_base = data.get('api_base', '').rstrip('/')
    api_key = data.get('api_key', '')
    model = data.get('model', '')
    
    if not api_base or not api_key:
        return jsonify({'code': 400, 'message': '请提供API地址和密钥'}), 400
    
    if not OPENAI_AVAILABLE:
        return jsonify({'code': 500, 'message': 'OpenAI库未安装'}), 500
    
    try:
        client = OpenAI(api_key=api_key, base_url=api_base)
        
        # 尝试调用模型
        test_model = model if model else 'gpt-3.5-turbo'
        response = client.chat.completions.create(
            model=test_model,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        return jsonify({
            'code': 0,
            'message': '连接测试成功',
            'data': {
                'model': response.model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens
                }
            }
        })
    except Exception as e:
        current_app.logger.error(f'测试连接失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': f'连接测试失败: {str(e)}'
        }), 500
