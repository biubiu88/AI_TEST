"""
AI助手路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import User, Prompt, Knowledge, LLMConfig, MCPConfig
from app.services.ai_service import AIService
from app.services.llm_clients import ChatMessage

ai_assistant_bp = Blueprint('ai_assistant', __name__)


def make_response(code=0, message='success', data=None):
    """统一响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    })


# 模拟AI会话数据
mock_sessions = [
    {
        'id': 1,
        'user_id': 1,
        'session_name': '测试用例生成讨论',
        'session_type': 'chat',
        'model_id': None,
        'prompt_id': None,
        'knowledge_ids': None,
        'mcp_config_id': None,
        'status': 'active',
        'created_at': '2024-01-24 17:00:00',
        'updated_at': '2024-01-24 17:30:00'
    },
    {
        'id': 2,
        'user_id': 1,
        'session_name': '需求分析',
        'session_type': 'analysis',
        'model_id': None,
        'prompt_id': None,
        'knowledge_ids': None,
        'mcp_config_id': None,
        'status': 'active',
        'created_at': '2024-01-24 17:15:00',
        'updated_at': '2024-01-24 17:20:00'
    }
]

# 模拟AI消息数据
mock_messages = {
    1: [
        {
            'id': 1,
            'session_id': 1,
            'role': 'user',
            'content': '你好，请帮我生成一个用户登录功能的测试用例',
            'message_type': 'text',
            'metadata': None,
            'token_count': 20,
            'created_at': '2024-01-24 17:00:10'
        },
        {
            'id': 2,
            'session_id': 1,
            'role': 'assistant',
            'content': '好的，我来帮你生成用户登录功能的测试用例。首先，我需要了解一些信息：\n\n1. 登录方式有哪些？（用户名/邮箱/手机号）\n2. 是否需要验证码？\n3. 是否有密码找回功能？\n4. 是否支持第三方登录？',
            'message_type': 'text',
            'metadata': None,
            'token_count': 85,
            'created_at': '2024-01-24 17:00:15'
        },
        {
            'id': 3,
            'session_id': 1,
            'role': 'user',
            'content': '用户名和邮箱都可以登录，需要图形验证码，有密码找回功能，支持微信登录',
            'message_type': 'text',
            'metadata': None,
            'token_count': 35,
            'created_at': '2024-01-24 17:10:00'
        },
        {
            'id': 4,
            'session_id': 1,
            'role': 'assistant',
            'content': '好的，基于你提供的信息，我为你生成了以下测试用例：\n\n1. 正常登录测试\n   - 使用正确的用户名和密码登录\n   - 使用正确的邮箱和密码登录\n   - 验证码输入正确\n\n2. 异常登录测试\n   - 用户名不存在\n   - 密码错误\n   - 验证码错误\n   - 用户名或密码为空\n\n3. 密码找回测试\n   - 验证邮箱地址\n   - 发送重置邮件\n   - 重置密码链接有效性\n\n4. 微信登录测试\n   - 微信授权登录\n   - 绑定微信账号\n   - 解绑微信账号',
            'message_type': 'text',
            'metadata': None,
            'token_count': 180,
            'created_at': '2024-01-24 17:10:15'
        }
    ],
    2: [
        {
            'id': 5,
            'session_id': 2,
            'role': 'user',
            'content': '请帮我分析一下这个需求的测试点',
            'message_type': 'text',
            'metadata': None,
            'token_count': 15,
            'created_at': '2024-01-24 17:15:10'
        },
        {
            'id': 6,
            'session_id': 2,
            'role': 'assistant',
            'content': '好的，请提供需求的具体内容，我会帮你分析测试点。',
            'message_type': 'text',
            'metadata': None,
            'token_count': 25,
            'created_at': '2024-01-24 17:15:15'
        }
    ]
}


@ai_assistant_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """获取用户的AI会话列表"""
    current_user_id = get_jwt_identity()
    status = request.args.get('status', '')
    
    # TODO: 从ai_sessions表查询
    filtered_sessions = [s for s in mock_sessions if s['user_id'] == current_user_id]
    
    if status:
        filtered_sessions = [s for s in filtered_sessions if s['status'] == status]
    
    return make_response(0, 'success', {
        'list': filtered_sessions,
        'total': len(filtered_sessions)
    })


