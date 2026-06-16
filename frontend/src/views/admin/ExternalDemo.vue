<template>
  <div>
    <h2>外部系统模拟接口演示</h2>
    <el-alert
      class="card-gap"
      type="info"
      :closable="false"
      title="第一版仅保留接口占位，调用后返回模拟数据并记录到外部接口日志表，用于证明系统结构完整。"
      show-icon
    />
    <el-row :gutter="16" class="card-gap">
      <el-col :xs="24" :sm="12" :md="6" v-for="api_ in apis" :key="api_.type">
        <el-card class="api-card" shadow="hover">
          <h3>{{ api_.title }}</h3>
          <p class="text-muted">{{ api_.desc }}</p>
          <el-button type="primary" :loading="loadingType === api_.type" @click="call(api_)">
            模拟调用
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="lastResponse" class="card-gap">
      <template #header>最近一次调用返回</template>
      <pre class="resp">{{ lastResponse }}</pre>
    </el-card>

    <el-card>
      <template #header>
        <div class="flex">
          <span>外部接口调用日志</span>
          <el-button size="small" @click="loadLogs">刷新</el-button>
        </div>
      </template>
      <el-table :data="logs" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="api_type" label="接口类型" width="140" />
        <el-table-column prop="request" label="请求内容" />
        <el-table-column prop="response" label="返回内容" />
        <el-table-column prop="status" label="状态" width="90" />
        <el-table-column prop="created_at" label="调用时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const apis = [
  { type: 'e-sign', title: '无纸化签署服务', desc: '后期对接电子签名系统', payload: { doc: 'health_survey' } },
  { type: 'blood-system', title: '采供血业务系统', desc: '获取献血历史与检测结果', payload: { id_card: '110101199001011234' } },
  { type: 'wechat', title: '微信公众号', desc: '微信登录与消息推送', payload: { code: 'mock_code' } },
  { type: 'recruit-call', title: '智慧招募呼叫', desc: '推送献血者名单', payload: { donors: ['张三', '李四'] } },
]
const loadingType = ref('')
const lastResponse = ref('')
const logs = ref([])

async function call(item) {
  loadingType.value = item.type
  try {
    const resp = await api.post(`/external/${item.type}`, { payload: item.payload })
    lastResponse.value = JSON.stringify(resp, null, 2)
    ElMessage.success('模拟调用成功')
    loadLogs()
  } finally {
    loadingType.value = ''
  }
}

async function loadLogs() {
  logs.value = await api.get('/external/logs')
}

onMounted(loadLogs)
</script>

<style scoped>
.api-card {
  text-align: center;
  margin-bottom: 16px;
}
.api-card h3 {
  margin: 0 0 8px;
}
.resp {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  overflow: auto;
  margin: 0;
}
.flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
