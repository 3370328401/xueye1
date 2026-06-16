<template>
  <div>
    <h2>身体异常反馈</h2>
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
        <el-form-item label="是否肿包"><el-switch v-model="form.swelling" /></el-form-item>
        <el-form-item label="是否发红"><el-switch v-model="form.redness" /></el-form-item>
        <el-form-item label="是否手臂疼痛"><el-switch v-model="form.arm_pain" /></el-form-item>
        <el-form-item label="其他异常描述">
          <el-input v-model="form.other_desc" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.contact_phone" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submit">提交反馈</el-button>
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
  swelling: false,
  redness: false,
  arm_pain: false,
  other_desc: '',
  contact_phone: '',
})

onMounted(async () => {
  appointments.value = await api.get('/appointments/mine')
})

async function submit() {
  if (!form.appointment_id) return ElMessage.warning('请选择预约')
  loading.value = true
  try {
    await api.post('/feedbacks', { ...form })
    ElMessage.success('反馈已提交')
  } finally {
    loading.value = false
  }
}
</script>
