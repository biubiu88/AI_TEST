"""
路由模块
"""
from app.routes.requirement import requirement_bp
from app.routes.testcase import testcase_bp
from app.routes.ai import ai_bp
from app.routes.prompt import prompt_bp
from app.routes.knowledge import knowledge_bp
from app.routes.llm_config import llm_config_bp
from app.routes.permission import permission_bp

__all__ = ['requirement_bp', 'testcase_bp', 'ai_bp', 'prompt_bp', 'knowledge_bp', 'llm_config_bp', 'permission_bp']