@ai_assistant_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_session():
    """创建新会话"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    new_session = {
        'id': len(mock_sessions) + 1,
        'user_id': current_user_id,
        'session_name': data.get('session_name', '新会话'),
        'session_type': data.get('session_type', 'chat'),
        'model_id': data.get('model_id'),
        'prompt_id': data.get('prompt_id'),
        'knowledge_ids': data.get('knowledge_ids'),
        'mcp_config_id': data.get('mcp_config_id'),
        'status': 'active',
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    mock_sessions.append(new_session)
    mock_messages[new_session['id']] = []
    
    return make_response(0, '创建成功', new_session)


@ai_assistant_bp.route('/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    """获取会话详情"""
    # TODO: 从ai_sessions表查询
    session = next((s for s in mock_sessions if s['id'] == session_id), None)
    if not session:
        return make_response(404, '会话不存在')
    return make_response(0, 'success', session)


@ai_assistant_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@jwt_required()
def update_session(session_id):
    """更新会话"""
    # TODO: 从ai_sessions表查询
    session = next((s for s in mock_sessions if s['id'] == session_id), None)
    if not session:
        return make_response(404, '会话不存在')
    
    data = request.get_json()
    
    if 'session_name' in data:
        session['session_name'] = data['session_name']
    if 'model_id' in data:
        session['model_id'] = data['model_id']
    if 'prompt_id' in data:
        session['prompt_id'] = data['prompt_id']
    if 'knowledge_ids' in data:
        session['knowledge_ids'] = data['knowledge_ids']
    if 'mcp_config_id' in data:
        session['mcp_config_id'] = data['mcp_config_id']
    if 'status' in data:
        session['status'] = data['status']
    
    session['updated_at'] = datetime.utcnow().isoformat()
    
    return make_response(0, '更新成功', session)


@ai_assistant_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    """删除会话"""
    # TODO: 从ai_sessions表删除
    global mock_sessions
    mock_sessions = [s for s in mock_sessions if s['id'] != session_id]
    if session_id in mock_messages:
        del mock_messages[session_id]
    
    return make_response(0, '删除成功')


@ai_assistant_bp.route('/sessions/<int:session_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(session_id):
    """获取会话的消息列表"""
    # TODO: 从ai_messages表查询
    messages = mock_messages.get(session_id, [])
    return make_response(0, 'success', messages)


@ai_assistant_bp.route('/sessions/<int:session_id>/messages', methods=['POST'])
@jwt_required()
def send_message(session_id):
    """发送消息"""
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return make_response(400, '消息内容不能为空')
    
    # 获取会话信息
    session = next((s for s in mock_sessions if s['id'] == session_id), None)
    if not session:
        return make_response(404, '会话不存在')
    
    # 保存用户消息
    user_message = {
        'id': len(mock_messages.get(session_id, [])) + 1,
        'session_id': session_id,
        'role': 'user',
        'content': content,
        'message_type': data.get('message_type', 'text'),
        'metadata': data.get('metadata'),
        'token_count': len(content.split()),
        'created_at': datetime.utcnow().isoformat()
    }
    
    if session_id not in mock_messages:
        mock_messages[session_id] = []
    mock_messages[session_id].append(user_message)
    
    # 调用AI服务生成回复
    try:
        # 获取大模型配置
        model_id = data.get('options', {}).get('model_id') or session.get('model_id')
        prompt_id = data.get('options', {}).get('prompt_id') or session.get('prompt_id')
        knowledge_ids = data.get('options', {}).get('knowledge_ids') or session.get('knowledge_ids', [])
        
        # 获取提示词内容
        prompt_content = None
        if prompt_id:
            prompt = Prompt.query.filter(
                Prompt.id == prompt_id,
                Prompt.is_active == True
            ).first()
            if prompt:
                prompt_content = prompt.content
        
        # 获取知识库内容
        knowledge_contents = None
        if knowledge_ids:
            knowledges = Knowledge.query.filter(
                Knowledge.id.in_(knowledge_ids),
                Knowledge.is_active == True
            ).all()
            if knowledges:
                knowledge_contents = [k.content for k in knowledges]
        
        # 创建AI服务
        ai_service = None
        if model_id:
            llm_config = LLMConfig.query.get(model_id)
            if llm_config and llm_config.is_active:
                ai_service = AIService(llm_config)
        else:
            ai_service = AIService.get_default_service()
        
        # 构建消息历史
        messages = []
        # 添加系统提示词
        if prompt_content:
            messages.append(ChatMessage(role="system", content=prompt_content))
        
        # 添加知识库上下文
        if knowledge_contents:
            knowledge_context = "\n\n参考知识库内容：\n" + "\n\n".join(knowledge_contents[:1000])  # 限制知识库内容长度
            messages.append(ChatMessage(role="system", content=knowledge_context))
        
        # 添加历史消息
        history_messages = mock_messages.get(session_id, [])
        for msg in history_messages[-10:]:  # 只取最近10条消息
            messages.append(ChatMessage(role=msg['role'], content=msg['content']))
        
        # 添加当前用户消息
        messages.append(ChatMessage(role="user", content=content))
        
        # 调用AI服务
        if ai_service:
            response = ai_service.client.chat(
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            ai_response = response.content
        else:
            # 没有配置AI服务，使用模拟回复
            ai_response = generate_ai_response(content, {})
        
        # 保存AI回复
        assistant_message = {
            'id': user_message['id'] + 1,
            'session_id': session_id,
            'role': 'assistant',
            'content': ai_response,
            'message_type': 'text',
            'metadata': None,
            'token_count': len(ai_response.split()),
            'created_at': datetime.utcnow().isoformat()
        }
        
        mock_messages[session_id].append(assistant_message)
        
        return make_response(0, '发送成功', assistant_message)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        # 如果AI调用失败，使用模拟回复
        ai_response = generate_ai_response(content, {})
        
        assistant_message = {
            'id': user_message['id'] + 1,
            'session_id': session_id,
            'role': 'assistant',
            'content': ai_response,
            'message_type': 'text',
            'metadata': None,
            'token_count': len(ai_response.split()),
            'created_at': datetime.utcnow().isoformat()
        }
        
        if session_id not in mock_messages:
            mock_messages[session_id] = []
        mock_messages[session_id].append(assistant_message)
        
        return make_response(0, '发送成功', assistant_message)


def generate_ai_response(user_message, options):
    """生成AI回复（模拟）"""
    # 这里应该调用真实的AI模型
    responses = [
        "我理解你的问题。让我来帮你分析一下...",
        "这是一个很好的问题！根据你提供的信息，我的建议是...",
        "基于你的描述，我认为需要考虑以下几个方面...",
        "我来帮你解决这个问题。首先，我们需要明确..."
    ]
    
    import random
    return random.choice(responses)


@ai_assistant_bp.route('/sessions/<int:session_id>/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(session_id, message_id):
    """删除消息"""
    # TODO: 从ai_messages表删除
    if session_id in mock_messages:
        mock_messages[session_id] = [
            m for m in mock_messages[session_id] if m['id'] != message_id
        ]
    
    return make_response(0, '删除成功')


@ai_assistant_bp.route('/knowledge', methods=['GET'])
@jwt_required()
def get_knowledge_bases():
    """获取知识库列表"""
    # 从知识库表查询
    knowledges = Knowledge.query.filter(
        Knowledge.is_active == True
    ).order_by(Knowledge.created_at.desc()).all()
    
    result = []
    for kb in knowledges:
        result.append({
            'id': kb.id,
            'name': kb.name,
            'description': kb.description or ''
        })
    
    return make_response(0, 'success', result)


@ai_assistant_bp.route('/prompts', methods=['GET'])
@jwt_required()
def get_prompts():
    """获取提示词列表"""
    # 从提示词表查询
    prompts = Prompt.query.filter(
        Prompt.is_active == True
    ).order_by(Prompt.created_at.desc()).all()
    
    result = []
    for prompt in prompts:
        result.append({
            'id': prompt.id,
            'name': prompt.name,
            'description': prompt.description or ''
        })
    
    return make_response(0, 'success', result)


@ai_assistant_bp.route('/models', methods=['GET'])
@jwt_required()
def get_models():
    """获取大模型列表"""
    # 从大模型配置表查询
    models = LLMConfig.query.filter(
        LLMConfig.is_active == True
    ).order_by(LLMConfig.created_at.desc()).all()
    
    result = []
    for model in models:
        result.append({
            'id': model.id,
            'name': model.name,
            'provider': model.provider,
            'model': model.model,
            'description': model.description or ''
        })
    
    return make_response(0, 'success', result)


@ai_assistant_bp.route('/mcp-configs', methods=['GET'])
@jwt_required()
def get_mcp_configs():
    """获取MCP配置列表"""
    # 从MCP配置表查询
    mcp_configs = MCPConfig.query.filter(
        MCPConfig.status == 1
    ).order_by(MCPConfig.created_at.desc()).all()
    
    result = []
    for mcp in mcp_configs:
        result.append({
            'id': mcp.id,
            'name': mcp.name,
            'server_name': mcp.server_name,
            'server_url': mcp.server_url
        })
    
    return make_response(0, 'success', result)

