<template>
  <div>
    <h2>预约管理</h2>
    <el-card class="card-gap">
      <el-form :inline="true" :model="filters">
        <el-form-item label="用户姓名"><el-input v-model="filters.name" clearable /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="filters.phone" clearable /></el-form-item>
        <el-form-item label="预约日期">
          <el-date-picker v-model="filters.appoint_date" type="date" value-format="YYYY-MM-DD" clearable />
        </el-form-item>
        <el-form-item label="献血类型">
          <el-select v-model="filters.blood_type" clearable style="width: 120px">
            <el-option label="全血" value="全血" />
            <el-option label="成分血" value="成分血" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" clearable style="width: 160px">
            <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="load">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="code" label="预约编号" width="170" />
        <el-table-column prop="user_name" label="姓名" width="90" />
        <el-table-column prop="user_phone" label="手机号" width="130" />
        <el-table-column prop="blood_type" label="类型" width="80" />
        <el-table-column prop="appoint_date" label="日期" width="110" />
        <el-table-column prop="time_slot" label="时间段" width="120" />
        <el-table-column prop="location" label="地点" />
        <el-table-column label="状态" width="150">
          <template #default="{ row }"><el-tag>{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-select
              :model-value="row.status"
              size="small"
              @change="(val) => updateStatus(row, val)"
            >
              <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
            </el-select>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const statuses = [
  '待填写健康征询表',
  '已填写健康征询表',
  '待现场采血',
  '正在现场采血',
  '已完成现场采血',
  '已取消',
  '作废',
]
const filters = reactive({ name: '', phone: '', appoint_date: '', blood_type: '', status: '' })
const list = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const params = {}
    Object.entries(filters).forEach(([k, v]) => {
      if (v) params[k] = v
    })
    list.value = await api.get('/appointments/admin/list', { params })
  } finally {
    loading.value = false
  }
}

function reset() {
  Object.keys(filters).forEach((k) => (filters[k] = ''))
  load()
}

async function updateStatus(row, val) {
  await api.put(`/appointments/admin/${row.id}/status`, { status: val })
  ElMessage.success('状态已更新')
  load()
}

onMounted(load)
</script>
