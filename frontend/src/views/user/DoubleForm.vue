<template>
  <div>
    <h2>双表填写与电子签署</h2>
    <el-alert
      type="info"
      :closable="false"
      title="系统根据你的个人信息、健康征询表与预约信息自动生成《献血者个人信息登记表》和《健康征询表》，确认无误后进行电子签署（模拟无纸化签署服务）。"
      style="margin-bottom: 16px"
    />
    <el-card class="card-gap">
      <el-form :inline="true">
        <el-form-item label="选择预约">
          <el-select v-model="appointmentId" placeholder="选择待签署的预约" style="width: 320px" @change="loadPreview">
            <el-option
              v-for="a in appointments"
              :key="a.id"
              :label="`${a.code}（${a.blood_type} / ${a.appoint_date}）· ${a.status}`"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <div v-if="preview">
      <el-card v-for="f in preview.forms" :key="f.form_name" class="card-gap">
        <template #header>
          <strong>{{ f.form_name }}</strong>
        </template>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item v-for="(val, key) in f.fields" :key="key" :label="key">
            {{ val === null || val === '' ? '-' : val }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card>
        <template v-if="preview.signed">
          <el-tag type="success" size="large">双表已签署确认</el-tag>
          <span class="text-muted" style="margin-left: 12px">当前预约状态：{{ preview.status }}</span>
        </template>
        <template v-else>
          <el-form label-width="160px">
            <el-form-item label="手写签名（模拟）">
              <el-input v-model="signature" placeholder="请输入本人姓名作为电子签名" style="max-width: 280px" />
            </el-form-item>
            <el-form-item label="确认">
              <el-checkbox v-model="confirmed">我已核对双表内容，确认真实无误并同意电子签署</el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="sign">确认签署双表</el-button>
            </el-form-item>
          </el-form>
        </template>
      </el-card>
    </div>

    <h3 style="margin-top: 24px">签署历史</h3>
    <el-card>
      <el-table :data="history" stripe>
        <el-table-column type="index" label="序号" width="70" />
        <el-table-column prop="signed_at" label="签署时间" width="200" />
        <el-table-column prop="form_name" label="表单名称" />
        <el-table-column prop="appointment_code" label="预约信息" width="180" />
        <el-table-column prop="sign_no" label="签署流水号" width="200" />
        <el-table-column label="签署状态" width="110">
          <template #default="{ row }"><el-tag type="success">{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column label="审验" width="90">
          <template #default="{ row }">
            <el-tag :type="row.verified ? 'success' : 'info'">{{ row.verified ? '已审验' : '待审验' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="viewForm(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" :title="currentForm?.form_name" width="560px">
      <el-descriptions v-if="currentFields" :column="1" border size="small">
        <el-descriptions-item v-for="(val, key) in currentFields" :key="key" :label="key">
          {{ val === null || val === '' ? '-' : val }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const appointments = ref([])
const appointmentId = ref(null)
const preview = ref(null)
const history = ref([])
const confirmed = ref(false)
const signature = ref('')
const loading = ref(false)
const dialog = ref(false)
const currentForm = ref(null)
const currentFields = ref(null)

async function loadAppointments() {
  const all = await api.get('/appointments/mine')
  appointments.value = all.filter((a) =>
    ['待填双表及签字确认', '双表已填且确认'].includes(a.status),
  )
}

async function loadHistory() {
  history.value = await api.get('/double-forms/mine')
}

async function loadPreview() {
  preview.value = null
  if (!appointmentId.value) return
  try {
    preview.value = await api.get('/double-forms/preview', {
      params: { appointment_id: appointmentId.value },
    })
  } catch (e) {
    /* handled by interceptor (e.g. 需先填写健康征询表) */
  }
}

async function sign() {
  if (!confirmed.value) return ElMessage.warning('请先勾选确认')
  if (!signature.value) return ElMessage.warning('请输入电子签名')
  loading.value = true
  try {
    await api.post('/double-forms/sign', {
      appointment_id: appointmentId.value,
      confirmed: true,
      signature: signature.value,
    })
    ElMessage.success('双表签署成功，预约状态更新为「双表已填且确认」')
    confirmed.value = false
    signature.value = ''
    await Promise.all([loadAppointments(), loadHistory(), loadPreview()])
  } finally {
    loading.value = false
  }
}

function viewForm(row) {
  currentForm.value = row
  try {
    currentFields.value = JSON.parse(row.content)
  } catch (e) {
    currentFields.value = {}
  }
  dialog.value = true
}

onMounted(async () => {
  await Promise.all([loadAppointments(), loadHistory()])
})
</script>

<style scoped>
.card-gap {
  margin-bottom: 16px;
}
.text-muted {
  color: #909399;
}
</style>
