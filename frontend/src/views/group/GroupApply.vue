<template>
  <div class="page-bg">
    <div class="page-container">
      <el-page-header @back="$router.push('/')" content="团体献血申报" class="card-gap" />
      <el-card>
        <el-form :model="form" :rules="rules" ref="formRef" label-width="160px" style="max-width: 680px">
          <el-form-item label="单位名称" prop="unit_name"><el-input v-model="form.unit_name" /></el-form-item>
          <el-form-item label="统一社会信用代码"><el-input v-model="form.credit_code" /></el-form-item>
          <el-form-item label="单位地址"><el-input v-model="form.unit_address" /></el-form-item>
          <el-form-item label="联系人姓名" prop="contact_name"><el-input v-model="form.contact_name" /></el-form-item>
          <el-form-item label="联系人手机号" prop="contact_phone"><el-input v-model="form.contact_phone" /></el-form-item>
          <el-form-item label="预计献血人数">
            <el-input-number v-model="form.expected_count" :min="0" />
          </el-form-item>
          <el-form-item label="期望献血日期">
            <el-date-picker v-model="form.expected_date" type="date" value-format="YYYY-MM-DD" />
          </el-form-item>
          <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="3" /></el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="submit">提交申报</el-button>
            <el-button @click="$router.push('/group/query')">查询申报状态</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const formRef = ref()
const loading = ref(false)
const form = reactive({
  unit_name: '',
  credit_code: '',
  unit_address: '',
  contact_name: '',
  contact_phone: '',
  expected_count: 0,
  expected_date: '',
  remark: '',
})
const rules = {
  unit_name: [{ required: true, message: '请输入单位名称', trigger: 'blur' }],
  contact_name: [{ required: true, message: '请输入联系人姓名', trigger: 'blur' }],
  contact_phone: [{ required: true, message: '请输入联系人手机号', trigger: 'blur' }],
}

async function submit() {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await api.post('/group-applications', { ...form })
      ElMessage.success('申报已提交，状态为"待受理"')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.page-bg {
  min-height: 100vh;
  padding: 20px 0;
}
</style>
