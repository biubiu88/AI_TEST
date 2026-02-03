"""
Flask 应用工厂
"""
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

from config import config

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_name: str = 'default') -> Flask:
    """创建 Flask 应用实例"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # JWT配置
    app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册蓝图
    from app.routes import requirement_bp, testcase_bp, ai_bp, prompt_bp, knowledge_bp, llm_config_bp, permission_bp
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.logs import logs_bp
    from app.routes.mcp import mcp_bp
    from app.routes.ai_assistant import ai_assistant_bp
    from app.routes.review import review_bp
    from app.routes.data_factory import data_factory_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(requirement_bp, url_prefix='/api/requirements')
    app.register_blueprint(testcase_bp, url_prefix='/api/testcases')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    app.register_blueprint(prompt_bp, url_prefix='/api/prompts')
    app.register_blueprint(knowledge_bp, url_prefix='/api/knowledges')
    app.register_blueprint(llm_config_bp, url_prefix='/api/llm-configs')
    app.register_blueprint(permission_bp, url_prefix='/api/permission')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')
    app.register_blueprint(mcp_bp, url_prefix='/api/mcp-configs')
    app.register_blueprint(ai_assistant_bp, url_prefix='/api/ai-assistant')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(data_factory_bp, url_prefix='/api/data-factory')
    
    # 健康检查路由
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'Service is running'}
    
    return app
