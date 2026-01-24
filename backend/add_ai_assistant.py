"""
添加AI助手功能
"""
from sqlalchemy import text
from app import create_app, db
from app.models import Menu, Permission, Role

app = create_app()

with app.app_context():
    # 1. 创建AI会话表
    create_sessions_table_sql = """
    CREATE TABLE IF NOT EXISTS ai_sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL COMMENT '用户ID',
        session_name VARCHAR(200) DEFAULT '新会话' COMMENT '会话名称',
        session_type VARCHAR(50) DEFAULT 'chat' COMMENT '会话类型: chat/analysis/generation',
        model_id INT COMMENT '使用的模型ID',
        prompt_id INT COMMENT '使用的提示词ID',
        knowledge_ids TEXT COMMENT '关联的知识库ID列表(JSON)',
        mcp_config_id INT COMMENT '使用的MCP配置ID',
        status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/archived/deleted',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        INDEX idx_user_id (user_id),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI会话表';
    """
    
    db.session.execute(text(create_sessions_table_sql))
    db.session.commit()
    print("AI会话表创建成功")
    
    # 2. 创建AI消息表
    create_messages_table_sql = """
    CREATE TABLE IF NOT EXISTS ai_messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id INT NOT NULL COMMENT '会话ID',
        role VARCHAR(20) NOT NULL COMMENT '角色: user/assistant/system',
        content TEXT NOT NULL COMMENT '消息内容',
        message_type VARCHAR(50) DEFAULT 'text' COMMENT '消息类型: text/image/code/table',
        metadata TEXT COMMENT '元数据JSON',
        token_count INT DEFAULT 0 COMMENT 'Token数量',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        INDEX idx_session_id (session_id),
        INDEX idx_role (role)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI消息表';
    """
    
    db.session.execute(text(create_messages_table_sql))
    db.session.commit()
    print("AI消息表创建成功")
    
    # 3. 添加AI助手权限
    ai_permissions = [
        {
            'name': 'AI助手使用',
            'code': 'ai:assistant',
            'type': 'menu',
            'description': '使用AI助手功能'
        },
        {
            'name': 'AI会话管理',
            'code': 'ai:session',
            'type': 'button',
            'description': '管理AI会话'
        },
        {
            'name': 'AI消息查看',
            'code': 'ai:message:view',
            'type': 'button',
            'description': '查看AI消息'
        }
    ]
    
    for perm_data in ai_permissions:
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
    
    # 4. 添加AI助手菜单（一级菜单）
    ai_menu = Menu(
        parent_id=0,
        name='AIAssistant',
        path='/ai-assistant',
        component='AIAssistantView',
        redirect='',
        icon='ChatLineRound',
        title='AI助手',
        hidden=False,
        always_show=False,
        keep_alive=True,
        sort=3,  # 放在知识资产后面，系统配置前面
        type='menu',
        permission='ai:assistant',
        status=1
    )
    db.session.add(ai_menu)
    db.session.commit()
    print(f"添加菜单: AI助手 (ID: {ai_menu.id}, Sort: {ai_menu.sort})")
    
    # 5. 更新其他菜单的排序
    # 知识资产保持sort=2
    # AI助手sort=3
    # 系统配置改为sort=4
    system_menu = Menu.query.filter_by(name='System').first()
    if system_menu:
        system_menu.sort = 4
        print(f"更新系统配置菜单排序: {system_menu.sort}")
    
    db.session.commit()
    
    # 6. 为所有角色重新分配菜单
    print("\n重新分配菜单给角色:")
    admin_role = Role.query.filter_by(code='admin').first()
    user_role = Role.query.filter_by(code='user').first()
    
    if admin_role:
        all_menus = Menu.query.all()
        admin_role.menus = all_menus
        print(f"  管理员角色: 分配 {len(all_menus)} 个菜单")
    
    if user_role:
        # 普通用户分配所有菜单（不包括系统配置的子菜单）
        user_menus = Menu.query.filter(
            ~Menu.name.in_(['Users', 'Roles', 'Menus', 'LLMConfigs', 'Logs'])
        ).all()
        # 加上AI助手菜单
        if ai_menu and ai_menu not in user_menus:
            user_menus.append(ai_menu)
        user_role.menus = user_menus
        print(f"  普通用户角色: 分配 {len(user_menus)} 个菜单")
    
    db.session.commit()
    
    # 7. 为角色分配AI权限
    if admin_role:
        ai_perms = Permission.query.filter(Permission.code.like('ai:%')).all()
        for perm in ai_perms:
            if perm not in admin_role.permissions:
                admin_role.permissions.append(perm)
        print(f"  管理员角色: 分配 {len(ai_perms)} 个AI权限")
    
    if user_role:
        ai_perms = Permission.query.filter(Permission.code.like('ai:%')).all()
        for perm in ai_perms:
            if perm not in user_role.permissions:
                user_role.permissions.append(perm)
        print(f"  普通用户角色: 分配 {len(ai_perms)} 个AI权限")
    
    db.session.commit()
    
    # 8. 显示更新后的菜单结构
    print("\n=== 更新后的菜单结构 ===")
    top_menus = Menu.query.filter_by(parent_id=0).order_by(Menu.sort.asc()).all()
    for menu in top_menus:
        print(f"\n【{menu.title}】({menu.icon}) - Sort: {menu.sort}")
        children = Menu.query.filter_by(parent_id=menu.id).order_by(Menu.sort.asc()).all()
        if children:
            for child in children:
                print(f"  - {child.title}: {child.path} ({child.icon})")
        else:
            print(f"  (直接访问: {menu.path})")
    
    print("\nAI助手功能添加完成！")
