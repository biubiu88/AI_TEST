"""
检查routes目录下所有路由是否都添加了@log_operation装饰器
"""
import os
import re

routes_dir = 'app/routes'
files_to_check = [
    'knowledge.py', 'llm_config.py', 'mcp.py', 
    'permission.py', 'ai_assistant.py', 'ai.py'
]

print("=" * 80)
print("检查需要添加@log_operation装饰器的路由")
print("=" * 80)

for filename in files_to_check:
    filepath = os.path.join(routes_dir, filename)
    if not os.path.exists(filepath):
        print(f"\n❌ {filename}: 文件不存在")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否导入了log_operation
    has_import = 'from app.middlewares import log_operation' in content or 'from app.middlewares import.*log_operation' in content
    
    # 找到所有路由定义
    route_pattern = r'@[a-z_]+\.route\([^)]+\)'
    routes = re.findall(route_pattern, content)
    
    # 找到所有带log_operation的函数
    decorated_pattern = r'@log_operation\s+def\s+([a-z_]+)\('
    decorated_funcs = re.findall(decorated_pattern, content)
    
    print(f"\n📄 {filename}:")
    print(f"   导入log_operation: {'✅' if has_import else '❌ 需要添加'}")
    print(f"   路由总数: {len(routes)}")
    print(f"   已添加装饰器: {len(decorated_funcs)}")
    
    if len(decorated_funcs) < len(routes):
        print(f"   ⚠️  还有 {len(routes) - len(decorated_funcs)} 个路由需要添加装饰器")
        
        # 找到所有函数定义
        func_pattern = r'def\s+([a-z_]+)\([^)]*\):'
        all_funcs = re.findall(func_pattern, content)
        
        # 过滤掉非路由函数
        route_funcs = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '@' in line and 'route' in line:
                # 向下查找函数定义
                for j in range(i+1, min(i+10, len(lines))):
                    if 'def ' in lines[j]:
                        func_name = re.search(r'def\s+([a-z_]+)\(', lines[j])
                        if func_name:
                            route_funcs.append(func_name.group(1))
                        break
        
        missing = [f for f in route_funcs if f not in decorated_funcs and f not in ['make_response', 'admin_required']]
        if missing:
            print(f"   缺失装饰器的函数: {', '.join(missing[:5])}" + ("..." if len(missing) > 5 else ""))

print("\n" + "=" * 80)
print("总结:")
print("  ✅ 已完成: auth.py, requirement.py, testcase.py, users.py, prompt.py")
print("  🔲 待处理: knowledge.py, llm_config.py, mcp.py, permission.py, ai_assistant.py, ai.py")
print("=" * 80)
