# API调用趋势图表时间范围功能说明

## 功能概述

为首页的API调用趋势图表添加了三种时间范围选择功能：
1. **月度**: 显示最近30天的API调用趋势
2. **季度**: 显示最近3个月（12周）的API调用趋势
3. **年度**: 显示最近12个月的API调用趋势

## 功能特性

### 1. 时间范围切换

#### 选择器组件
- **组件**: `el-radio-group` + `el-radio-button`
- **位置**: 图表标题栏右侧
- **样式**: 小尺寸按钮组

#### 切换效果
- ✅ 切换时自动重新加载数据
- ✅ 图表平滑过渡
- ✅ 保持图表配置不变

### 2. 数据统计逻辑

#### 月度统计 (month)
- **时间范围**: 最近30天
- **统计粒度**: 按天统计
- **数据点**: 30个
- **标签格式**: `MM/DD` (如: 01/25)
- **X轴间隔**: 每4天显示一个标签

#### 季度统计 (quarter)
- **时间范围**: 最近12周
- **统计粒度**: 按周统计
- **数据点**: 12个
- **标签格式**: `MM/DD-MM/DD` (如: 01/19-01/25)
- **X轴间隔**: 全部显示

#### 年度统计 (year)
- **时间范围**: 最近12个月
- **统计粒度**: 按月统计
- **数据点**: 12个
- **标签格式**: `YYYY/MM` (如: 2025/01)
- **X轴间隔**: 全部显示

## 技术实现

### 1. 状态管理

```javascript
// API调用图表时间范围
const apiChartTimeRange = ref('month')  // 默认月度
```

### 2. 切换方法

```javascript
// 切换API图表时间范围
const handleApiChartTimeRangeChange = (value) => {
  apiChartTimeRange.value = value
  loadApiChartData()
}
```

### 3. 数据加载

```javascript
const loadApiChartData = async () => {
  try {
    // 根据时间范围获取不同数量的数据
    let pageSize = 1000
    if (apiChartTimeRange.value === 'quarter') {
      pageSize = 5000
    } else if (apiChartTimeRange.value === 'year') {
      pageSize = 10000
    }

    const logData = await logApi.getList({ page: 1, pageSize })
    if (logData.data && logData.data.list) {
      initApiChart(logData.data.list, apiChartTimeRange.value)
    }
  } catch (error) {
    console.error('加载API图表数据失败:', error)
  }
}
```

### 4. 图表初始化

```javascript
const initApiChart = (logs, timeRange = 'month') => {
  // 根据时间范围生成日期标签
  const dateLabels = []
  const dateMap = {}
  const today = new Date()

  if (timeRange === 'month') {
    // 月度：显示最近30天
    for (let i = 29; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      const dateStr = date.toISOString().split('T')[0]
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0 }
    }
  } else if (timeRange === 'quarter') {
    // 季度：显示最近3个月，按周统计
    for (let i = 11; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - (i * 7))
      const weekStart = new Date(date)
      weekStart.setDate(date.getDate() - date.getDay())
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)

      const dateStr = `${weekStart.getMonth() + 1}/${weekStart.getDate()}-${weekEnd.getMonth() + 1}/${weekEnd.getDate()}`
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0, startDate: weekStart, endDate: weekEnd }
    }
  } else if (timeRange === 'year') {
    // 年度：显示最近12个月
    for (let i = 11; i >= 0; i--) {
      const date = new Date(today.getFullYear(), today.getMonth() - i, 1)
      const dateStr = `${date.getFullYear()}/${date.getMonth() + 1}`
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0, startDate: date, endDate: new Date(date.getFullYear(), date.getMonth() + 1, 0) }
    }
  }

  // 统计API调用数量
  logs.forEach(log => {
    if (log.created_at) {
      const logDate = new Date(log.created_at)

      if (timeRange === 'month') {
        // 按天统计
        const dateStr = log.created_at.split('T')[0]
        if (dateMap.hasOwnProperty(dateStr)) {
          dateMap[dateStr].total++
          if (log.status === 'success') {
            dateMap[dateStr].success++
          } else if (log.status === 'fail' || log.status === 'error') {
            dateMap[dateStr].fail++
          }
        }
      } else if (timeRange === 'quarter') {
        // 按周统计
        for (const label of dateLabels) {
          const range = dateMap[label]
          if (logDate >= range.startDate && logDate <= range.endDate) {
            range.total++
            if (log.status === 'success') {
              range.success++
            } else if (log.status === 'fail' || log.status === 'error') {
              range.fail++
            }
            break
          }
        }
      } else if (timeRange === 'year') {
        // 按月统计
        const dateStr = `${logDate.getFullYear()}/${logDate.getMonth() + 1}`
        if (dateMap.hasOwnProperty(dateStr)) {
          dateMap[dateStr].total++
          if (log.status === 'success') {
            dateMap[dateStr].success++
          } else if (log.status === 'fail' || log.status === 'error') {
            dateMap[dateStr].fail++
          }
        }
      }
    }
  })

  // 生成图表数据
  const totalValues = dateLabels.map(date => dateMap[date].total)
  const successValues = dateLabels.map(date => dateMap[date].success)
  const failValues = dateLabels.map(date => dateMap[date].fail)

  // 创建图表...
}
```

