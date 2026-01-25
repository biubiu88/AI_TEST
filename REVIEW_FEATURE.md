# 用例评审功能使用说明

## 功能概述

用例评审功能允许对测试用例进行评审和讨论，提高测试用例质量。主要功能包括：

1. **评审管理**：创建、编辑、删除评审记录
2. **评审评分**：多维度评分（清晰度、完整性、可执行性、覆盖度）
3. **评审评论**：支持多轮讨论和回复
4. **评审模板**：标准化的评审检查点
5. **统计分析**：评审数据的统计和分析

## 数据库初始化

在首次使用前，需要创建评审相关的数据库表：

```bash
cd backend
python add_review_tables.py
```

这将创建以下表：
- `testcase_reviews`：测试用例评审表
- `review_comments`：评审评论表
- `review_templates`：评审模板表

并插入3个默认评审模板：
- 通用测试用例评审模板
- Web应用测试用例评审模板
- API接口测试用例评审模板

## 后端API接口

### 评审管理

#### 获取评审列表
```
GET /api/reviews/list
```

查询参数：
- `page`: 页码
- `per_page`: 每页数量
- `testcase_id`: 测试用例ID
- `reviewer_id`: 评审人ID
- `status`: 评审状态
- `keyword`: 关键词（搜索用例标题）

#### 获取评审详情
```
GET /api/reviews/{review_id}
```

#### 创建评审
```
POST /api/reviews
```

请求体：
```json
{
  "testcase_id": 1
}
```

#### 更新评审（提交评审结果）
```
PUT /api/reviews/{review_id}
```

请求体：
```json
{
  "status": "approved",
  "overall_rating": 4,
  "comments": "测试用例结构清晰，步骤完整",
  "improvement_suggestions": "建议增加边界值测试",
  "clarity_score": 4,
  "completeness_score": 4,
  "feasibility_score": 5,
  "coverage_score": 3
}
```

#### 删除评审
```
DELETE /api/reviews/{review_id}
```

#### 批量创建评审
```
POST /api/reviews/batch
```

请求体：
```json
{
  "testcase_ids": [1, 2, 3, 4, 5]
}
```

### 评审评论

#### 获取评论列表
```
GET /api/reviews/{review_id}/comments
```

#### 添加评论
```
POST /api/reviews/{review_id}/comments
```

请求体：
```json
{
  "content": "同意评审意见，会尽快改进"
}
```

#### 删除评论
```
DELETE /api/reviews/comments/{comment_id}
```

### 评审模板

#### 获取模板列表
```
GET /api/reviews/templates
```

#### 创建模板
```
POST /api/reviews/templates
```

请求体：
```json
{
  "name": "自定义评审模板",
  "description": "适用于特定场景的评审",
  "category": "general",
  "checklist": [
    {"id": 1, "item": "检查项1", "required": true},
    {"id": 2, "item": "检查项2", "required": false}
  ],
  "scoring_criteria": {
    "clarity": {"name": "清晰度", "description": "描述", "max": 5},
    "completeness": {"name": "完整性", "description": "描述", "max": 5}
  }
}
```

### 统计

#### 获取评审统计
```
GET /api/reviews/stats
```

返回数据：
```json
{
  "total": 100,
  "pending": 20,
  "approved": 60,
  "rejected": 10,
  "need_revision": 10,
  "avg_rating": 4.2,
  "approval_rate": 60.0
}
```

## 前端使用

### 访问评审页面

1. 登录系统后，在左侧菜单中找到"用例评审"页面
2. 或者直接访问：`/testing/reviews`

### 创建评审

1. 点击"批量创建评审"按钮，为所有测试用例创建评审记录
2. 或点击"创建评审"按钮，为特定测试用例创建评审

### 提交评审

1. 在评审列表中，点击"编辑"按钮
2. 填写评审信息：
   - 选择评审状态（待评审/通过/拒绝/需要修改）
   - 给出整体评分（1-5分）
   - 给出详细评分（清晰度、完整性、可执行性、覆盖度）
   - 填写评审意见
   - 填写改进建议（可选）
3. 点击"确定"提交评审

### 评审讨论

1. 在评审列表中，点击"评论"按钮
2. 查看历史评论
3. 输入新评论并点击"发送"
4. 可以删除自己发表的评论

## 评审状态说明

- **待评审 (pending)**：评审已创建，等待评审人评审
- **通过 (approved)**：评审通过，测试用例质量符合要求
- **拒绝 (rejected)**：评审未通过，测试用例需要重大修改
- **需要修改 (need_revision)**：评审基本通过，但需要小幅改进

## 评分标准

### 整体评分
- 1分：质量很差，需要完全重写
- 2分：质量较差，需要大量修改
- 3分：质量一般，需要部分修改
- 4分：质量较好，需要小幅改进
- 5分：质量优秀，无需修改

### 详细评分维度

1. **清晰度 (clarity_score)**：用例描述是否清晰易懂
2. **完整性 (completeness_score)**：用例要素是否完整
3. **可执行性 (feasibility_score)**：用例是否可以被执行
4. **覆盖度 (coverage_score)**：用例覆盖范围是否充分

## 测试

运行测试脚本验证功能：

```bash
cd backend
python test_review_api.py
```

## 文件清单

### 后端文件
- `backend/app/models.py`：评审相关数据模型（已合并到统一模型文件）
- `backend/app/routes/review.py`：评审路由和API
- `backend/add_review_tables.py`：数据库表创建脚本
- `backend/test_review_api.py`：API测试脚本

### 前端文件
- `vue_web/src/views/ReviewView.vue`：评审页面
- `vue_web/src/stores/review.js`：评审状态管理
- `vue_web/src/api/index.js`：评审API接口（已更新）

## 注意事项

1. **权限控制**：只有评审人可以编辑和删除自己的评审记录
2. **数据关联**：删除测试用例时会级联删除相关评审记录
3. **评分范围**：所有评分字段为1-5的整数
4. **评论权限**：只能删除自己发表的评论

## 扩展功能建议

1. **评审流程**：支持多级评审流程（初审、复审等）
2. **通知机制**：评审完成后通知相关人员
3. **评审报告**：生成评审报告和改进建议
4. **AI辅助评审**：使用AI自动评审测试用例质量
5. **评审历史**：查看测试用例的评审历史记录
