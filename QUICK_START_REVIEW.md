# 用例评审功能快速启动指南

## 一键启动

### Windows用户

```batch
@echo off
echo ========================================
echo 用例评审功能快速启动
echo ========================================
echo.

cd %~dp0backend
echo [1/4] 创建数据库表...
python add_review_tables.py
echo.

echo [2/4] 添加菜单和权限...
python add_review_menu_permissions.py
echo.

echo [3/4] 验证设置...
python verify_review_setup.py
echo.

echo [4/4] 启动后端服务...
start cmd /k "python run.py"
echo.

echo ========================================
echo 后端服务已启动！
echo 请在另一个终端启动前端服务：
echo cd vue_web && npm run dev
echo ========================================
pause
```

保存为 `start_review.bat` 并运行。

### Linux/Mac用户

```bash
#!/bin/bash
echo "========================================"
echo "用例评审功能快速启动"
echo "========================================"
echo ""

cd backend
echo "[1/4] 创建数据库表..."
python add_review_tables.py
echo ""

echo "[2/4] 添加菜单和权限..."
python add_review_menu_permissions.py
echo ""

echo "[3/4] 验证设置..."
python verify_review_setup.py
echo ""

echo "[4/4] 启动后端服务..."
python run.py &
echo ""

echo "========================================"
echo "后端服务已启动！"
echo "请在另一个终端启动前端服务："
echo "cd vue_web && npm run dev"
echo "========================================"
```

保存为 `start_review.sh` 并运行 `chmod +x start_review.sh && ./start_review.sh`。

## 手动启动步骤

### 步骤1: 创建数据库表
```bash
cd backend
python add_review_tables.py
```

**预期输出**:
```
=== 连接到数据库 testcase_generator ===
创建表: testcase_reviews
创建表: review_comments
创建表: review_templates
插入默认评审模板

==================================================
评审相关表创建完成！
==================================================
```

### 步骤2: 添加菜单和权限
```bash
python add_review_menu_permissions.py
```

**预期输出**:
```
=== 连接到数据库 testcase_generator ===

=== 添加评审权限 ===
  ✓ 添加权限: 评审查看 (review:view)
  ✓ 添加权限: 评审新增 (review:create)
  ...

=== 添加评审菜单 ===
  Testing 目录 ID: 11
  ✓ 添加菜单: Reviews (用例评审)

=== 为管理员角色分配权限 ===
  ✓ 分配权限: review:view
  ...

==================================================
✓ 评审菜单和权限添加完成！
==================================================
```

### 步骤3: 验证设置
```bash
python verify_review_setup.py
```

**预期输出**:
```
============================================================
用例评审功能设置验证
============================================================

【1】验证数据库表
  ✓ 表 testcase_reviews: 存在
  ✓ 表 review_comments: 存在
  ✓ 表 review_templates: 存在

【2】验证菜单
  ✓ 评审菜单已添加

【3】验证权限
  ✓ 评审权限数量: 10

【4】验证角色权限分配
  ✓ 管理员角色: 10 个评审权限
  ✓ 普通用户角色: 6 个评审权限

【5】验证角色菜单分配
  ✓ 管理员角色: 有评审菜单
  ✓ 普通用户角色: 有评审菜单

【6】验证后端路由
  ✓ 评审路由已注册 (19 个)

【7】验证前端文件
  ✓ 前端页面: vue_web/src/views/ReviewView.vue
  ✓ 状态管理: vue_web/src/stores/review.js
  ✓ 路由配置: vue_web/src/router/index.js

============================================================
验证总结
============================================================

✓ 验证通过！用例评审功能已正确设置。
============================================================
```

### 步骤4: 启动后端服务
```bash
python run.py
```

**预期输出**:
```
 * Serving Flask app '__main__'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://0.0.0.0:5000
```

### 步骤5: 启动前端服务
```bash
cd vue_web
npm run dev
```

**预期输出**:
```
  VITE v7.3.0  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## 访问评审功能

### 1. 登录系统
打开浏览器访问: http://localhost:5173

**管理员账号**:
- 用户名: admin
- 密码: admin123

**普通用户账号**:
- 用户名: testuser
- 密码: 123456

### 2. 找到评审菜单
在左侧菜单中:
1. 展开"测试模块"目录
2. 点击"用例评审"菜单项

或直接访问: http://localhost:5173/testing/reviews

### 3. 开始使用
- **创建评审**: 点击"批量创建评审"或"创建评审"
- **提交评审**: 点击"编辑"填写评审信息
- **评审讨论**: 点击"评论"参与讨论
- **查看统计**: 查看顶部统计卡片

## 测试API

运行API测试脚本:
```bash
cd backend
python test_review_api.py
```

**预期输出**:
```
==================================================
测试用例评审功能
==================================================

1. 登录...
✓ 登录成功

2. 获取测试用例列表...
✓ 获取到 5 条测试用例

3. 创建评审...
✓ 创建评审成功

4. 提交评审结果...
✓ 提交评审结果成功

...

==================================================
✓ 所有测试通过！
==================================================
```

## 常见问题

### Q1: 菜单不显示
**A**: 
1. 检查是否已登录
2. 重新登录刷新权限
3. 检查角色是否有菜单权限

### Q2: API调用失败
**A**:
1. 检查后端服务是否启动
2. 检查数据库表是否创建
3. 查看浏览器控制台错误信息

### Q3: 权限不足
**A**:
1. 使用管理员账号登录
2. 检查角色权限配置
3. 运行 `python add_review_menu_permissions.py` 重新分配权限

### Q4: 数据库连接失败
**A**:
1. 检查 `.env` 文件配置
2. 确认MySQL服务是否启动
3. 验证数据库连接信息

## 功能演示

### 创建评审
1. 点击"批量创建评审"
2. 系统为所有测试用例创建评审记录
3. 评审状态为"待评审"

### 提交评审
1. 点击评审记录的"编辑"按钮
2. 选择评审状态（通过/拒绝/需要修改）
3. 给出整体评分（1-5星）
4. 填写详细评分（清晰度、完整性、可执行性、覆盖度）
5. 填写评审意见和改进建议
6. 点击"确定"提交

### 评审讨论
1. 点击评审记录的"评论"按钮
2. 查看历史评论
3. 输入新评论
4. 点击"发送"提交
5. 可以删除自己的评论

### 查看统计
- 总评审数
- 待评审数
- 已通过数
- 已拒绝数
- 平均评分
- 通过率

## 下一步

1. **熟悉功能**: 阅读完整使用文档 `REVIEW_FEATURE.md`
2. **自定义配置**: 根据需求调整评分标准和评审模板
3. **权限调整**: 根据团队需求配置角色权限
4. **扩展功能**: 参考扩展建议实现更多功能

## 技术支持

如遇到问题，请查看:
- 完整文档: `IMPLEMENTATION_SUMMARY.md`
- 使用说明: `REVIEW_FEATURE.md`
- 菜单权限: `MENU_PERMISSIONS_UPDATE.md`

## 快速命令参考

```bash
# 创建数据库表
cd backend && python add_review_tables.py

# 添加菜单权限
cd backend && python add_review_menu_permissions.py

# 验证设置
cd backend && python verify_review_setup.py

# 测试API
cd backend && python test_review_api.py

# 启动后端
cd backend && python run.py

# 启动前端
cd vue_web && npm run dev
```

---

**祝使用愉快！** 🎉
