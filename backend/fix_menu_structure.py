"""
修改菜单结构：将概览仪表盘作为一级菜单，无需二级菜单
"""
from app import create_app, db
from app.models import Menu, Role

app = create_app()

with app.app_context():
    # 1. 删除原有的首页目录（Home）
    home_menu = Menu.query.filter_by(name='Home').first()
    if home_menu:
        print(f"删除原有首页目录: {home_menu.name} (ID: {home_menu.id})")
        db.session.delete(home_menu)
        db.session.commit()

    # 2. 将Dashboard改为一级菜单
    dashboard_menu = Menu.query.filter_by(name='Dashboard').first()
    if dashboard_menu:
        print(f"修改Dashboard菜单: {dashboard_menu.name} (ID: {dashboard_menu.id})")
        dashboard_menu.parent_id = 0  # 改为一级菜单
        dashboard_menu.path = '/dashboard'
        dashboard_menu.redirect = ''
        dashboard_menu.icon = 'DataBoard'
        dashboard_menu.title = '概览仪表盘'
        dashboard_menu.type = 'menu'
        dashboard_menu.sort = 0  # 排在第一位
        db.session.commit()
    else:
        # 如果Dashboard不存在，创建一个
        dashboard_menu = Menu(
            parent_id=0,
            name='Dashboard',
            path='/dashboard',
            component='DashboardView',
            redirect='',
            icon='DataBoard',
            title='概览仪表盘',
            hidden=False,
            always_show=False,
            keep_alive=True,
            sort=0,
            type='menu',
            permission='dashboard:view',
            status=1
        )
        db.session.add(dashboard_menu)
        db.session.commit()
        print(f"创建Dashboard菜单: {dashboard_menu.name} (ID: {dashboard_menu.id})")

    # 3. 更新测试核心的图标
    testing_menu = Menu.query.filter_by(name='Testing').first()
    if testing_menu:
        print(f"更新测试核心图标: {testing_menu.name} (ID: {testing_menu.id})")
        testing_menu.icon = 'Microscope'  # 使用显微镜图标
        db.session.commit()

    # 4. 更新其他菜单的排序
    menus = Menu.query.filter_by(parent_id=0).order_by(Menu.sort.asc()).all()
    print("\n更新菜单排序:")
    for i, menu in enumerate(menus):
        if menu.sort != i:
            menu.sort = i
            print(f"  {menu.title}: {menu.sort} -> {i}")

    db.session.commit()

    # 5. 为所有角色重新分配菜单
    print("\n重新分配菜单给角色:")
    admin_role = Role.query.filter_by(code='admin').first()
    user_role = Role.query.filter_by(code='user').first()

    if admin_role:
        all_menus = Menu.query.all()
        admin_role.menus = all_menus
        print(f"  管理员角色: 分配 {len(all_menus)} 个菜单")

    if user_role:
        # 普通用户只分配二级菜单（不包括系统配置）
        user_menus = Menu.query.filter(
            Menu.parent_id != 0,
            ~Menu.name.in_(['Users', 'Roles', 'Menus', 'LLMConfigs', 'Logs'])
        ).all()
        # 加上概览仪表盘（一级菜单）
        dashboard = Menu.query.filter_by(name='Dashboard').first()
        if dashboard and dashboard not in user_menus:
            user_menus.append(dashboard)

        user_role.menus = user_menus
        print(f"  普通用户角色: 分配 {len(user_menus)} 个菜单")

    db.session.commit()

    # 6. 显示新的菜单结构
    print("\n=== 新的菜单结构 ===")
    top_menus = Menu.query.filter_by(parent_id=0).order_by(Menu.sort.asc()).all()
    for menu in top_menus:
        print(f"\n【{menu.title}】({menu.icon})")
        children = Menu.query.filter_by(parent_id=menu.id).order_by(Menu.sort.asc()).all()
        if children:
            for child in children:
                print(f"  - {child.title}: {child.path}")
        else:
            print(f"  (直接访问: {menu.path})")

    print("\n菜单结构修改完成！")
