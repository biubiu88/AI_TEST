"""
添加用例评审相关的菜单和权限
"""
import pymysql
import os
import sys
from dotenv import load_dotenv

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'testcase_generator'),
    'charset': 'utf8mb4'
}


def add_review_menu_permissions():
    """添加评审相关的菜单和权限"""
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"\n=== 连接到数据库 {DB_CONFIG['database']} ===")
        
        # 1. 添加评审相关权限
        print("\n=== 添加评审权限 ===")
        review_permissions = [
            ('评审查看', 'review:view', 'button', '查看评审列表和详情'),
            ('评审新增', 'review:create', 'button', '新增评审记录'),
            ('评审编辑', 'review:edit', 'button', '编辑评审记录'),
            ('评审删除', 'review:delete', 'button', '删除评审记录'),
            ('评审提交', 'review:submit', 'button', '提交评审结果'),
            ('评审评论', 'review:comment', 'button', '添加评审评论'),
            ('评审模板查看', 'review:template:view', 'button', '查看评审模板'),
            ('评审模板新增', 'review:template:create', 'button', '新增评审模板'),
            ('评审模板编辑', 'review:template:edit', 'button', '编辑评审模板'),
            ('评审模板删除', 'review:template:delete', 'button', '删除评审模板'),
        ]
        
        permission_ids = {}
        for i, (name, code, ptype, description) in enumerate(review_permissions, 1):
            # 检查权限是否已存在
            cursor.execute("SELECT id FROM permissions WHERE code = %s", (code,))
            existing = cursor.fetchone()
            
            if existing:
                permission_ids[code] = existing[0]
                print(f"  权限已存在: {name} ({code}) - ID: {existing[0]}")
            else:
                cursor.execute("""
                    INSERT INTO permissions (name, code, type, description)
                    VALUES (%s, %s, %s, %s)
                """, (name, code, ptype, description))
                permission_id = cursor.lastrowid
                permission_ids[code] = permission_id
                print(f"  ✓ 添加权限: {name} ({code}) - ID: {permission_id}")
        
        # 2. 添加评审菜单
        print("\n=== 添加评审菜单 ===")
        
        # 查找 Testing 目录的 ID
        cursor.execute("SELECT id FROM menus WHERE name = 'Testing' AND type = 'directory'")
        testing_dir = cursor.fetchone()
        
        if not testing_dir:
            print("  ✗ 未找到 Testing 目录，请先创建")
            return
        
        testing_parent_id = testing_dir[0]
        print(f"  Testing 目录 ID: {testing_parent_id}")
        
        # 获取当前最大的 sort 值
        cursor.execute("SELECT MAX(sort) FROM menus WHERE parent_id = %s", (testing_parent_id,))
        max_sort = cursor.fetchone()[0] or 0
        new_sort = max_sort + 1
        
        # 检查菜单是否已存在
        cursor.execute("SELECT id FROM menus WHERE path = '/testing/reviews'")
        existing_menu = cursor.fetchone()
        
        if existing_menu:
            menu_id = existing_menu[0]
            print(f"  菜单已存在: Reviews - ID: {menu_id}")
        else:
            # 插入评审菜单
            cursor.execute("""
                INSERT INTO menus (
                    parent_id, name, path, component, icon, title, 
                    hidden, always_show, keep_alive, sort, type, 
                    permission, status
                ) VALUES (
                    %s, 'Reviews', '/testing/reviews', 'ReviewView', 
                    'Checked', '用例评审', FALSE, FALSE, TRUE, 
                    %s, 'menu', 'review:view', 1
                )
            """, (testing_parent_id, new_sort))
            menu_id = cursor.lastrowid
            print(f"  ✓ 添加菜单: Reviews (用例评审) - ID: {menu_id}")
        
        # 3. 为管理员角色分配所有评审权限
        print("\n=== 为管理员角色分配权限 ===")
        cursor.execute("SELECT id FROM roles WHERE code = 'admin'")
        admin_role = cursor.fetchone()
        
        if admin_role:
            admin_role_id = admin_role[0]
            print(f"  管理员角色 ID: {admin_role_id}")
            
            for permission_id in permission_ids.values():
                # 检查是否已分配
                cursor.execute("""
                    SELECT 1 FROM role_permissions 
                    WHERE role_id = %s AND permission_id = %s
                """, (admin_role_id, permission_id))
                existing = cursor.fetchone()
                
                if not existing:
                    cursor.execute("""
                        INSERT INTO role_permissions (role_id, permission_id)
                        VALUES (%s, %s)
                    """, (admin_role_id, permission_id))
                    print(f"  ✓ 分配权限 ID: {permission_id}")
        else:
            print("  ✗ 未找到管理员角色")
        
        # 4. 为管理员角色分配评审菜单
        if admin_role_id:
            cursor.execute("""
                SELECT 1 FROM role_menus 
                WHERE role_id = %s AND menu_id = %s
            """, (admin_role_id, menu_id))
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute("""
                    INSERT INTO role_menus (role_id, menu_id)
                    VALUES (%s, %s)
                """, (admin_role_id, menu_id))
                print(f"  ✓ 分配菜单: Reviews (ID: {menu_id})")
        
        # 5. 为普通用户角色分配基本权限
        print("\n=== 为普通用户角色分配权限 ===")
        cursor.execute("SELECT id FROM roles WHERE code = 'user'")
        user_role = cursor.fetchone()
        
        if user_role:
            user_role_id = user_role[0]
            print(f"  普通用户角色 ID: {user_role_id}")
            
            # 普通用户的评审权限
            user_permissions = [
                'review:view',
                'review:create',
                'review:edit',
                'review:submit',
                'review:comment',
                'review:template:view'
            ]
            
            for code in user_permissions:
                if code in permission_ids:
                    permission_id = permission_ids[code]
                    cursor.execute("""
                        SELECT 1 FROM role_permissions 
                        WHERE role_id = %s AND permission_id = %s
                    """, (user_role_id, permission_id))
                    existing = cursor.fetchone()
                    
                    if not existing:
                        cursor.execute("""
                            INSERT INTO role_permissions (role_id, permission_id)
                            VALUES (%s, %s)
                        """, (user_role_id, permission_id))
                        print(f"  ✓ 分配权限: {code}")
            
            # 为普通用户分配评审菜单
            cursor.execute("""
                SELECT 1 FROM role_menus 
                WHERE role_id = %s AND menu_id = %s
            """, (user_role_id, menu_id))
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute("""
                    INSERT INTO role_menus (role_id, menu_id)
                    VALUES (%s, %s)
                """, (user_role_id, menu_id))
                print(f"  ✓ 分配菜单: Reviews (ID: {menu_id})")
        else:
            print("  ✗ 未找到普通用户角色")
        
        conn.commit()
        
        print("\n" + "="*50)
        print("✓ 评审菜单和权限添加完成！")
        print("="*50)
        print("\n添加的权限:")
        for name, code, _, _ in review_permissions:
            print(f"  - {name} ({code})")
        print(f"\n添加的菜单:")
        print(f"  - 用例评审 (/testing/reviews)")
        print("\n权限分配:")
        print(f"  - 管理员: 所有评审权限")
        print(f"  - 普通用户: 基本评审权限（查看、创建、编辑、提交、评论、查看模板）")
        print("="*50)
        
    except Exception as e:
        print(f"\n错误: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    add_review_menu_permissions()
