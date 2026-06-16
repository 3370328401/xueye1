<template>
  <div>
    <h2>我要预约献血</h2>
    <el-card>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" style="max-width: 640px">
        <el-form-item label="献血类型" prop="blood_type">
          <el-radio-group v-model="form.blood_type">
            <el-radio value="全血">全血</el-radio>
            <el-radio value="成分血">成分血</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="预约日期" prop="appoint_date">
          <el-date-picker v-model="form.appoint_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="预约时间段" prop="time_slot">
          <el-select v-model="form.time_slot" placeholder="选择时间段">
            <el-option v-for="s in slots" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="采血地点" prop="location">
          <el-select v-model="form.location" placeholder="选择采血地点">
            <el-option v-for="l in locations" :key="l.id" :label="l.name" :value="l.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submit">提交预约</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../../api'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const locations = ref([])
const slots = ['09:00-10:00', '10:00-11:00', '11:00-12:00', '14:00-15:00', '15:00-16:00', '16:00-17:00']
const form = reactive({ blood_type: '全血', appoint_date: '', time_slot: '', location: '', remark: '' })
const rules = {
  blood_type: [{ required: true, message: '请选择献血类型', trigger: 'change' }],
  appoint_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  time_slot: [{ required: true, message: '请选择时间段', trigger: 'change' }],
  location: [{ required: true, message: '请选择采血地点', trigger: 'change' }],
}

onMounted(async () => {
  locations.value = await api.get('/locations')
})

async function submit() {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await api.post('/appointments', { ...form })
      ElMessage.success('预约提交成功')
      router.push('/user/appointments')
    } finally {
      loading.value = false
    }
  })
}
</script>
