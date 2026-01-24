# 操作日志系统实现文档

## 一、系统概述

实现了完整的操作日志审计系统,自动记录所有API请求的详细信息,包括用户信息、请求参数、响应状态、客户端环境等。

## 二、数据库设计

### 操作日志表 (operation_logs)

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 用户ID |
| username | String(80) | 用户名 |
| action | String(50) | 操作类型 (login/logout/create/update/delete/query/export/import) |
| module | String(50) | 模块名称 |
| description | String(500) | 操作描述 |
| method | String(10) | 请求方法 (GET/POST/PUT/DELETE) |
| path | String(500) | 请求路径 |
| params | Text | 请求参数JSON |
| status_code | Integer | 响应状态码 |
| response_time | Float | 响应时间(毫秒) |
| error_msg | Text | 错误信息 |
| ip | String(50) | IP地址 |
| user_agent | String(500) | User-Agent |
| browser | String(100) | 浏览器 |
| browser_version | String(50) | 浏览器版本 |
| os | String(100) | 操作系统 |
| os_version | String(50) | 系统版本 |
| device | String(50) | 设备类型 (desktop/mobile/tablet) |
| status | String(20) | 操作状态 (success/fail/error) |
| created_at | DateTime | 创建时间(已索引) |

## 三、后端实现

### 1. 模型定义 (app/models.py)

```python
class OperationLog(db.Model):
    """操作日志模型"""
    __tablename__ = 'operation_logs'
    # ... 字段定义 ...
```

### 2. 日志中间件 (app/middlewares.py)

#### 核心功能:
- **自动日志记录装饰器 `@log_operation`**
- User-Agent 解析 (浏览器、操作系统、设备类型)
- IP地址获取 (支持代理)
- 请求参数记录 (自动过滤敏感信息: password, api_key, token)
- 响应时间统计
- 错误信息捕获

#### 使用示例:
```python
@app.route('/login', methods=['POST'])
@log_operation
def login():
    # 业务逻辑
    pass
```

### 3. 日志路由 (app/routes/logs.py)

#### API接口:

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/logs | GET | 获取日志列表(支持分页、搜索、过滤) |
| /api/logs/<id> | GET | 获取日志详情 |
| /api/logs/export | GET | 导出日志为CSV |
| /api/logs/statistics | GET | 获取日志统计信息 |

#### 查询参数:
- `keyword`: 关键词搜索(用户名、描述、IP)
- `action`: 操作类型过滤
- `module`: 模块过滤
- `status`: 状态过滤
- `startTime`: 开始时间
- `endTime`: 结束时间
- `page`: 页码
- `pageSize`: 每页条数

## 四、前端实现

### 1. 日志列表页面 (LogView.vue)

#### 功能特性:
- **高级搜索**: 关键词、操作类型、模块、状态、时间范围
- **多字段展示**:
  - 基本信息: 用户、操作、模块、描述
  - 请求信息: 方法、路径、状态码、响应时间
  - 客户端信息: IP、浏览器、操作系统、设备类型
- **详情查看**: 弹窗显示完整日志信息
- **数据导出**: CSV格式导出
- **视觉优化**:
  - 状态码颜色标识 (2xx绿色, 4xx黄色, 5xx红色)
  - 响应时间颜色标识 (快绿色, 中黄色, 慢红色)
  - 请求方法类型标签

### 2. 表格字段说明

| 字段 | 宽度 | 特殊处理 |
|------|------|----------|
| ID | 70px | - |
| 用户名 | 100px | - |
| 动作 | 80px | 标签+颜色 |
| 模块 | 100px | - |
| 描述 | 180px+ | 溢出省略 |
| 请求方法 | 90px | 标签+颜色 |
| 请求路径 | 200px+ | 溢出省略 |
| 状态码 | 90px | 标签+颜色 |
| 响应时间 | 100px | 颜色标识 |
| IP地址 | 140px | - |
| 浏览器 | 120px | 含版本号 |
| 操作系统 | 120px | 含版本号 |
| 设备 | 80px | 中文标签 |
| 状态 | 80px | 标签+颜色 |
| 时间 | 170px | - |
| 操作 | 100px | 详情按钮 |

