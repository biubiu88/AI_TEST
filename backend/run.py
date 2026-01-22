"""
Flask 应用入口
"""
import os
from app import create_app, db
from app.models import Requirement, TestCase, User

# 获取环境配置
env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)


@app.shell_context_processor
def make_shell_context():
    """为 Flask shell 添加上下文"""
    return {
        'db': db,
        'Requirement': Requirement,
        'TestCase': TestCase,
        'User': User
    }


@app.cli.command('init-db')
def init_db():
    """初始化数据库"""
    db.create_all()
    print('数据库表创建成功！')


@app.cli.command('drop-db')
def drop_db():
    """删除数据库表"""
    if input('确定要删除所有表吗？(y/N): ').lower() == 'y':
        db.drop_all()
        print('数据库表已删除！')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
