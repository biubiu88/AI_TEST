# -*- coding: utf-8 -*-
import re

# 读取文件
with open('vue_web/src/views/DashboardView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换1: 添加currentYear变量
content = content.replace(
    'const today = new Date()',
    '''const today = new Date()
  const currentYear = today.getFullYear()'''
)

# 替换2: 修改月度逻辑
old_month = '''if (timeRange === 'month') {
    // 月度：显示最近30天
    for (let i = 29; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      const dateStr = date.toISOString().split('T')[0]
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0 }
    }'''

new_month = '''if (timeRange === 'month') {
    // 月度：显示当前月份每天的数据（1号到月底）
    const year = today.getFullYear()
    const month = today.getMonth()
    const daysInMonth = new Date(year, month + 1, 0).getDate()

    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0 }
    }'''

content = content.replace(old_month, new_month)

# 替换3: 修改季度逻辑
old_quarter = '''else if (timeRange === 'quarter') {
    // 季度：显示最近3个月，按周统计
    for (let i = 11; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - (i * 7))
      const weekStart = new Date(date)
      weekStart.setDate(date.getDate() - date.getDay())
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekEnd.getDate() + 6)

      const dateStr = `${weekStart.getMonth() + 1}/${weekStart.getDate()}-${weekEnd.getMonth() + 1}/${weekEnd.getDate()}`
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0, startDate: weekStart, endDate: weekEnd }
    }'''

new_quarter = '''else if (timeRange === 'quarter') {
    // 季度：显示一年四个季度
    const quarters = [
      { name: '一季度', start: new Date(currentYear, 0, 1), end: new Date(currentYear, 2, 31) },
      { name: '二季度', start: new Date(currentYear, 3, 1), end: new Date(currentYear, 5, 30) },
      { name: '三季度', start: new Date(currentYear, 6, 1), end: new Date(currentYear, 8, 30) },
      { name: '四季度', start: new Date(currentYear, 9, 1), end: new Date(currentYear, 11, 31) }
    ]

    quarters.forEach(quarter => {
      dateLabels.push(quarter.name)
      dateMap[quarter.name] = { total: 0, success: 0, fail: 0, startDate: quarter.start, endDate: quarter.end }
    })'''

content = content.replace(old_quarter, new_quarter)

# 替换4: 修改年度逻辑
old_year = '''else if (timeRange === 'year') {
    // 年度：显示最近12个月
    for (let i = 11; i >= 0; i--) {
      const date = new Date(today.getFullYear(), today.getMonth() - i, 1)
      const dateStr = `${date.getFullYear()}/${date.getMonth() + 1}`
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0, startDate: date, endDate: new Date(date.getFullYear(), date.getMonth() + 1, 0) }
    }'''

new_year = '''else if (timeRange === 'year') {
    // 年度：显示从2026年开始的年份
    const startYear = 2026
    for (let year = startYear; year <= currentYear; year++) {
      const dateStr = `${year}年`
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0, startDate: new Date(year, 0, 1), endDate: new Date(year, 11, 31) }
    }'''

content = content.replace(old_year, new_year)

# 替换5: 修改统计逻辑中的季度部分
old_quarter_stats = '''} else if (timeRange === 'quarter') {
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
        }'''

new_quarter_stats = '''} else if (timeRange === 'quarter') {
        // 按季度统计
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
        }'''

content = content.replace(old_quarter_stats, new_quarter_stats)

# 替换6: 修改年度统计逻辑
old_year_stats = '''} else if (timeRange === 'year') {
        // 按月统计
        const dateStr = `${logDate.getFullYear()}/${logDate.getMonth() + 1}`
        if (dateMap.hasOwnProperty(dateStr)) {
          dateMap[dateStr].total++
          if (log.status === 'success') {
            dateMap[dateStr].success++
          } else if (log.status === 'fail' || log.status === 'error') {
            dateMap[dateStr].fail++
          }
        }'''

new_year_stats = '''} else if (timeRange === 'year') {
        // 按年统计
        const year = logDate.getFullYear()
        const dateStr = `${year}年`
        if (dateMap.hasOwnProperty(dateStr)) {
          dateMap[dateStr].total++
          if (log.status === 'success') {
            dateMap[dateStr].success++
          } else if (log.status === 'fail' || log.status === 'error') {
            dateMap[dateStr].fail++
          }
        }'''

content = content.replace(old_year_stats, new_year_stats)

# 替换7: 修改图表类型为柱状图
old_chart_type = '''type: 'line',
        smooth: true,'''

new_chart_type = '''type: 'bar','''

content = content.replace(old_chart_type, new_chart_type)

# 替换8: 修改tooltip类型
old_tooltip = '''tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },'''

new_tooltip = '''tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },'''

content = content.replace(old_tooltip, new_tooltip)

# 替换9: 移除areaStyle
content = re.sub(r'        areaStyle: \{[^}]+\}', '', content, flags=re.MULTILINE | re.DOTALL)

# 替换10: 修改x轴标签旋转和间隔
old_xaxis = '''axisLabel: {
        rotate: timeRange === 'year' ? 0 : 0,
        interval: timeRange === 'month' ? 4 : timeRange === 'quarter' ? 0 : 0
      }'''

new_xaxis = '''axisLabel: {
        rotate: timeRange === 'month' ? 45 : 0,
        interval: timeRange === 'month' ? 2 : 0
      }'''

content = content.replace(old_xaxis, new_xaxis)

# 替换11: 添加圆角样式
old_itemstyle = '''itemStyle: {
          color: '#409eff'
        }'''

new_itemstyle = '''itemStyle: {
          color: '#409eff',
          borderRadius: [4, 4, 0, 0]
        }'''

content = content.replace(old_itemstyle, new_itemstyle)

# 替换12: 修改成功和失败的itemStyle
content = content.replace(
    '''itemStyle: {
          color: '#67c23a'
        }''',
    '''itemStyle: {
          color: '#67c23a',
          borderRadius: [4, 4, 0, 0]
        }'''
)

content = content.replace(
    '''itemStyle: {
          color: '#f56c6c'
        }''',
    '''itemStyle: {
          color: '#f56c6c',
          borderRadius: [4, 4, 0, 0]
        }'''
)

# 替换13: 修改注释
content = content.replace(
    '// 初始化API调用折线图',
    '// 初始化API调用柱状图'
)

# 写入文件
with open('vue_web/src/views/DashboardView.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print("DashboardView.vue has been updated successfully!")
