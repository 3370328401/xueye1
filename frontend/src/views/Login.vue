<template>
  <div class="auth-wrap">
    <el-card class="auth-card">
      <h2>用户登录</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" class="full" @click="submit">登录</el-button>
      </el-form>
      <div class="links">
        <router-link to="/register">没有账号？去注册</router-link>
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
const form = reactive({ phone: '', password: '' })
const rules = {
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function submit() {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await auth.login({ ...form })
      ElMessage.success('登录成功')
      router.push(auth.isAdmin ? '/admin/dashboard' : '/user/center')
    } catch (e) {
      /* handled by interceptor */
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
