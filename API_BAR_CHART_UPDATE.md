# API调用趋势柱状图功能更新说明

## 功能概述

将首页的API调用趋势图从折线图改为柱状图，并重新定义三种时间范围：
1. **月度**: 显示当前月份每天的数据（1号到月底）
2. **季度**: 显示一年四个季度（一季度、二季度、三季度、四季度）
3. **年度**: 显示从2026年开始的年份

## 主要修改

### 1. 图表类型变更

#### 从折线图到柱状图
```javascript
// 修改前
type: 'line',
smooth: true,

// 修改后
type: 'bar',
```

#### 移除平滑曲线
- 删除了 `smooth: true` 属性
- 删除了 `areaStyle` 区域填充样式

#### 添加圆角样式
```javascript
itemStyle: {
  color: '#409eff',
  borderRadius: [4, 4, 0, 0]  // 添加圆角
}
```

### 2. Tooltip类型变更

```javascript
// 修改前
tooltip: {
  trigger: 'axis',
  axisPointer: {
    type: 'cross',
    label: {
      backgroundColor: '#6a7985'
    }
  }
}

// 修改后
tooltip: {
  trigger: 'axis',
  axisPointer: {
    type: 'shadow'  // 改为阴影指示器
  }
}
```

### 3. 时间范围重新定义

#### 月度统计 (month)
```javascript
// 修改前：显示最近30天
for (let i = 29; i >= 0; i--) {
  const date = new Date(today)
  date.setDate(date.getDate() - i)
  const dateStr = date.toISOString().split('T')[0]
  dateLabels.push(dateStr)
}

// 修改后：显示当前月份每天（1号到月底）
const year = today.getFullYear()
const month = today.getMonth()
const daysInMonth = new Date(year, month + 1, 0).getDate()

for (let day = 1; day <= daysInMonth; day++) {
  const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  dateLabels.push(dateStr)
}
```

**特点**:
- 显示当前月份的所有天数
- 标签格式: `YYYY-MM-DD` (如: 2025-01-25)
- 数据点: 28-31个（根据月份）

#### 季度统计 (quarter)
```javascript
// 修改前：显示最近3个月，按周统计
for (let i = 11; i >= 0; i--) {
  const date = new Date(today)
  date.setDate(date.getDate() - (i * 7))
  // 按周统计...
}

// 修改后：显示一年四个季度
const quarters = [
  { name: '一季度', start: new Date(currentYear, 0, 1), end: new Date(currentYear, 2, 31) },
  { name: '二季度', start: new Date(currentYear, 3, 1), end: new Date(currentYear, 5, 30) },
  { name: '三季度', start: new Date(currentYear, 6, 1), end: new Date(currentYear, 8, 30) },
  { name: '四季度', start: new Date(currentYear, 9, 1), end: new Date(currentYear, 11, 31) }
]

quarters.forEach(quarter => {
  dateLabels.push(quarter.name)
  dateMap[quarter.name] = { total: 0, success: 0, fail: 0, startDate: quarter.start, endDate: quarter.end }
})
```

**特点**:
- 显示当前年度的四个季度
- 标签格式: `一季度`、`二季度`、`三季度`、`四季度`
- 数据点: 4个
- 季度划分:
  - 一季度: 1月1日 - 3月31日
  - 二季度: 4月1日 - 6月30日
  - 三季度: 7月1日 - 9月30日
  - 四季度: 10月1日 - 12月31日

#### 年度统计 (year)
```javascript
// 修改前：显示最近12个月
for (let i = 11; i >= 0; i--) {
  const date = new Date(today.getFullYear(), today.getMonth() - i, 1)
  const dateStr = `${date.getFullYear()}/${date.getMonth() + 1}`
  // ...
}

// 修改后：显示从2026年开始的年份
const startYear = 2026
for (let year = startYear; year <= currentYear; year++) {
  const dateStr = `${year}年`
  dateLabels.push(dateStr)
  dateMap[dateStr] = { total: 0, success: 0, fail: 0, startDate: new Date(year, 0, 1), endDate: new Date(year, 11, 31) }
}
```

**特点**:
- 显示从2026年开始到当前年份的所有年份
- 标签格式: `2026年`、`2027年`、`2028年`...
- 数据点: 根据当前年份动态计算
- 如果当前年份是2025年，则不显示任何数据（因为startYear是2026）

### 4. X轴标签调整

```javascript
// 修改前
axisLabel: {
  rotate: timeRange === 'year' ? 0 : 0,
  interval: timeRange === 'month' ? 4 : timeRange === 'quarter' ? 0 : 0
}

// 修改后
axisLabel: {
  rotate: timeRange === 'month' ? 45 : 0,  // 月度标签旋转45度
  interval: timeRange === 'month' ? 2 : 0   // 月度每2天显示一个标签
}
```

**特点**:
- 月度视图：标签旋转45度，每2天显示一个标签
- 季度视图：标签不旋转，全部显示
- 年度视图：标签不旋转，全部显示

### 5. 统计逻辑更新

#### 月度统计
```javascript
if (timeRange === 'month') {
  const dateStr = log.created_at.split('T')[0]
  if (dateMap.hasOwnProperty(dateStr)) {
    dateMap[dateStr].total++
    if (log.status === 'success') {
      dateMap[dateStr].success++
    } else if (log.status === 'fail' || log.status === 'error') {
      dateMap[dateStr].fail++
    }
  }
}
```

#### 季度统计
```javascript
else if (timeRange === 'quarter') {
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
}
```

