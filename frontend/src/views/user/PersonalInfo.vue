<template>
  <div v-loading="loading">
    <h2>我的献血信息</h2>
    <el-alert
      type="info"
      :closable="false"
      class="card-gap"
      title="以下信息来自微信公众号 / 采供血业务管理系统（演示环境为模拟数据）"
    />

    <el-row :gutter="16" class="card-gap">
      <el-col :span="6"><el-card><el-statistic title="电子献血证编号" :value="0" :formatter="() => info.e_cert_no" /></el-card></el-col>
      <el-col :span="6"><el-card><el-statistic title="累计献血量(ml)" :value="info.total_volume_ml" /></el-card></el-col>
      <el-col :span="6"><el-card><el-statistic title="献血次数" :value="info.donate_count" /></el-card></el-col>
      <el-col :span="6"><el-card><el-statistic title="当前积分" :value="info.points_balance" /></el-card></el-col>
    </el-row>

    <el-card class="card-gap">
      <template #header>个人献血足迹</template>
      <el-table :data="info.traces" stripe>
        <el-table-column prop="seq" label="序号" width="70" />
        <el-table-column prop="donate_date" label="献血时间" width="130" />
        <el-table-column prop="location" label="献血地点" />
        <el-table-column prop="volume_ml" label="献血量(ml)" width="110" />
        <el-table-column prop="blood_type" label="献血类型" width="100" />
        <el-table-column prop="identity" label="身份类型" width="110" />
      </el-table>
    </el-card>

    <el-card class="card-gap">
      <template #header>血液检测结果</template>
      <el-table :data="info.tests" stripe>
        <el-table-column prop="seq" label="序号" width="70" />
        <el-table-column prop="test_date" label="检测时间" width="130" />
        <el-table-column label="检测结果" width="100">
          <template #default="{ row }"><el-tag type="success">{{ row.result }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="detail" label="检测明细" />
      </el-table>
    </el-card>

    <el-card>
      <template #header>血液使用情况</template>
      <el-table :data="info.blood_usage" stripe>
        <el-table-column prop="date" label="日期" width="130" />
        <el-table-column prop="hospital" label="用血单位" />
        <el-table-column prop="usage" label="使用情况" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../../api'

const loading = ref(false)
const info = ref({
  e_cert_no: '',
  total_volume_ml: 0,
  donate_count: 0,
  points_balance: 0,
  blood_usage: [],
  tests: [],
  traces: [],
})

onMounted(async () => {
  loading.value = true
  try {
    info.value = await api.get('/personal/info')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.card-gap {
  margin-bottom: 16px;
}
</style>