## 五、使用指南

### 1. 数据库初始化

```bash
cd backend
python create_log_table.py
```

### 2. 为接口添加日志记录

```python
from app.middlewares import log_operation

@your_blueprint.route('/your-endpoint', methods=['POST'])
@jwt_required()  # JWT认证装饰器(如需要)
@log_operation   # 日志记录装饰器
def your_function():
    # 业务逻辑
    pass
```

### 3. 前端访问

访问: `http://localhost:5173/system/logs`

### 4. 导出日志

1. 使用前端搜索过滤需要的日志
2. 点击"导出"按钮
3. 下载CSV文件

## 六、技术特点

### 1. 自动化
- 通过装饰器自动记录,无需手动编写日志代码
- 自动解析User-Agent获取浏览器、系统信息
- 自动计算响应时间

### 2. 安全性
- 自动过滤敏感参数 (password, api_key, token)
- 参数长度限制 (最长2000字符)
- 错误信息长度限制 (最长500字符)

### 3. 性能优化
- 异步日志保存(不阻塞主流程)
- 数据库索引优化 (created_at字段)
- 分页查询避免大数据量问题
- 导出限制最多10000条

### 4. 用户体验
- 实时搜索过滤
- 多维度筛选
- 详情弹窗展示
- CSV导出支持Excel直接打开 (UTF-8 BOM)
- 响应时间和状态码颜色可视化

## 七、扩展建议

### 1. 日志清理策略
建议定期清理历史日志:
```python
# 清理90天前的日志
from datetime import datetime, timedelta
cutoff_date = datetime.now() - timedelta(days=90)
OperationLog.query.filter(OperationLog.created_at < cutoff_date).delete()
db.session.commit()
```

### 2. 异步日志保存
对于高并发场景,建议使用Celery等任务队列异步保存日志:
```python
@celery_app.task
def save_log_async(log_data):
    operation_log = OperationLog(**log_data)
    db.session.add(operation_log)
    db.session.commit()
```

### 3. 日志分析
可基于日志数据实现:
- 用户行为分析
- API性能监控
- 异常告警
- 安全审计

### 4. 日志级别
可扩展不同级别的日志:
- DEBUG: 开发调试
- INFO: 一般操作
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

## 八、注意事项

1. **数据库存储**: 日志会持续增长,需要定期清理或归档
2. **性能影响**: 每个请求都会记录日志,高并发时注意数据库性能
3. **敏感信息**: 确保不记录敏感数据(已默认过滤password等)
4. **日志保存失败**: 装饰器已处理异常,不会影响主业务流程
5. **时区问题**: 使用UTC时间,前端展示需要转换为本地时间

## 九、测试验证

### 1. 登录测试
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"account":"admin","password":"admin123"}'
```

### 2. 查询日志
```bash
curl http://localhost:5000/api/logs?page=1&pageSize=10 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 日志统计
```bash
curl http://localhost:5000/api/logs/statistics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 十、相关文件

### 后端文件:
- `backend/app/models.py` - OperationLog模型
- `backend/app/middlewares.py` - 日志中间件
- `backend/app/routes/logs.py` - 日志路由
- `backend/app/routes/auth.py` - 登录接口(示例)
- `backend/create_log_table.py` - 表创建脚本

### 前端文件:
- `vue_web/src/views/LogView.vue` - 日志页面
- `vue_web/src/api/index.js` - API接口定义

## 十一、更新记录

- 2026-01-24: 
  - 实现操作日志模型
  - 实现日志中间件和装饰器
  - 实现日志查询、导出、统计接口
  - 优化前端日志页面,增加更多字段展示
  - 添加User-Agent解析功能
  - 添加响应时间统计
  - 添加CSV导出功能
