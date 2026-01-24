"""
修改菜单结构：
1. 将提示词管理挪到知识资产的二级目录下
2. 删除公共组件库菜单
"""
from app import create_app, db
from app.models import Menu, Role

app = create_app()

with app.app_context():
    # 1. 获取知识资产菜单
    knowledge_menu = Menu.query.filter_by(name='Knowledge').first()
    if not knowledge_menu:
        print("未找到知识资产菜单")
        exit(1)

    # 2. 获取提示词管理菜单
    prompts_menu = Menu.query.filter_by(name='Prompts').first()
    if not prompts_menu:
        print("未找到提示词管理菜单")
        exit(1)

    # 3. 修改提示词管理的父菜单为知识资产
    print(f"修改提示词管理菜单: {prompts_menu.name} (ID: {prompts_menu.id})")
    print(f"  原父菜单ID: {prompts_menu.parent_id}")
    prompts_menu.parent_id = knowledge_menu.id
    prompts_menu.path = '/knowledge/prompts'
    print(f"  新父菜单ID: {knowledge_menu.id}")
    print(f"  新路径: {prompts_menu.path}")

    db.session.commit()

    # 4. 获取公共组件库菜单
    component_menu = Menu.query.filter_by(name='ComponentLibrary').first()
    if component_menu:
        print(f"\n删除公共组件库菜单: {component_menu.name} (ID: {component_menu.id})")
        db.session.delete(component_menu)
        db.session.commit()
    else:
        print("\n未找到公共组件库菜单")

    # 5. 更新测试核心菜单的排序
    testing_menu = Menu.query.filter_by(name='Testing').first()
    if testing_menu:
        print(f"\n更新测试核心菜单排序")
        testing_menu.sort = 1

    # 6. 更新知识资产菜单的排序和重定向
    knowledge_menu.sort = 2
    knowledge_menu.redirect = '/knowledge/knowledges'

    # 7. 更新系统配置菜单的排序
    system_menu = Menu.query.filter_by(name='System').first()
    if system_menu:
        system_menu.sort = 3

    db.session.commit()

    # 8. 重新排序知识资产下的子菜单
    print("\n重新排序知识资产子菜单:")
    knowledge_children = Menu.query.filter_by(parent_id=knowledge_menu.id).order_by(Menu.sort.asc()).all()
    for i, child in enumerate(knowledge_children):
        if child.sort != i:
            child.sort = i
            print(f"  {child.title}: {child.sort} -> {i}")

    db.session.commit()

    # 9. 为所有角色重新分配菜单
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
            ~Menu.name.in_(['Users', 'Roles', 'Menus', 'LLMConfigs', 'Logs'])
        ).all()
        user_role.menus = user_menus
        print(f"  普通用户角色: 分配 {len(user_menus)} 个菜单")

    db.session.commit()

    # 10. 显示更新后的菜单结构
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

    print("\n菜单结构修改完成！")
