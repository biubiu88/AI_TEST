# 数据库菜单和权限更新说明

## 更新内容

已成功在数据库中添加了用例评审功能相关的菜单和权限。

## 添加的菜单

### 用例评审菜单
- **菜单ID**: 28
- **菜单名称**: Reviews
- **菜单标题**: 用例评审
- **路由路径**: `/testing/reviews`
- **图标**: Checked
- **父菜单**: Testing (ID: 11)
- **排序**: 4

## 添加的权限

### 评审管理权限 (10个)

| ID | 权限名称 | 权限编码 | 类型 | 说明 |
|----|---------|---------|------|------|
| 48 | 评审查看 | review:view | button | 查看评审列表和详情 |
| 49 | 评审新增 | review:create | button | 新增评审记录 |
| 50 | 评审编辑 | review:edit | button | 编辑评审记录 |
| 51 | 评审删除 | review:delete | button | 删除评审记录 |
| 52 | 评审提交 | review:submit | button | 提交评审结果 |
| 53 | 评审评论 | review:comment | button | 添加评审评论 |
| 54 | 评审模板查看 | review:template:view | button | 查看评审模板 |
| 55 | 评审模板新增 | review:template:create | button | 新增评审模板 |
| 56 | 评审模板编辑 | review:template:edit | button | 编辑评审模板 |
| 57 | 评审模板删除 | review:template:delete | button | 删除评审模板 |

## 权限分配

### 管理员角色 (admin)
- **分配权限**: 所有10个评审权限
- **分配菜单**: 用例评审菜单
- **总权限数**: 46个

### 普通用户角色 (user)
- **分配权限**: 6个基本评审权限
  - review:view (评审查看)
  - review:create (评审新增)
  - review:edit (评审编辑)
  - review:submit (评审提交)
  - review:comment (评审评论)
  - review:template:view (评审模板查看)
- **分配菜单**: 用例评审菜单
- **总权限数**: 28个

## 菜单结构

```
Testing (测试模块 - 目录)
├── TestCases (测试用例) - Sort: 1
├── Generate (生成用例) - Sort: 2
├── Requirements (需求管理) - Sort: 3
└── Reviews (用例评审) - Sort: 4 ← 新增
```

## 使用说明

### 访问评审功能

1. **登录系统**
   - 管理员账号: admin / admin123
   - 普通用户账号: testuser / 123456

2. **导航到评审页面**
   - 在左侧菜单中找到"测试模块"目录
   - 点击"用例评审"菜单项
   - 或直接访问: `/testing/reviews`

3. **权限控制**
   - 管理员可以执行所有评审操作
   - 普通用户可以查看、创建、编辑评审，但无法删除评审和模板

### 权限编码使用

在前端组件中使用权限指令：

```vue
<!-- 按钮级权限控制 -->
<el-button v-permission="'review:create'">创建评审</el-button>
<el-button v-permission="'review:edit'">编辑评审</el-button>
<el-button v-permission="'review:delete'">删除评审</el-button>
<el-button v-permission="'review:comment'">添加评论</el-button>

<!-- 模板权限 -->
<el-button v-permission="'review:template:create'">新建模板</el-button>
<el-button v-permission="'review:template:edit'">编辑模板</el-button>
<el-button v-permission="'review:template:delete'">删除模板</el-button>
```

在脚本中判断权限：

```javascript
import { hasPermission } from '@/utils/permission'

// 判断是否有评审查看权限
if (hasPermission('review:view')) {
  // 显示评审内容
}

// 判断是否有评审删除权限
if (hasPermission('review:delete')) {
  // 显示删除按钮
}
```

## 数据库脚本

### 更新脚本
- 文件路径: `backend/add_review_menu_permissions.py`
- 功能: 添加评审相关的菜单和权限，并自动分配给角色

### 验证脚本

```bash
cd backend
python -c "
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'testcase_generator'),
    'charset': 'utf8mb4'
}

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

# 查看评审菜单
cursor.execute(\"SELECT * FROM menus WHERE path = '/testing/reviews'\")
print('评审菜单:', cursor.fetchone())

# 查看评审权限
cursor.execute(\"SELECT * FROM permissions WHERE code LIKE 'review:%'\")
print('评审权限:', cursor.fetchall())

conn.close()
"
```

## 注意事项

1. **角色权限更新**: 如果已有用户登录，需要重新登录才能看到新的菜单和权限
2. **权限缓存**: 前端权限状态存储在 Pinia store 中，刷新页面后会重新加载最新权限
3. **菜单排序**: 评审菜单排在测试模块的第4位，可以根据需要调整 sort 值
4. **权限扩展**: 如需添加新的评审权限，可以参考现有的权限编码规范（review:*）

## 后续操作

1. **测试菜单显示**: 登录系统，检查左侧菜单是否显示"用例评审"菜单
2. **测试权限控制**: 使用不同角色的账号登录，验证权限控制是否生效
3. **测试功能**: 测试评审功能的各项操作是否正常
4. **调整权限**: 根据实际需求调整角色权限分配

## 回滚操作

如果需要回滚，执行以下SQL：

```sql
-- 删除评审菜单
DELETE FROM role_menus WHERE menu_id = 28;
DELETE FROM menus WHERE id = 28;

-- 删除评审权限
DELETE FROM role_permissions WHERE permission_id BETWEEN 48 AND 57;
DELETE FROM permissions WHERE id BETWEEN 48 AND 57;
```

## 更新日志

- **2025-01-25**: 初始版本，添加评审相关的菜单和权限
- 添加10个评审权限
- 添加1个评审菜单
- 为管理员和普通用户角色分配相应权限
