<template>
  <div>
    <h2>我的个人信息</h2>
    <el-card>
      <el-form :model="form" label-width="120px" style="max-width: 640px">
        <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="身份证号"><el-input v-model="form.id_card" /></el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄"><el-input-number v-model="form.age" :min="0" :max="120" /></el-form-item>
        <el-form-item label="职业"><el-input v-model="form.occupation" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="联系地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="紧急联系人"><el-input v-model="form.emergency_contact" /></el-form-item>
        <el-form-item label="紧急联系人电话"><el-input v-model="form.emergency_phone" /></el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="save">保存</el-button>
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
const form = reactive({
  name: '',
  id_card: '',
  gender: '',
  age: null,
  occupation: '',
  phone: '',
  address: '',
  emergency_contact: '',
  emergency_phone: '',
})

onMounted(async () => {
  const info = await api.get('/donor/info')
  if (info) Object.assign(form, info)
})

async function save() {
  loading.value = true
  try {
    await api.post('/donor/info', { ...form })
    ElMessage.success('保存成功')
  } finally {
    loading.value = false
  }
}
</script>
