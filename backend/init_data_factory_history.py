"""
初始化数据工厂历史记录表
"""
from app import create_app, db

if __name__ == '__main__':
    try:
        # 创建应用实例
        app = create_app()
        
        # 在应用上下文中运行
        with app.app_context():
            # 创建表
            from app.models import DataFactoryHistory
            db.create_all()
            print("✓ 数据工厂历史记录表创建成功")
            
            # 检查表是否存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if inspector.has_table('data_factory_history'):
                print("✓ 数据工厂历史记录表已确认存在")
            else:
                print("✗ 数据工厂历史记录表创建失败")
                
    except Exception as e:
        print(f"✗ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
