# 日志装饰器添加状态

## 已完成的文件

### 1. auth.py ✅
- [x] register - 用户注册
- [x] login - 用户登录  
- [x] update_profile - 更新个人信息
- [x] change_password - 修改密码
- [x] reset_password - 重置密码
- [x] logout - 用户登出

### 2. requirement.py ✅
- [x] create_requirement - 创建需求
- [x] update_requirement - 更新需求
- [x] delete_requirement - 删除需求

### 3. testcase.py ✅
- [x] create_testcase - 创建测试用例
- [x] create_testcases_batch - 批量创建
- [x] update_testcase - 更新测试用例
- [x] delete_testcase - 删除测试用例
- [x] export_testcases - 导出用例
- [x] import_testcases - 导入用例

### 4. logs.py (日志模块本身不需要)
- 日志查询接口无需记录日志

## 待添加的文件

### 5. users.py 🔲
需要添加:
```python
from app.middlewares import log_operation

@users_bp.route('', methods=['POST'])
@jwt_required()
@log_operation
def create_user():
    ...

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@log_operation
def update_user(user_id):
    ...

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@log_operation
def delete_user(user_id):
    ...
```

### 6. prompt.py 🔲
需要添加:
- create_prompt
- update_prompt  
- delete_prompt

### 7. knowledge.py 🔲
需要添加:
- create_knowledge
- update_knowledge
- delete_knowledge

### 8. llm_config.py 🔲
需要添加:
- create_llm_config
- update_llm_config
- delete_llm_config

### 9. mcp.py 🔲
需要添加:
- create_mcp_config
- update_mcp_config
- delete_mcp_config

### 10. permission.py 🔲
需要添加:
- create_role
- update_role
- delete_role
- create_menu
- update_menu
- delete_menu

### 11. ai_assistant.py 🔲
需要添加:
- create_session
- update_session
- delete_session
- send_message
- delete_message

### 12. ai.py 🔲
需要添加:
- generate - AI生成用例
- parse_document - 解析文档

## 添加装饰器的标准顺序

```python
@路由装饰器
@jwt_required()  # 如果需要认证
@log_operation   # 日志记录
def function_name():
    ...
```

## 注意事项

1. **导入语句**: 在文件开头添加
```python
from flask_jwt_extended import jwt_required
from app.middlewares import log_operation
```

2. **装饰器顺序**: 
   - 路由装饰器在最外层
   - JWT认证在中间
   - log_operation在最内层(紧贴函数定义)

3. **哪些操作需要记录**:
   - ✅ 所有增删改操作 (POST/PUT/DELETE)
   - ✅ 登录/登出等安全操作
   - ✅ 导入/导出操作
   - ⚠️ 查询操作(GET) 可选,根据重要性决定
   - ❌ 健康检查等系统接口不需要

4. **已自动过滤的敏感字段**:
   - password
   - confirmPassword
   - api_key
   - token
