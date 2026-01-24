"""
更新菜单结构
按照新的菜单设计重新组织数据库中的菜单
"""
from app import create_app, db
from app.models import Menu, Role, Permission
import json

app = create_app()

def create_menu(data, parent_id=0):
    """创建菜单"""
    menu = Menu(
        parent_id=parent_id,
        name=data.get('name', ''),
        path=data.get('path', ''),
        component=data.get('component', ''),
        redirect=data.get('redirect', ''),
        icon=data.get('icon', ''),
        title=data.get('title', data.get('name', '')),
        hidden=data.get('hidden', False),
        always_show=data.get('alwaysShow', False),
        keep_alive=data.get('keepAlive', False),
        sort=data.get('sort', 0),
        type=data.get('type', 'menu'),
        permission=data.get('permission', ''),
        status=data.get('status', 1)
    )
    db.session.add(menu)
    db.session.flush()  # 获取ID
    return menu.id

def create_permission(data):
    """创建权限"""
    # 检查权限是否已存在
    existing = Permission.query.filter_by(code=data.get('code', '')).first()
    if existing:
        return existing.id

    permission = Permission(
        name=data.get('name', ''),
        code=data.get('code', ''),
        type=data.get('type', 'button'),
        description=data.get('description', '')
    )
    db.session.add(permission)
    db.session.flush()
    return permission.id

