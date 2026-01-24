"""
创建操作日志表
"""
from app import create_app, db
from app.models import OperationLog

app = create_app('development')

with app.app_context():
    # 创建操作日志表
    db.create_all()
    print("操作日志表创建成功！")
    print(f"表名: {OperationLog.__tablename__}")
