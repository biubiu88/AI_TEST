"""
修改测试核心的图标为Element Plus中存在的图标
"""
from app import create_app, db
from app.models import Menu

app = create_app()

with app.app_context():
    # 修改测试核心的图标为Tools（工具图标）
    testing_menu = Menu.query.filter_by(name='Testing').first()
    if testing_menu:
        print(f"修改测试核心图标: {testing_menu.name} (ID: {testing_menu.id})")
        print(f"  原图标: {testing_menu.icon}")
        testing_menu.icon = 'Tools'  # 使用工具图标
        print(f"  新图标: {testing_menu.icon}")

    db.session.commit()

    # 显示更新后的菜单结构
    print("\n=== 更新后的菜单结构 ===")
    top_menus = Menu.query.filter_by(parent_id=0).order_by(Menu.sort.asc()).all()
    for menu in top_menus:
        print(f"\n【{menu.title}】({menu.icon})")
        children = Menu.query.filter_by(parent_id=menu.id).order_by(Menu.sort.asc()).all()
        if children:
            for child in children:
                print(f"  - {child.title}: {child.path} ({child.icon})")
        else:
            print(f"  (直接访问: {menu.path})")

    print("\n菜单图标修改完成！")
