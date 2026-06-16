<template>
  <div class="auth-wrap">
    <el-card class="auth-card">
      <h2>用户注册</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input v-model="form.confirm" type="password" placeholder="请再次输入密码" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" class="full" @click="submit">注册</el-button>
      </el-form>
      <div class="links">
        <router-link to="/login">已有账号？去登录</router-link>
        <router-link to="/">返回首页</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ name: '', phone: '', password: '', confirm: '' })
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1\d{10}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  password: [{ required: true, min: 6, message: '密码至少 6 位', trigger: 'blur' }],
  confirm: [
    {
      validator: (rule, value, cb) =>
        value === form.password ? cb() : cb(new Error('两次密码不一致')),
      trigger: 'blur',
    },
  ],
}

async function submit() {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await auth.register({ name: form.name, phone: form.phone, password: form.password })
      ElMessage.success('注册成功')
      router.push('/user/center')
    } catch (e) {
      /* handled */
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.auth-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fdecea, #f5f7fa);
}
.auth-card {
  width: 380px;
  padding: 10px 20px 20px;
}
.auth-card h2 {
  text-align: center;
  margin-bottom: 20px;
}
.full {
  width: 100%;
}
.links {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  font-size: 14px;
}
</style>
