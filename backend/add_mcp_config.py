"""
添加MCP配置功能
"""
from sqlalchemy import text
from app import create_app, db
from app.models import Menu, Permission, Role

app = create_app()

with app.app_context():
    # 1. 创建MCP配置表
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS mcp_configs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL COMMENT '配置名称',
        server_url VARCHAR(500) NOT NULL COMMENT 'MCP服务器地址',
        server_name VARCHAR(100) COMMENT '服务器名称',
        description VARCHAR(500) COMMENT '配置描述',
        timeout INT DEFAULT 30 COMMENT '超时时间(秒)',
        max_retries INT DEFAULT 3 COMMENT '最大重试次数',
        status INT DEFAULT 1 COMMENT '状态: 1启用 0禁用',
        is_default BOOLEAN DEFAULT FALSE COMMENT '是否默认配置',
        extra_params TEXT COMMENT '额外参数JSON',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        INDEX idx_status (status),
        INDEX idx_is_default (is_default)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='MCP配置表';
    """
    
    db.session.execute(text(create_table_sql))
    db.session.commit()
    print("MCP配置表创建成功")
    
    # 2. 添加MCP配置权限
    mcp_permissions = [
        {
            'name': 'MCP配置查看',
            'code': 'mcp:view',
            'type': 'button',
            'description': '查看MCP配置'
        },
        {
            'name': 'MCP配置新增',
            'code': 'mcp:create',
            'type': 'button',
            'description': '新增MCP配置'
        },
        {
            'name': 'MCP配置编辑',
            'code': 'mcp:edit',
            'type': 'button',
            'description': '编辑MCP配置'
        },
        {
            'name': 'MCP配置删除',
            'code': 'mcp:delete',
            'type': 'button',
            'description': '删除MCP配置'
        }
    ]
    
    for perm_data in mcp_permissions:
        existing = Permission.query.filter_by(code=perm_data['code']).first()
        if not existing:
            permission = Permission(
                name=perm_data['name'],
                code=perm_data['code'],
                type=perm_data['type'],
                description=perm_data['description']
            )
            db.session.add(permission)
            print(f"添加权限: {perm_data['name']} ({perm_data['code']})")
    
    db.session.commit()
    
    # 3. 添加MCP配置菜单
    system_menu = Menu.query.filter_by(name='System').first()
    if system_menu:
        # 获取当前最大的sort值
        max_sort = db.session.query(db.func.max(Menu.sort)).filter(
            Menu.parent_id == system_menu.id
        ).scalar() or 0
        
        mcp_menu = Menu(
            parent_id=system_menu.id,
            name='MCPConfigs',
            path='/system/mcp-configs',
            component='MCPConfigView',
            redirect='',
            icon='Connection',
            title='MCP配置',
            hidden=False,
            always_show=False,
            keep_alive=True,
            sort=max_sort + 1,
            type='menu',
            permission='mcp:view',
            status=1
        )
        db.session.add(mcp_menu)
        db.session.commit()
        print(f"添加菜单: MCP配置 (ID: {mcp_menu.id}, Sort: {mcp_menu.sort})")
    
    # 4. 为管理员角色分配所有MCP权限
    admin_role = Role.query.filter_by(code='admin').first()
    if admin_role:
        mcp_perms = Permission.query.filter(Permission.code.like('mcp:%')).all()
        for perm in mcp_perms:
            if perm not in admin_role.permissions:
                admin_role.permissions.append(perm)
        print(f"为管理员角色分配 {len(mcp_perms)} 个MCP权限")
    
    # 5. 为普通用户角色分配MCP查看权限
    user_role = Role.query.filter_by(code='user').first()
    if user_role:
        mcp_view_perm = Permission.query.filter_by(code='mcp:view').first()
        if mcp_view_perm and mcp_view_perm not in user_role.permissions:
            user_role.permissions.append(mcp_view_perm)
        print("为普通用户角色分配MCP查看权限")
    
    db.session.commit()
    
    # 6. 显示更新后的菜单结构
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
    
    print("\nMCP配置功能添加完成！")
