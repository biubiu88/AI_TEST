"""
添加菜单管理菜单到数据库
"""
from app import create_app, db
from app.models import Menu, Role

app = create_app()

with app.app_context():
    # 检查是否已存在菜单管理菜单
    existing_menu = Menu.query.filter_by(path='/menu').first()
    if existing_menu:
        print(f"菜单管理菜单已存在，ID: {existing_menu.id}")
        # 更新菜单信息
        existing_menu.name = 'Menu'
        existing_menu.component = 'MenuView'
        existing_menu.icon = 'Menu'
        existing_menu.title = '菜单管理'
        existing_menu.sort = 7
        existing_menu.type = 'menu'
        existing_menu.permission = 'system:menu'
        existing_menu.status = 1
        db.session.commit()
        print("菜单信息已更新")
    else:
        # 创建菜单管理菜单
        menu = Menu(
            parent_id=1,  # Root的ID
            name='Menu',
            path='/menu',
            component='MenuView',
            redirect='',
            icon='Menu',
            title='菜单管理',
            hidden=False,
            always_show=False,
            keep_alive=True,
            sort=7,
            type='menu',
            permission='system:menu',
            status=1
        )
        db.session.add(menu)
        db.session.commit()
        print(f"菜单管理菜单已创建，ID: {menu.id}")

    # 为管理员角色分配这个菜单
    admin_role = Role.query.filter_by(code='admin').first()
    if admin_role:
        menu = Menu.query.filter_by(path='/menu').first()
        if menu and menu not in admin_role.menus:
            admin_role.menus.append(menu)
            db.session.commit()
            print("已为管理员角色分配菜单管理菜单")
        else:
            print("管理员角色已拥有菜单管理菜单")

    # 为普通用户角色分配这个菜单（可选）
    user_role = Role.query.filter_by(code='user').first()
    if user_role:
        menu = Menu.query.filter_by(path='/menu').first()
        if menu and menu not in user_role.menus:
            # 如果需要给普通用户也分配菜单管理权限，取消下面的注释
            # user_role.menus.append(menu)
            # db.session.commit()
            print("普通用户角色未分配菜单管理菜单（需要管理员权限）")
        else:
            print("普通用户角色已拥有菜单管理菜单")

    print("\n菜单管理菜单添加完成！")
