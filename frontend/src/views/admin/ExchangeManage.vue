<template>
  <div>
    <h2>积分兑换管理</h2>
    <el-card class="card-gap">
      <el-form :inline="true">
        <el-form-item label="状态">
          <el-select v-model="status" clearable placeholder="全部" style="width: 130px">
            <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="load">查询</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="user_name" label="用户" width="110" />
        <el-table-column prop="user_phone" label="手机号" width="140" />
        <el-table-column prop="gift_name" label="礼品" />
        <el-table-column prop="points_cost" label="消耗积分" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="tagType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="190">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="处理" width="260">
          <template #default="{ row }">
            <el-button size="small" @click="setStatus(row, '处理中')" :disabled="row.status !== '待处理'">受理</el-button>
            <el-button size="small" type="success" @click="setStatus(row, '已兑换')" :disabled="!['待处理','处理中'].includes(row.status)">已兑换</el-button>
            <el-button size="small" type="danger" @click="setStatus(row, '已取消')" :disabled="!['待处理','处理中'].includes(row.status)">取消</el-button>
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

const statuses = ['待处理', '处理中', '已兑换', '已取消']
const status = ref('')
const list = ref([])
const loading = ref(false)

function formatTime(t) {
  return t ? new Date(t).toLocaleString() : ''
}
function tagType(s) {
  return { 已兑换: 'success', 已取消: 'info', 处理中: 'warning' }[s] || ''
}

async function load() {
  loading.value = true
  try {
    const params = {}
    if (status.value) params.status = status.value
    list.value = await api.get('/points/exchanges/admin/list', { params })
  } finally {
    loading.value = false
  }
}

async function setStatus(row, s) {
  await api.put(`/points/exchanges/${row.id}/status`, { status: s })
  ElMessage.success('已更新')
  load()
}

onMounted(load)
</script>

<style scoped>
.card-gap {
  margin-bottom: 16px;
}
</style>
