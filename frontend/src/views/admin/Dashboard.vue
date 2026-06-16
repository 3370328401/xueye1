<template>
  <div>
    <h2>统计首页</h2>
    <el-row :gutter="16" class="card-gap">
      <el-col :xs="12" :sm="8" :md="6" v-for="c in cards" :key="c.label">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-value" :style="{ color: c.color }">{{ c.value }}</div>
          <div class="stat-label">{{ c.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :md="12">
        <el-card class="card-gap"><div ref="statusRef" class="chart"></div></el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card class="card-gap"><div ref="trendRef" class="chart"></div></el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card class="card-gap"><div ref="bloodRef" class="chart"></div></el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card class="card-gap"><div ref="feedbackRef" class="chart"></div></el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import api from '../../api'

const cards = ref([])
const statusRef = ref()
const trendRef = ref()
const bloodRef = ref()
const feedbackRef = ref()
const charts = []

function renderPie(el, title, data) {
  const chart = echarts.init(el)
  chart.setOption({
    title: { text: title, left: 'center' },
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['50%', '48%'],
        data,
        label: { formatter: '{b}: {c}' },
      },
    ],
  })
  charts.push(chart)
}

function renderBar(el, title, data) {
  const chart = echarts.init(el)
  chart.setOption({
    title: { text: title, left: 'center' },
    tooltip: { trigger: 'item' },
    xAxis: { type: 'category', data: data.map((d) => d.name) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ type: 'bar', data: data.map((d) => d.value), itemStyle: { color: '#c62828' }, barWidth: '45%' }],
  })
  charts.push(chart)
}

function renderLine(el, title, dates, counts) {
  const chart = echarts.init(el)
  chart.setOption({
    title: { text: title, left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dates },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ type: 'line', data: counts, smooth: true, areaStyle: {}, itemStyle: { color: '#e53935' } }],
  })
  charts.push(chart)
}

onMounted(async () => {
  const c = await api.get('/stats/cards')
  cards.value = [
    { label: '用户总数', value: c.total_users, color: '#409eff' },
    { label: '预约总数', value: c.total_appointments, color: '#67c23a' },
    { label: '今日预约数', value: c.today_appointments, color: '#e6a23c' },
    { label: '已完成预约数', value: c.completed_appointments, color: '#67c23a' },
    { label: '团体申报数', value: c.group_applications, color: '#409eff' },
    { label: '待处理反馈数', value: c.pending_feedbacks, color: '#f56c6c' },
    { label: '平均评价分数', value: c.avg_evaluation_score, color: '#c62828' },
  ]

  const [status, trend, blood, feedback] = await Promise.all([
    api.get('/stats/appointment-status'),
    api.get('/stats/daily-trend'),
    api.get('/stats/blood-type'),
    api.get('/stats/feedback-status'),
  ])
  renderPie(statusRef.value, '预约状态分布', status)
  renderLine(trendRef.value, '每日预约趋势', trend.dates, trend.counts)
  renderBar(bloodRef.value, '献血类型统计', blood)
  renderPie(feedbackRef.value, '反馈处理状态统计', feedback)
})

const resize = () => charts.forEach((c) => c.resize())
window.addEventListener('resize', resize)
onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  charts.forEach((c) => c.dispose())
})
</script>

<style scoped>
.stat-card {
  text-align: center;
  margin-bottom: 16px;
}
.stat-value {
  font-size: 30px;
  font-weight: bold;
}
.stat-label {
  margin-top: 6px;
  color: #909399;
}
.chart {
  height: 320px;
}
</style>
