<template>
  <div>
    <h2>献血过程评价</h2>
    <el-card>
      <el-form :model="form" label-width="160px" style="max-width: 680px">
        <el-form-item label="对应预约" required>
          <el-select v-model="form.appointment_id" placeholder="选择对应的预约">
            <el-option
              v-for="a in appointments"
              :key="a.id"
              :label="`${a.code}（${a.blood_type} / ${a.appoint_date}）`"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="采血环境评分"><el-rate v-model="form.env_score" /></el-form-item>
        <el-form-item label="工作人员态度评分"><el-rate v-model="form.attitude_score" /></el-form-item>
        <el-form-item label="等待时间评分"><el-rate v-model="form.wait_score" /></el-form-item>
        <el-form-item label="业务技能评分"><el-rate v-model="form.skill_score" /></el-form-item>
        <el-form-item label="注意事项讲解评分"><el-rate v-model="form.notice_score" /></el-form-item>
        <el-form-item label="总体评分"><el-rate v-model="form.overall_score" /></el-form-item>
        <el-form-item label="改进建议">
          <el-input v-model="form.suggestion" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submit">提交评价</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const loading = ref(false)
const appointments = ref([])
const form = reactive({
  appointment_id: null,
  env_score: 5,
  attitude_score: 5,
  wait_score: 5,
  skill_score: 5,
  notice_score: 5,
  overall_score: 5,
  suggestion: '',
})

onMounted(async () => {
  appointments.value = await api.get('/appointments/mine')
})

async function submit() {
  if (!form.appointment_id) return ElMessage.warning('请选择预约')
  loading.value = true
  try {
    await api.post('/evaluations', { ...form })
    ElMessage.success('评价已提交')
  } finally {
    loading.value = false
  }
}
</script>
