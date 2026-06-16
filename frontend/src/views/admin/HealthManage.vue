<template>
  <div>
    <h2>健康征询表管理</h2>
    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="user_name" label="姓名" width="90" />
        <el-table-column prop="user_phone" label="手机号" width="130" />
        <el-table-column prop="appointment_code" label="预约编号" width="170" />
        <el-table-column label="是否健康" width="90">
          <template #default="{ row }"><el-tag :type="row.is_healthy ? 'success' : 'danger'">{{ row.is_healthy ? '是' : '否' }}</el-tag></template>
        </el-table-column>
        <el-table-column label="饮酒" width="70"><template #default="{ row }">{{ row.drank_alcohol ? '是' : '否' }}</template></el-table-column>
        <el-table-column label="服药" width="70"><template #default="{ row }">{{ row.took_medicine ? '是' : '否' }}</template></el-table-column>
        <el-table-column label="症状" width="70"><template #default="{ row }">{{ row.has_symptoms ? '是' : '否' }}</template></el-table-column>
        <el-table-column label="确认真实" width="90">
          <template #default="{ row }"><el-tag :type="row.confirmed ? 'success' : 'info'">{{ row.confirmed ? '已确认' : '未确认' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" />
        <el-table-column label="操作" width="90">
          <template #default="{ row }"><el-button size="small" @click="view(row)">详情</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" title="健康征询表详情" width="520px">
      <el-descriptions v-if="current" :column="1" border>
        <el-descriptions-item label="姓名">{{ current.user_name }}</el-descriptions-item>
        <el-descriptions-item label="预约编号">{{ current.appointment_code }}</el-descriptions-item>
        <el-descriptions-item label="当前身体是否健康">{{ current.is_healthy ? '是' : '否' }}</el-descriptions-item>
        <el-descriptions-item label="过去24小时饮酒">{{ current.drank_alcohol ? '是' : '否' }}</el-descriptions-item>
        <el-descriptions-item label="过去24小时服药">{{ current.took_medicine ? '是' : '否' }}</el-descriptions-item>
        <el-descriptions-item label="是否有症状">{{ current.has_symptoms ? '是' : '否' }}</el-descriptions-item>
        <el-descriptions-item label="重大疾病史">{{ current.has_major_disease ? '是' : '否' }}</el-descriptions-item>
        <el-descriptions-item label="不适合献血">{{ current.unsuitable ? '是' : '否' }}</el-descriptions-item>
        <el-descriptions-item label="其他说明">{{ current.other_note || '-' }}</el-descriptions-item>
        <el-descriptions-item label="确认真实">{{ current.confirmed ? '已确认' : '未确认' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../../api'

const list = ref([])
const loading = ref(false)
const dialog = ref(false)
const current = ref(null)

async function load() {
  loading.value = true
  try {
    list.value = await api.get('/health-surveys/admin/list')
  } finally {
    loading.value = false
  }
}

function view(row) {
  current.value = row
  dialog.value = true
}

onMounted(load)
</script>
