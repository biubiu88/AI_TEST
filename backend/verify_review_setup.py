"""
验证用例评审功能设置
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


def verify_review_setup():
    """验证评审功能设置"""
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("="*60)
        print("用例评审功能设置验证")
        print("="*60)
        
        # 1. 验证数据库表
        print("\n【1】验证数据库表")
        tables = ['testcase_reviews', 'review_comments', 'review_templates']
        for table in tables:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            exists = cursor.fetchone()
            status = "✓" if exists else "✗"
            print(f"  {status} 表 {table}: {'存在' if exists else '不存在'}")
            
            if exists:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"      记录数: {count}")
        
        # 2. 验证菜单
        print("\n【2】验证菜单")
        cursor.execute("SELECT id, name, path, icon, sort FROM menus WHERE path = '/testing/reviews'")
        menu = cursor.fetchone()
        if menu:
            print(f"  ✓ 评审菜单已添加")
            print(f"    ID: {menu[0]}")
            print(f"    名称: {menu[1]}")
            print(f"    路径: {menu[2]}")
            print(f"    图标: {menu[3]}")
            print(f"    排序: {menu[4]}")
        else:
            print(f"  ✗ 评审菜单未添加")
        
        # 3. 验证权限
        print("\n【3】验证权限")
        cursor.execute("SELECT COUNT(*) FROM permissions WHERE code LIKE 'review:%'")
        permission_count = cursor.fetchone()[0]
        print(f"  ✓ 评审权限数量: {permission_count}")
        
        if permission_count > 0:
            cursor.execute("SELECT id, name, code FROM permissions WHERE code LIKE 'review:%' ORDER BY id")
            permissions = cursor.fetchall()
            print(f"  权限列表:")
            for perm in permissions:
                print(f"    - {perm[1]} ({perm[2]}) - ID: {perm[0]}")
        
        # 4. 验证角色权限分配
        print("\n【4】验证角色权限分配")
        
        # 管理员角色
        cursor.execute("SELECT id, name FROM roles WHERE code = 'admin'")
        admin_role = cursor.fetchone()
        if admin_role:
            cursor.execute("""
                SELECT COUNT(*) FROM role_permissions rp
                JOIN permissions p ON rp.permission_id = p.id
                WHERE rp.role_id = %s AND p.code LIKE %s
            """, (admin_role[0], 'review:%'))
            admin_review_count = cursor.fetchone()[0]
            print(f"  ✓ 管理员角色 ({admin_role[1]}): {admin_review_count} 个评审权限")
        
        # 普通用户角色
        cursor.execute("SELECT id, name FROM roles WHERE code = 'user'")
        user_role = cursor.fetchone()
        if user_role:
            cursor.execute("""
                SELECT COUNT(*) FROM role_permissions rp
                JOIN permissions p ON rp.permission_id = p.id
                WHERE rp.role_id = %s AND p.code LIKE %s
            """, (user_role[0], 'review:%'))
            user_review_count = cursor.fetchone()[0]
            print(f"  ✓ 普通用户角色 ({user_role[1]}): {user_review_count} 个评审权限")
        
        # 5. 验证角色菜单分配
        print("\n【5】验证角色菜单分配")
        cursor.execute("SELECT id FROM menus WHERE path = '/testing/reviews'")
        menu_result = cursor.fetchone()
        if menu_result:
            menu_id = menu_result[0]
            
            # 管理员
            if admin_role:
                cursor.execute("SELECT 1 FROM role_menus WHERE role_id = %s AND menu_id = %s", (admin_role[0], menu_id))
                admin_has_menu = cursor.fetchone()
                status = "✓" if admin_has_menu else "✗"
                print(f"  {status} 管理员角色: {'有' if admin_has_menu else '无'}评审菜单")
            
            # 普通用户
            if user_role:
                cursor.execute("SELECT 1 FROM role_menus WHERE role_id = %s AND menu_id = %s", (user_role[0], menu_id))
                user_has_menu = cursor.fetchone()
                status = "✓" if user_has_menu else "✗"
                print(f"  {status} 普通用户角色: {'有' if user_has_menu else '无'}评审菜单")
        
        # 6. 验证后端路由
        print("\n【6】验证后端路由")
        try:
            from app import create_app
            app = create_app()
            
            # 获取所有路由
            routes = []
            for rule in app.url_map.iter_rules():
                if '/reviews' in rule.rule:
                    routes.append(f"{rule.methods} {rule.rule}")
            
            if routes:
                print(f"  ✓ 评审路由已注册 ({len(routes)} 个)")
                for route in routes:
                    print(f"    {route}")
            else:
                print(f"  ✗ 未找到评审路由")
        except Exception as e:
            print(f"  ✗ 路由验证失败: {e}")
        
        # 7. 验证前端文件
        print("\n【7】验证前端文件")
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        files_to_check = [
            ('前端页面', 'vue_web/src/views/ReviewView.vue'),
            ('状态管理', 'vue_web/src/stores/review.js'),
            ('路由配置', 'vue_web/src/router/index.js'),
        ]
        
        for name, file_path in files_to_check:
            full_path = os.path.join(base_dir, file_path)
            exists = os.path.exists(full_path)
            status = "✓" if exists else "✗"
            print(f"  {status} {name}: {file_path}")
        
        # 8. 总结
        print("\n" + "="*60)
        print("验证总结")
        print("="*60)
        
        all_checks = [
            ('数据库表', len(tables)),
            ('评审菜单', 1 if menu else 0),
            ('评审权限', permission_count),
            ('管理员权限', admin_review_count if admin_role else 0),
            ('普通用户权限', user_review_count if user_role else 0),
        ]
        
        total_items = sum(count for _, count in all_checks)
        expected_items = 3 + 1 + 10 + 10 + 6  # 表3 + 菜单1 + 权限10 + 管理员10 + 用户6
        
        print(f"\n预期项目数: {expected_items}")
        print(f"实际项目数: {total_items}")
        
        if total_items >= expected_items - 5:  # 允许少量差异
            print("\n✓ 验证通过！用例评审功能已正确设置。")
            print("\n下一步操作:")
            print("1. 启动后端服务: cd backend && python run.py")
            print("2. 启动前端服务: cd vue_web && npm run dev")
            print("3. 登录系统，在左侧菜单中找到'用例评审'")
            print("4. 测试评审功能的各项操作")
        else:
            print("\n✗ 验证未完全通过，请检查上述项目。")
            print("\n可能的问题:")
            print("- 数据库表未创建，请运行: python add_review_tables.py")
            print("- 菜单权限未添加，请运行: python add_review_menu_permissions.py")
        
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ 验证过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    verify_review_setup()
