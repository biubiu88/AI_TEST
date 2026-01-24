"""
修改菜单图标和名称
1. 修改测试核心的图标
2. 将概览仪表盘改名为首页
"""
from app import create_app, db
from app.models import Menu

app = create_app()

with app.app_context():
    # 1. 修改测试核心的图标
    testing_menu = Menu.query.filter_by(name='Testing').first()
    if testing_menu:
        print(f"修改测试核心图标: {testing_menu.name} (ID: {testing_menu.id})")
        print(f"  原图标: {testing_menu.icon}")
        testing_menu.icon = 'Microscope'  # 显微镜图标
        print(f"  新图标: {testing_menu.icon}")
    else:
        print("未找到测试核心菜单")

    # 2. 将概览仪表盘改名为首页
    dashboard_menu = Menu.query.filter_by(name='Dashboard').first()
    if dashboard_menu:
        print(f"\n修改Dashboard菜单名称: {dashboard_menu.name} (ID: {dashboard_menu.id})")
        print(f"  原标题: {dashboard_menu.title}")
        dashboard_menu.title = '首页'
        dashboard_menu.name = 'Home'  # 同时也更新name
        print(f"  新标题: {dashboard_menu.title}")
        print(f"  新名称: {dashboard_menu.name}")
    else:
        print("未找到Dashboard菜单")

    # 3. 更新其他菜单的图标（确保使用Element Plus图标）
    icon_mappings = {
        'TestCases': 'List',
        'Generate': 'MagicStick',
        'Requirements': 'Document',
        'Prompts': 'ChatDotRound',
        'Knowledges': 'Reading',
        'ComponentLibrary': 'Grid',
        'Users': 'User',
        'Roles': 'UserFilled',
        'Menus': 'Menu',
        'LLMConfigs': 'Connection',
        'Logs': 'DocumentCopy'
    }

    print("\n更新菜单图标:")
    for menu_name, icon in icon_mappings.items():
        menu = Menu.query.filter_by(name=menu_name).first()
        if menu:
            if menu.icon != icon:
                menu.icon = icon
                print(f"  {menu.title}: {menu.icon} -> {icon}")

    db.session.commit()

    # 4. 显示更新后的菜单结构
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

    print("\n菜单图标和名称修改完成！")
