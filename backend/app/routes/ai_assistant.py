"""
AI助手路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import User, Prompt, Knowledge, LLMConfig, MCPConfig, ChatSession, ChatMessage
from app.services.ai_service import AIService
from app.services.llm_clients import ChatMessage as LLMChatMessage
from app.middlewares import log_operation

ai_assistant_bp = Blueprint('ai_assistant', __name__)


def make_response(code=0, message='success', data=None):
    """统一响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    })


@ai_assistant_bp.route('/sessions', methods=['GET'])
@jwt_required()
@log_operation
def get_sessions():
    """获取用户的AI会话列表"""
    current_user_id = get_jwt_identity()
    
    # 按置顶状态和更新时间排序
    sessions = ChatSession.query.filter_by(user_id=current_user_id).order_by(
        ChatSession.is_pinned.desc(), 
        ChatSession.updated_at.desc()
    ).all()
    
    return make_response(0, 'success', {
        'list': [s.to_dict() for s in sessions],
        'total': len(sessions)
    })


@ai_assistant_bp.route('/sessions', methods=['POST'])
@jwt_required()
@log_operation
def create_session():
    """创建新会话"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    new_session = ChatSession(
        user_id=current_user_id,
        session_name=data.get('session_name', '新会话'),
        model_id=data.get('model_id'),
        prompt_id=data.get('prompt_id'),
        knowledge_ids=data.get('knowledge_ids', []),
        mcp_config_id=data.get('mcp_config_id')
    )
    
    db.session.add(new_session)
    db.session.commit()
    
    return make_response(0, '创建成功', new_session.to_dict())


@ai_assistant_bp.route('/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
@log_operation
def get_session(session_id):
    """获取会话详情"""
    current_user_id = get_jwt_identity()
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user_id).first()
    
    if not session:
        return make_response(404, '会话不存在')
    return make_response(0, 'success', session.to_dict())


@ai_assistant_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@jwt_required()
@log_operation
def update_session(session_id):
    """更新会话"""
    current_user_id = get_jwt_identity()
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user_id).first()
    
    if not session:
        return make_response(404, '会话不存在')
    
    data = request.get_json()
    
    if 'session_name' in data:
        session.session_name = data['session_name']
    if 'is_pinned' in data:
        session.is_pinned = data['is_pinned']
    if 'model_id' in data:
        session.model_id = data['model_id']
    if 'prompt_id' in data:
        session.prompt_id = data['prompt_id']
    if 'knowledge_ids' in data:
        session.knowledge_ids = data['knowledge_ids']
    if 'mcp_config_id' in data:
        session.mcp_config_id = data['mcp_config_id']
    
    session.updated_at = datetime.utcnow()
    db.session.commit()
    
    return make_response(0, '更新成功', session.to_dict())


@ai_assistant_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
@log_operation
def delete_session(session_id):
    """删除会话"""
    current_user_id = get_jwt_identity()
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user_id).first()
    
    if not session:
        return make_response(404, '会话不存在')
    
    db.session.delete(session)
    db.session.commit()
    
    return make_response(0, '删除成功')


@ai_assistant_bp.route('/sessions/<int:session_id>/messages', methods=['GET'])
@jwt_required()
@log_operation
def get_messages(session_id):
    """获取会话的消息列表"""
    current_user_id = get_jwt_identity()
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user_id).first()
    
    if not session:
        return make_response(404, '会话不存在')
    
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at.asc()).all()
    return make_response(0, 'success', [m.to_dict() for m in messages])


@ai_assistant_bp.route('/sessions/<int:session_id>/messages', methods=['POST'])
@jwt_required()
@log_operation
def send_message(session_id):
    """发送消息并获取AI回复"""
    current_user_id = get_jwt_identity()
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user_id).first()
    
    if not session:
        return make_response(404, '会话不存在')
    
    data = request.get_json()
    user_content = data.get('content', '').strip()
    
    if not user_content:
        return make_response(400, '消息内容不能为空')
    
    # 1. 保存用户消息
    user_msg = ChatMessage(
        session_id=session_id,
        role='user',
        content=user_content
    )
    db.session.add(user_msg)
    
    # 先提交一次，确保用户消息已保存
    try:
        session.updated_at = datetime.utcnow()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_response(500, f'保存消息失败: {str(e)}')
    
    # 2. 调用AI服务
    try:
        # 准备配置
        options = data.get('options', {})
        model_id = options.get('model_id') or session.model_id
        prompt_id = options.get('prompt_id') or session.prompt_id
        knowledge_ids = options.get('knowledge_ids') or session.knowledge_ids or []
        
        # 获取系统提示词
        system_prompt = ""
        if prompt_id:
            prompt = Prompt.query.get(prompt_id)
            if prompt:
                system_prompt = prompt.content
        
        # 获取知识库上下文
        if knowledge_ids:
            knowledges = Knowledge.query.filter(Knowledge.id.in_(knowledge_ids)).all()
            if knowledges:
                knowledge_context = "\n\n参考知识库内容：\n" + "\n\n".join([k.content for k in knowledges])
                system_prompt += knowledge_context
        
        # 构建历史记录
        history = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at.asc()).all()
        llm_messages = []
        
        if system_prompt:
            llm_messages.append(LLMChatMessage(role="system", content=system_prompt))
            
        for m in history[-11:]:  # 取最近10条+当前这条
            llm_messages.append(LLMChatMessage(role=m.role, content=m.content))
            
        # 初始化AI服务
        ai_service = None
        if model_id:
            config = LLMConfig.query.get(model_id)
            if config:
                ai_service = AIService(config)
        
        if not ai_service:
            ai_service = AIService.get_default_service()
            
        # 发送请求
        ai_response_content = ""
        if ai_service:
            try:
                response = ai_service.client.chat(messages=llm_messages)
                ai_response_content = response.content
            except Exception as e:
                ai_response_content = f"AI助手调用出错: {str(e)}"
        else:
            ai_response_content = "未配置AI服务，请在设置中选择模型。"
            
        # 3. 保存AI回复
        assistant_msg = ChatMessage(
            session_id=session_id,
            role='assistant',
            content=ai_response_content,
            model=ai_service.model if ai_service else 'unknown'
        )
        db.session.add(assistant_msg)
        
        # 更新会话时间
        session.updated_at = datetime.utcnow()
        db.session.commit()
        
        return make_response(0, '发送成功', assistant_msg.to_dict())
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return make_response(500, f'处理AI回复失败: {str(e)}')


@ai_assistant_bp.route('/sessions/<int:session_id>/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
@log_operation
def delete_message(session_id, message_id):
    """删除单条消息"""
    current_user_id = get_jwt_identity()
    session = ChatSession.query.filter_by(id=session_id, user_id=current_user_id).first()
    
    if not session:
        return make_response(404, '会话不存在')
    
    msg = ChatMessage.query.filter_by(id=message_id, session_id=session_id).first()
    if not msg:
        return make_response(404, '消息不存在')
        
    db.session.delete(msg)
    db.session.commit()
    
    return make_response(0, '删除成功')


@ai_assistant_bp.route('/knowledge', methods=['GET'])
@jwt_required()
@log_operation
def get_knowledge_bases():
    """获取知识库列表"""
    knowledges = Knowledge.query.filter_by(is_active=True).all()
    return make_response(0, 'success', [
        {'id': k.id, 'name': k.name, 'description': k.description} for k in knowledges
    ])


@ai_assistant_bp.route('/prompts', methods=['GET'])
@jwt_required()
@log_operation
def get_prompts():
    """获取提示词列表"""
    prompts = Prompt.query.filter_by(is_active=True).all()
    return make_response(0, 'success', [
        {'id': p.id, 'name': p.name, 'description': p.description} for p in prompts
    ])


@ai_assistant_bp.route('/models', methods=['GET'])
@jwt_required()
@log_operation
def get_models():
    """获取大模型列表"""
    models = LLMConfig.query.filter_by(is_active=True).all()
    return make_response(0, 'success', [
        {'id': m.id, 'name': m.name, 'provider': m.provider, 'model': m.model} for m in models
    ])


@ai_assistant_bp.route('/mcp-configs', methods=['GET'])
@jwt_required()
@log_operation
def get_mcp_configs():
    """获取MCP配置列表"""
    mcp_configs = MCPConfig.query.filter_by(status=1).all()
    return make_response(0, 'success', [
        {'id': m.id, 'name': m.name, 'server_name': m.server_name} for m in mcp_configs
    ])