#### 年度统计
```javascript
else if (timeRange === 'year') {
  const year = logDate.getFullYear()
  const dateStr = `${year}年`
  if (dateMap.hasOwnProperty(dateStr)) {
    dateMap[dateStr].total++
    if (log.status === 'success') {
      dateMap[dateStr].success++
    } else if (log.status === 'fail' || log.status === 'error') {
      dateMap[dateStr].fail++
    }
  }
}
```

## 功能展示

### 月度视图（柱状图）
```
API调用趋势  [月度] [季度] [年度]  [成功] [失败]
┌─────────────────────────────────────────────────┐
│  ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐     │
│  │██│ │██│ │██│ │██│ │██│ │██│ │██│ │██│ ... │
│  ├──┤ ├──┤ ├──┤ ├──┤ ├──┤ ├──┤ ├──┤ ├──┤     │
│  │██│ │██│ │██│ │██│ │██│ │██│ │██│ │██│     │
│  ├──┤ ├──┤ ├──┤ ├──┤ ├──┤ ├──┤ ├──┤ ├──┤     │
│  │██│ │██│ │██│ │██│ │██│ │██│ │██│ │██│     │
│  └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘ └──┘     │
│  01/01 01/03 01/05 01/07 01/09 01/11 01/13    │
└─────────────────────────────────────────────────┘
```

### 季度视图（柱状图）
```
API调用趋势  [月度] [季度] [年度]  [成功] [失败]
┌─────────────────────────────────────────────────┐
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐                   │
│  │████│ │████│ │████│ │████│                   │
│  │███│ │███│ │███│ │███│                   │
│  │██│ │██│ │██│ │██│                   │
│  │█│ │█│ │█│ │█│                   │
│  └────┘ └────┘ └────┘ └────┘                   │
│  一季度 二季度 三季度 四季度                   │
└─────────────────────────────────────────────────┘
```

### 年度视图（柱状图）
```
API调用趋势  [月度] [季度] [年度]  [成功] [失败]
┌─────────────────────────────────────────────────┐
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐                   │
│  │████│ │████│ │████│ │████│                   │
│  │███│ │███│ │███│ │███│                   │
│  │██│ │██│ │██│ │██│                   │
│  │█│ │█│ │█│ │█│                   │
│  └────┘ └────┘ └────┘ └────┘                   │
│  2026年 2027年 2028年 2029年                   │
└─────────────────────────────────────────────────┘
```

## 图表特性

### 柱状图优势
- ✅ 更直观的数据对比
- ✅ 清晰的数量差异
- ✅ 适合离散数据展示
- ✅ 圆角设计更美观

### 三种颜色
- **蓝色 (#409eff)**: 总调用
- **绿色 (#67c23a)**: 成功
- **红色 (#f56c6c)**: 失败

### 交互特性
- ✅ 鼠标悬停显示详细数据
- ✅ 阴影指示器
- ✅ 图例说明
- ✅ 响应式设计

## 数据说明

### 月度数据
- **时间范围**: 当前月份的1号到最后一天
- **统计粒度**: 按天统计
- **标签格式**: `YYYY-MM-DD`
- **X轴**: 旋转45度，每2天显示一个

### 季度数据
- **时间范围**: 当前年度的四个季度
- **统计粒度**: 按季度统计
- **标签格式**: `一季度`、`二季度`、`三季度`、`四季度`
- **X轴**: 不旋转，全部显示

### 年度数据
- **时间范围**: 从2026年开始到当前年份
- **统计粒度**: 按年统计
- **标签格式**: `2026年`、`2027年`、`2028年`...
- **X轴**: 不旋转，全部显示

## 文件修改清单

### 修改的文件
- **`vue_web/src/views/DashboardView.vue`**
  - ✅ 添加 `currentYear` 变量
  - ✅ 修改月度逻辑：从最近30天改为当前月份每天
  - ✅ 修改季度逻辑：从按周统计改为按季度统计
  - ✅ 修改年度逻辑：从最近12个月改为从2026年开始
  - ✅ 修改图表类型：从折线图改为柱状图
  - ✅ 修改tooltip类型：从cross改为shadow
  - ✅ 移除平滑曲线和区域填充
  - ✅ 添加圆角样式
  - ✅ 调整X轴标签旋转和间隔
  - ✅ 更新统计逻辑

### 新建的文件
- **`update_dashboard.py`** - Python更新脚本
- **`API_BAR_CHART_UPDATE.md`** - 功能说明文档

## 使用说明

### 切换时间范围
1. 在首页找到 "API调用趋势" 图表
2. 点击图表标题右侧的按钮组
3. 选择 "月度"、"季度" 或 "年度"
4. 图表自动更新显示对应时间范围的柱状图

### 查看数据
- 鼠标悬停在柱子上查看详细数据
- 图例显示三条柱子的含义
- 右上角标签显示成功/失败总数

## 注意事项

1. **年度数据**
   - 如果当前年份早于2026年，年度视图将不显示任何数据
   - 只有从2026年开始有年份数据才会显示

2. **月度数据**
   - 只显示当前月份的数据
   - 如果当前月份还没有数据，将显示空柱状图

3. **季度数据**
   - 显示当前年度的四个季度
   - 如果当前年度还没有结束，部分季度可能为0

## 后续优化建议

1. **自定义年份范围**
   - 添加年份选择器
   - 支持用户自定义起始年份

2. **数据对比**
   - 支持同比、环比对比
   - 显示增长率/下降率

3. **更多统计维度**
   - 按模块统计
   - 按用户统计
   - 按接口统计

4. **交互优化**
   - 点击柱子跳转到详情页
   - 支持柱子拖拽排序
   - 数据导出功能

## 兼容性

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 更新记录

- **2025-01-25**: 初始版本发布
  - 图表类型从折线图改为柱状图
  - 重新定义三种时间范围
  - 优化图表样式和交互
  - 添加圆角和阴影效果