with app.app_context():
    # 清空现有菜单（谨慎操作！）
    print("正在清空现有菜单...")
    Menu.query.delete()
    db.session.commit()

    # 定义新的菜单结构
    menu_structure = [
        # 一级菜单：首页
        {
            'name': 'Home',
            'path': '/',
            'component': 'Layout',
            'redirect': '/dashboard',
            'icon': 'HomeFilled',
            'title': '首页',
            'type': 'directory',
            'sort': 0,
            'children': [
                {
                    'name': 'Dashboard',
                    'path': '/dashboard',
                    'component': 'DashboardView',
                    'icon': 'DataBoard',
                    'title': '概览仪表盘',
                    'type': 'menu',
                    'permission': 'dashboard:view',
                    'sort': 1,
                    'keepAlive': True
                }
            ]
        },
        # 一级菜单：测试核心
        {
            'name': 'Testing',
            'path': '/testing',
            'component': 'Layout',
            'redirect': '/testing/testcases',
            'icon': 'Microscope',
            'title': '测试核心',
            'type': 'directory',
            'sort': 1,
            'children': [
                {
                    'name': 'TestCases',
                    'path': '/testing/testcases',
                    'component': 'TestCaseView',
                    'icon': 'List',
                    'title': '测试用例管理',
                    'type': 'menu',
                    'permission': 'testcase:view',
                    'sort': 1,
                    'keepAlive': True
                },
                {
                    'name': 'Generate',
                    'path': '/testing/generate',
                    'component': 'GenerateView',
                    'icon': 'MagicStick',
                    'title': '生成用例',
                    'type': 'menu',
                    'permission': 'ai:generate',
                    'sort': 2,
                    'keepAlive': False
                },
                {
                    'name': 'Requirements',
                    'path': '/testing/requirements',
                    'component': 'RequirementView',
                    'icon': 'Document',
                    'title': '需求管理',
                    'type': 'menu',
                    'permission': 'requirement:view',
                    'sort': 3,
                    'keepAlive': True
                },
                {
                    'name': 'Prompts',
                    'path': '/testing/prompts',
                    'component': 'PromptView',
                    'icon': 'ChatDotRound',
                    'title': '提示词管理',
                    'type': 'menu',
                    'permission': 'prompt:view',
                    'sort': 4,
                    'keepAlive': True
                }
            ]
        },
        # 一级菜单：知识资产
        {
            'name': 'Knowledge',
            'path': '/knowledge',
            'component': 'Layout',
            'redirect': '/knowledge/knowledges',
            'icon': 'Collection',
            'title': '知识资产',
            'type': 'directory',
            'sort': 2,
            'children': [
                {
                    'name': 'Knowledges',
                    'path': '/knowledge/knowledges',
                    'component': 'KnowledgeView',
                    'icon': 'Reading',
                    'title': '知识库管理',
                    'type': 'menu',
                    'permission': 'knowledge:view',
                    'sort': 1,
                    'keepAlive': True
                },
                {
                    'name': 'ComponentLibrary',
                    'path': '/knowledge/components',
                    'component': 'ComponentLibraryView',
                    'icon': 'Grid',
                    'title': '公共组件库',
                    'type': 'menu',
                    'permission': 'component:view',
                    'sort': 2,
                    'keepAlive': True
                }
            ]
        },
        # 一级菜单：系统配置
        {
            'name': 'System',
            'path': '/system',
            'component': 'Layout',
            'redirect': '/system/users',
            'icon': 'Setting',
            'title': '系统配置',
            'type': 'directory',
            'sort': 3,
            'children': [
                {
                    'name': 'Users',
                    'path': '/system/users',
                    'component': 'UserView',
                    'icon': 'User',
                    'title': '用户管理',
                    'type': 'menu',
                    'permission': 'system:user',
                    'sort': 1,
                    'keepAlive': True
                },
                {
                    'name': 'Roles',
                    'path': '/system/roles',
                    'component': 'RoleView',
                    'icon': 'UserFilled',
                    'title': '角色管理',
                    'type': 'menu',
                    'permission': 'system:role',
                    'sort': 2,
                    'keepAlive': True
                },
                {
                    'name': 'Menus',
                    'path': '/system/menus',
                    'component': 'MenuView',
                    'icon': 'Menu',
                    'title': '菜单管理',
                    'type': 'menu',
                    'permission': 'system:menu',
                    'sort': 3,
                    'keepAlive': True
                },
                {
                    'name': 'LLMConfigs',
                    'path': '/system/llm-configs',
                    'component': 'LLMConfigView',
                    'icon': 'Connection',
                    'title': '大模型配置',
                    'type': 'menu',
                    'permission': 'llm:view',
                    'sort': 4,
                    'keepAlive': True
                },
                {
                    'name': 'Logs',
                    'path': '/system/logs',
                    'component': 'LogView',
                    'icon': 'DocumentCopy',
                    'title': '日志与审计',
                    'type': 'menu',
                    'permission': 'system:log',
                    'sort': 5,
                    'keepAlive': False
                }
            ]
        }
    ]

    # 创建菜单和权限
    print("正在创建新菜单结构...")
    menu_id_map = {}

    for menu_group in menu_structure:
        # 创建一级菜单
        group_id = create_menu(menu_group)
        menu_id_map[menu_group['name']] = group_id

        # 创建子菜单
        if 'children' in menu_group:
            for child in menu_group['children']:
                child_id = create_menu(child, parent_id=group_id)
                menu_id_map[child['name']] = child_id

                # 创建对应的权限
                if child.get('permission'):
                    permission_data = {
                        'name': child.get('title', child.get('name')),
                        'code': child.get('permission'),
                        'type': 'menu',
                        'description': f'{child.get("title")}权限'
                    }
                    create_permission(permission_data)

    db.session.commit()

    # 为管理员角色分配所有菜单和权限
    print("正在为管理员角色分配权限...")
    admin_role = Role.query.filter_by(code='admin').first()
    if admin_role:
        # 分配所有菜单
        all_menus = Menu.query.all()
        admin_role.menus = all_menus

        # 分配所有权限
        all_permissions = Permission.query.all()
        admin_role.permissions = all_permissions

        db.session.commit()
        print(f"已为管理员角色分配 {len(all_menus)} 个菜单和 {len(all_permissions)} 个权限")

    # 为普通用户角色分配基本权限
    print("正在为普通用户角色分配权限...")
    user_role = Role.query.filter_by(code='user').first()
    if user_role:
        # 分配基本菜单
        basic_menu_codes = ['Dashboard', 'TestCases', 'Generate', 'Requirements', 'Prompts', 'Knowledges']
        basic_menus = Menu.query.filter(Menu.name.in_(basic_menu_codes)).all()
        user_role.menus = basic_menus

        # 分配基本权限
        basic_permissions = [
            'dashboard:view',
            'testcase:view', 'testcase:create', 'testcase:edit', 'testcase:export',
            'ai:generate',
            'requirement:view', 'requirement:create', 'requirement:edit',
            'prompt:view',
            'knowledge:view'
        ]
        basic_perms = Permission.query.filter(Permission.code.in_(basic_permissions)).all()
        user_role.permissions = basic_perms

        db.session.commit()
        print(f"已为普通用户角色分配 {len(basic_menus)} 个菜单和 {len(basic_perms)} 个权限")

    # 显示创建的菜单
    print("\n=== 新菜单结构 ===")
    for menu_group in menu_structure:
        print(f"\n【{menu_group['title']}】")
        if 'children' in menu_group:
            for child in menu_group['children']:
                print(f"  - {child['title']}: {child['path']}")

    print("\n菜单结构更新完成！")
