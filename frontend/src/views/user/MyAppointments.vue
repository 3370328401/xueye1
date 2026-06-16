<template>
  <div>
    <h2>我的预约</h2>
    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="code" label="预约编号" width="170" />
        <el-table-column prop="blood_type" label="献血类型" width="90" />
        <el-table-column prop="appoint_date" label="预约日期" width="120" />
        <el-table-column prop="time_slot" label="时间段" width="130" />
        <el-table-column prop="location" label="采血地点" />
        <el-table-column label="当前状态" width="150">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button size="small" @click="detail(row)">详情</el-button>
            <el-button size="small" type="primary" @click="$router.push('/user/health-survey')">健康征询表</el-button>
            <el-button
              size="small"
              type="danger"
              :disabled="['已取消', '作废', '已完成现场采血'].includes(row.status)"
              @click="cancel(row)"
            >取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" title="预约详情" width="500px">
      <el-descriptions v-if="current" :column="1" border>
        <el-descriptions-item label="预约编号">{{ current.code }}</el-descriptions-item>
        <el-descriptions-item label="献血类型">{{ current.blood_type }}</el-descriptions-item>
        <el-descriptions-item label="预约日期">{{ current.appoint_date }}</el-descriptions-item>
        <el-descriptions-item label="时间段">{{ current.time_slot }}</el-descriptions-item>
        <el-descriptions-item label="采血地点">{{ current.location }}</el-descriptions-item>
        <el-descriptions-item label="当前状态">{{ current.status }}</el-descriptions-item>
        <el-descriptions-item label="备注">{{ current.remark || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ current.created_at }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api'

const list = ref([])
const loading = ref(false)
const dialog = ref(false)
const current = ref(null)

const statusMap = {
  待填写健康征询表: 'warning',
  已填写健康征询表: 'info',
  待现场采血: 'info',
  正在现场采血: 'primary',
  已完成现场采血: 'success',
  已取消: 'danger',
  作废: 'danger',
}
const statusType = (s) => statusMap[s] || 'info'

async function load() {
  loading.value = true
  try {
    list.value = await api.get('/appointments/mine')
  } finally {
    loading.value = false
  }
}

function detail(row) {
  current.value = row
  dialog.value = true
}

async function cancel(row) {
  await ElMessageBox.confirm('确认取消该预约？', '提示', { type: 'warning' })
  await api.post(`/appointments/${row.id}/cancel`)
  ElMessage.success('已取消')
  load()
}

onMounted(load)
</script>
