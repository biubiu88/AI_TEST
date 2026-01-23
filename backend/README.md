# 测试用例生成器 - 后端服务

基于 Python 3.11 + Flask + MySQL 的测试用例生成后端服务。

## 环境要求

- Python 3.11+
- MySQL 5.7+ / 8.0+

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
uv pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置文件
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac

# 编辑 .env 文件，配置数据库连接等信息
```

### 3. 初始化数据库

**方式一：使用 SQL 脚本**
```bash
mysql -h 192.168.40.128 -u root -p < init_db.sql
```

**方式二：使用 Flask CLI**
```bash
# 确保已配置 .env 文件
flask --app run:app init-db
```

# 方式1: 使用Python脚本初始化（推荐）
cd backend
python init_db.py

# 方式2: 使用SQL文件初始化
mysql -u root -p < init_db.sql

### 4. 启动服务

```bash
# 开发模式
python run.py

# 或使用 Flask CLI
flask --app run:app run --host=0.0.0.0 --port=5000
```

服务启动后访问: http://localhost:5000/api/health

## API 接口

| 模块 | 路径 | 说明 |
|------|------|------|
| 需求管理 | `/api/requirements` | 需求文档 CRUD |
| 测试用例 | `/api/testcases` | 测试用例 CRUD |
| AI 生成 | `/api/ai/generate` | AI 生成测试用例 |

## 数据库配置

在 `.env` 文件中配置：

```
MYSQL_HOST=192.168.40.128
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=testcase_generator
```

## AI 配置（可选）

配置 AI API 以启用智能生成测试用例：

```
AI_API_KEY=your-api-key
AI_API_BASE=https://api.siliconflow.cn/v1
AI_MODEL=deepseek-ai/DeepSeek-V3.2
```
