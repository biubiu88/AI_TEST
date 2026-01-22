"""
路由模块
"""
from app.routes.requirement import requirement_bp
from app.routes.testcase import testcase_bp
from app.routes.ai import ai_bp
from app.routes.prompt import prompt_bp
from app.routes.knowledge import knowledge_bp

__all__ = ['requirement_bp', 'testcase_bp', 'ai_bp', 'prompt_bp', 'knowledge_bp']
