
// 根据时间范围生成日期标签
  const dateLabels = []
  const dateMap = {}
  const today = new Date()
  const currentYear = today.getFullYear()

  if (timeRange === 'month') {
    // 月度：显示当前月份每天的数据（1号到月底）
    const year = today.getFullYear()
    const month = today.getMonth()
    const daysInMonth = new Date(year, month + 1, 0).getDate()

    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0 }
    }
  } else if (timeRange === 'quarter') {
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
    })
  } else if (timeRange === 'year') {
    // 年度：显示从2026年开始的年份
    const startYear = 2026
    for (let year = startYear; year <= currentYear; year++) {
      const dateStr = `${year}年`
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0, startDate: new Date(year, 0, 1), endDate: new Date(year, 11, 31) }
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
        }
      } else if (timeRange === 'year') {
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
        }
      }
    }
  })

  const totalValues = dateLabels.map(date => dateMap[date].total)
  const successValues = dateLabels.map(date => dateMap[date].success)
  const failValues = dateLabels.map(date => dateMap[date].fail)

  // 销毁旧图表
  if (apiChartInstance) {
    apiChartInstance.dispose()
  }

  // 创建新图表 - 柱状图
  apiChartInstance = echarts.init(apiChartContainer.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['总调用', '成功', '失败'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dateLabels,
      axisLabel: {
        rotate: timeRange === 'month' ? 45 : 0,
        interval: timeRange === 'month' ? 2 : 0
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        name: '总调用',
        type: 'bar',
        data: totalValues,
        itemStyle: {
          color: '#409eff',
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '成功',
        type: 'bar',
        data: successValues,
        itemStyle: {
          color: '#67c23a',
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '失败',
        type: 'bar',
        data: failValues,
        itemStyle: {
          color: '#f56c6c',
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  }
  apiChartInstance.setOption(option)

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    apiChartInstance?.resize()
  })
