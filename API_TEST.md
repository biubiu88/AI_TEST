# API 测试说明

## 问题修复

### 错误信息
```
加载统计数据失败: TypeError: logApi.getStatistics is not a function
```

### 问题原因
`logApi` 对象中缺少 `getStatistics` 方法。

### 解决方案
在 `vue_web/src/api/index.js` 中添加了 `getStatistics` 方法：

```javascript
export const logApi = {
  getList: (params) => api.get('/logs', { params }),
  getDetail: (id) => api.get(`/logs/${id}`),
  getStatistics: () => api.get('/logs/statistics'),  // 新增
  export: (params) => api.get('/logs/export', { params })
}
```

### API 路径说明
- **后端路由**: `/api/logs/statistics`
- **前端调用**: `logApi.getStatistics()`
- **完整URL**: `http://localhost:5000/api/logs/statistics`

### 后端接口返回数据
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 1234,           // 总日志数
    "today_count": 56,       // 今日日志数
    "success_count": 1100,   // 成功数
    "fail_count": 134,       // 失败数
    "action_stats": [        // 按操作类型统计
      { "action": "create", "count": 100 },
      { "action": "update", "count": 200 }
    ],
    "module_stats": [        // 按模块统计
      { "module": "testcase", "count": 300 },
      { "module": "user", "count": 100 }
    ]
  }
}
```

## 验证步骤

### 1. 检查前端 API 定义
```bash
cd d:/office/web/vue/ai_test/vue_web/src/api
grep -A 5 "export const logApi" index.js
```

### 2. 检查后端路由
```bash
cd d:/office/web/vue/ai_test/backend
grep -A 2 "statistics" app/routes/logs.py
```

### 3. 测试后端接口
```bash
curl -X GET http://localhost:5000/api/logs/statistics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. 检查前端调用
在浏览器控制台中运行：
```javascript
import { logApi } from '@/api'
console.log(typeof logApi.getStatistics)  // 应该输出 "function"
```

## 修复内容

### 修改的文件
- ✅ `vue_web/src/api/index.js` - 添加 `getStatistics` 方法

### 验证结果
- ✅ API 方法已添加
- ✅ 后端接口存在
- ✅ 路径匹配正确

## 后续操作

1. **重启开发服务器**
   ```bash
   cd vue_web
   npm run dev
   ```

2. **刷新浏览器页面**
   - 清除缓存
   - 硬刷新 (Ctrl + Shift + R)

3. **检查控制台**
   - 确认没有错误信息
   - 查看API调用是否成功

4. **验证数据显示**
   - 检查欢迎卡片中的API调用统计
   - 检查API调用趋势图表是否显示

## 可能的其他问题

如果问题仍然存在，请检查：

1. **后端服务是否运行**
   ```bash
   cd backend
   python app.py
   ```

2. **网络连接**
   - 检查后端端口是否正确 (5000)
   - 检查防火墙设置

3. **认证Token**
   - 确认localStorage中有有效的accessToken
   - 检查Token是否过期

4. **CORS问题**
   - 检查后端是否配置了CORS
   - 确认允许的域名

## 联系支持

如果问题仍未解决，请提供：
- 浏览器控制台的完整错误信息
- 网络请求的详细信息 (F12 -> Network)
- 后端服务器的日志
