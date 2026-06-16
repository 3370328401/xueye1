<template>
  <div>
    <h2>献血评价管理</h2>
    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="user_name" label="姓名" width="90" />
        <el-table-column prop="user_phone" label="手机号" width="130" />
        <el-table-column prop="appointment_code" label="预约编号" width="170" />
        <el-table-column prop="env_score" label="环境" width="70" />
        <el-table-column prop="attitude_score" label="态度" width="70" />
        <el-table-column prop="wait_score" label="等待" width="70" />
        <el-table-column prop="skill_score" label="技能" width="70" />
        <el-table-column prop="notice_score" label="讲解" width="70" />
        <el-table-column label="总体" width="90">
          <template #default="{ row }"><el-tag type="success">{{ row.overall_score }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="suggestion" label="改进建议" />
        <el-table-column prop="created_at" label="提交时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../../api'

const list = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    list.value = await api.get('/evaluations/admin/list')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
