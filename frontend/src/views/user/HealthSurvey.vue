<template>
  <div>
    <h2>健康征询表</h2>
    <el-card>
      <el-form :model="form" label-width="220px" style="max-width: 720px">
        <el-form-item label="选择预约" required>
          <el-select v-model="form.appointment_id" placeholder="选择需要填写的预约">
            <el-option
              v-for="a in appointments"
              :key="a.id"
              :label="`${a.code}（${a.blood_type} / ${a.appoint_date}）`"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="当前身体是否健康">
          <el-switch v-model="form.is_healthy" active-text="健康" inactive-text="不健康" />
        </el-form-item>
        <el-form-item label="过去 24 小时内是否饮酒">
          <el-switch v-model="form.drank_alcohol" />
        </el-form-item>
        <el-form-item label="过去 24 小时内是否服药">
          <el-switch v-model="form.took_medicine" />
        </el-form-item>
        <el-form-item label="是否有发热、咳嗽、腹泻等症状">
          <el-switch v-model="form.has_symptoms" />
        </el-form-item>
        <el-form-item label="是否有重大疾病史">
          <el-switch v-model="form.has_major_disease" />
        </el-form-item>
        <el-form-item label="是否处于不适合献血状态">
          <el-switch v-model="form.unsuitable" />
        </el-form-item>
        <el-form-item label="其他情况说明">
          <el-input v-model="form.other_note" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="本人确认信息真实有效">
          <el-checkbox v-model="form.confirmed">我确认以上信息真实有效（替代电子签名）</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submit">提交健康征询表</el-button>
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
  is_healthy: true,
  drank_alcohol: false,
  took_medicine: false,
  has_symptoms: false,
  has_major_disease: false,
  unsuitable: false,
  other_note: '',
  confirmed: false,
})

onMounted(async () => {
  const all = await api.get('/appointments/mine')
  appointments.value = all.filter((a) => !['已取消', '作废'].includes(a.status))
})

async function submit() {
  if (!form.appointment_id) return ElMessage.warning('请选择预约')
  if (!form.confirmed) return ElMessage.warning('请勾选确认信息真实有效')
  loading.value = true
  try {
    await api.post('/health-surveys', { ...form })
    ElMessage.success('提交成功，预约状态已更新为"已填写健康征询表"')
  } finally {
    loading.value = false
  }
}
</script>
