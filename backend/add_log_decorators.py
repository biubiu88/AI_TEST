"""
批量为路由添加日志装饰器
"""
import os
import re

# 需要处理的文件和需要添加装饰器的路由
routes_config = {
    'testcase.py': {
        'import_lines': [
            'from flask_jwt_extended import jwt_required, get_jwt_identity',
            'from app.middlewares import log_operation'
        ],
        'routes': [
            ('POST', '', 'create_testcase'),
            ('PUT', '/<int:testcase_id>', 'update_testcase'),
            ('DELETE', '/<int:testcase_id>', 'delete_testcase'),
            ('POST', '/import', 'import_testcases'),
            ('POST', '/batch-delete', 'batch_delete_testcases'),
        ]
    },
    'users.py': {
        'import_lines': [
            'from app.middlewares import log_operation'
        ],
        'routes': [
            ('POST', '', 'create_user'),
            ('PUT', '/<int:user_id>', 'update_user'),
            ('DELETE', '/<int:user_id>', 'delete_user'),
        ]
    },
    'prompt.py': {
        'import_lines': [
            'from app.middlewares import log_operation'
        ],
        'routes': [
            ('POST', '', 'create_prompt'),
            ('PUT', '/<int:prompt_id>', 'update_prompt'),
            ('DELETE', '/<int:prompt_id>', 'delete_prompt'),
        ]
    },
    'knowledge.py': {
        'import_lines': [
            'from app.middlewares import log_operation'
        ],
        'routes': [
            ('POST', '', 'create_knowledge'),
            ('PUT', '/<int:knowledge_id>', 'update_knowledge'),
            ('DELETE', '/<int:knowledge_id>', 'delete_knowledge'),
        ]
    },
    'llm_config.py': {
        'import_lines': [
            'from app.middlewares import log_operation'
        ],
        'routes': [
            ('POST', '', 'create_llm_config'),
            ('PUT', '/<int:config_id>', 'update_llm_config'),
            ('DELETE', '/<int:config_id>', 'delete_llm_config'),
        ]
    },
    'mcp.py': {
        'import_lines': [
            'from app.middlewares import log_operation'
        ],
        'routes': [
            ('POST', '', 'create_mcp_config'),
            ('PUT', '/<int:config_id>', 'update_mcp_config'),
            ('DELETE', '/<int:config_id>', 'delete_mcp_config'),
        ]
    },
    'permission.py': {
        'import_lines': [
            'from app.middlewares import log_operation'
        ],
        'routes': [
            ('POST', '/roles', 'create_role'),
            ('PUT', '/roles/<int:role_id>', 'update_role'),
            ('DELETE', '/roles/<int:role_id>', 'delete_role'),
            ('POST', '/menus', 'create_menu'),
            ('PUT', '/menus/<int:menu_id>', 'update_menu'),
            ('DELETE', '/menus/<int:menu_id>', 'delete_menu'),
        ]
    },
    'ai_assistant.py': {
        'import_lines': [
            'from app.middlewares import log_operation'
        ],
        'routes': [
            ('POST', '/sessions', 'create_session'),
            ('PUT', '/sessions/<int:session_id>', 'update_session'),
            ('DELETE', '/sessions/<int:session_id>', 'delete_session'),
            ('POST', '/sessions/<int:session_id>/messages', 'send_message'),
            ('DELETE', '/sessions/<int:session_id>/messages/<int:message_id>', 'delete_message'),
        ]
    }
}

print("需要手动为以下路由添加 @log_operation 装饰器:")
print("=" * 80)

for filename, config in routes_config.items():
    print(f"\n文件: {filename}")
    print(f"需要添加的导入:")
    for import_line in config['import_lines']:
        if 'log_operation' in import_line:
            print(f"  {import_line}")
    
    print(f"\n需要添加装饰器的路由 (在@jwt_required()之后):")
    for method, path, func_name in config['routes']:
        print(f"  - {method:6} {path:40} -> {func_name}()")

print("\n" + "=" * 80)
print("\n建议的装饰器添加顺序:")
print("1. @路由装饰器")
print("2. @jwt_required() (如果需要认证)")
print("3. @log_operation (日志记录)")
print("4. def function_name():")