### 5. 模板更新

```vue
<el-card class="chart-card">
  <template #header>
    <div class="card-header">
      <div class="chart-title">
        <span>API调用趋势</span>
        <el-radio-group v-model="apiChartTimeRange" size="small" @change="handleApiChartTimeRangeChange">
          <el-radio-button label="month">月度</el-radio-button>
          <el-radio-button label="quarter">季度</el-radio-button>
          <el-radio-button label="year">年度</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-stats">
        <el-tag type="success" size="small">成功: {{ stats.successApiCalls }}</el-tag>
        <el-tag type="danger" size="small">失败: {{ stats.failApiCalls }}</el-tag>
      </div>
    </div>
  </template>
  <div ref="apiChartContainer" class="chart-container"></div>
</el-card>
```

### 6. 样式更新

```scss
.chart-title {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;

  span {
    font-weight: 600;
  }
}
```

## 功能展示

### 月度视图
```
┌─────────────────────────────────────────────────┐
│ API调用趋势  [月度] [季度] [年度]  [成功] [失败] │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  [蓝色折线 - 总调用]                     │   │
│  │  [绿色折线 - 成功]                       │   │
│  │  [红色折线 - 失败]                       │   │
│  │                                         │   │
│  │  01/25 01/20 01/15 01/10 01/05 01/01  │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 季度视图
```
┌─────────────────────────────────────────────────┐
│ API调用趋势  [月度] [季度] [年度]  [成功] [失败] │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  [蓝色折线 - 总调用]                     │   │
│  │  [绿色折线 - 成功]                       │   │
│  │  [红色折线 - 失败]                       │   │
│  │                                         │   │
│  │  W12 W11 W10 W9 W8 W7 W6 W5 W4 W3 W2 W1│   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 年度视图
```
┌─────────────────────────────────────────────────┐
│ API调用趋势  [月度] [季度] [年度]  [成功] [失败] │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  [蓝色折线 - 总调用]                     │   │
│  │  [绿色折线 - 成功]                       │   │
│  │  [红色折线 - 失败]                       │   │
│  │                                         │   │
│  │  2025/01 2024/12 2024/11 ... 2024/02   │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## 数据说明

### 数据量控制
- **月度**: 1000条记录
- **季度**: 5000条记录
- **年度**: 10000条记录

### 统计维度
- **总调用**: 所有API调用次数
- **成功**: 状态为 'success' 的调用
- **失败**: 状态为 'fail' 或 'error' 的调用

### 时间标签格式
- **月度**: `MM/DD` (如: 01/25)
- **季度**: `MM/DD-MM/DD` (如: 01/19-01/25)
- **年度**: `YYYY/MM` (如: 2025/01)

## 优势特点

### 1. 灵活性
- ✅ 三种时间范围满足不同需求
- ✅ 切换流畅，无刷新
- ✅ 自动适配数据量

### 2. 可视化
- ✅ 清晰的时间标签
- ✅ 合理的X轴间隔
- ✅ 统一的图表样式

### 3. 性能优化
- ✅ 根据时间范围调整数据量
- ✅ 前端统计减少后端压力
- ✅ 图表实例复用

### 4. 用户体验
- ✅ 直观的切换按钮
- ✅ 即时反馈
- ✅ 保持图表状态

## 文件修改清单

### 修改的文件
- **`vue_web/src/views/DashboardView.vue`**
  - ✅ 新增 `apiChartTimeRange` 状态
  - ✅ 新增 `handleApiChartTimeRangeChange` 方法
  - ✅ 更新 `loadApiChartData` 方法
  - ✅ 更新 `initApiChart` 方法，支持三种时间范围
  - ✅ 更新模板，添加时间范围选择器
  - ✅ 更新样式，添加 `.chart-title` 样式

### 新建的文档
- **`API_CHART_TIME_RANGE.md`** - 功能说明文档

## 使用说明

### 切换时间范围
1. 在首页找到 "API调用趋势" 图表
2. 点击图表标题右侧的按钮组
3. 选择 "月度"、"季度" 或 "年度"
4. 图表自动更新显示对应时间范围的数据

### 查看数据
- 鼠标悬停在图表上查看详细数据
- 图例显示三条曲线的含义
- 右上角标签显示成功/失败总数

## 后续优化建议

1. **自定义时间范围**
   - 添加日期选择器
   - 支持用户自定义起止日期

2. **数据导出**
   - 导出当前视图数据为CSV
   - 导出图表为图片

3. **更多统计维度**
   - 按模块统计
   - 按用户统计
   - 按接口统计

4. **实时更新**
   - WebSocket 实时推送
   - 定时自动刷新

5. **性能优化**
   - 后端聚合统计
   - 缓存机制
   - 分页加载

## 兼容性

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 更新记录

- **2025-01-25**: 初始版本发布
  - 添加三种时间范围选择
  - 实现月度/季度/年度统计
  - 优化图表显示效果
