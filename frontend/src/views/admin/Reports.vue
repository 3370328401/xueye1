<template>
  <div>
    <h2>统计报表导出</h2>
    <el-row :gutter="16" class="card-gap">
      <el-col :span="6"><el-card><el-statistic title="预约总数" :value="summary.appointment_total" /></el-card></el-col>
      <el-col :span="6"><el-card><el-statistic title="团体活动数" :value="summary.group_total" /></el-card></el-col>
      <el-col :span="6"><el-card><el-statistic title="评价数 / 平均总体分" :value="summary.evaluation_total">
        <template #suffix>&nbsp;/ {{ summary.evaluation_avg_overall }}</template>
      </el-statistic></el-card></el-col>
      <el-col :span="6"><el-card><el-statistic title="异常反馈数" :value="summary.feedback_total" /></el-card></el-col>
    </el-row>

    <el-card>
      <template #header>报表导出（CSV，UTF-8，Excel 可直接打开）</template>
      <el-table :data="reports" stripe>
        <el-table-column prop="name" label="报表名称" />
        <el-table-column prop="dimension" label="统计维度" />
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="download(row)">导出</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const summary = ref({
  appointment_total: 0,
  group_total: 0,
  evaluation_total: 0,
  evaluation_avg_overall: 0,
  feedback_total: 0,
})

const reports = [
  { name: '预约统计报表', dimension: '日期/采血点/献血类型/状态', file: 'appointments.csv' },
  { name: '团体单位统计报表', dimension: '单位类型/年度/预约与实际人数', file: 'groups.csv' },
  { name: '排班统计报表', dimension: '工作人员/采血点/车辆/班次', file: 'shifts.csv' },
  { name: '评价统计报表', dimension: '环境/态度/等待/技能/讲解', file: 'evaluations.csv' },
  { name: '异常反馈统计报表', dimension: '反馈类型/状态/采血点', file: 'feedbacks.csv' },
  { name: '消息推送统计报表', dimension: '类型/范围/已读情况', file: 'messages.csv' },
]

async function download(row) {
  try {
    const resp = await api.get(`/reports/${row.file}`, { responseType: 'blob' })
    const blob = new Blob([resp], { type: 'text/csv;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = row.file
    a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('已导出')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

onMounted(async () => {
  summary.value = await api.get('/reports/summary')
})
</script>

<style scoped>
.card-gap {
  margin-bottom: 16px;
}
</style>
