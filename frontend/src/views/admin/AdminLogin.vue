<template>
  <div class="auth-wrap">
    <el-card class="auth-card">
      <h2>管理端登录</h2>
      <el-form :model="form" ref="formRef" label-position="top">
        <el-form-item label="账号" prop="phone">
          <el-input v-model="form.phone" placeholder="管理员账号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" show-password />
        </el-form-item>
        <el-button type="primary" :loading="loading" class="full" @click="submit">登录</el-button>
      </el-form>
      <div class="links">
        <router-link to="/">返回首页</router-link>
        <span class="text-muted">admin/admin123 · recruiter/123456 · collector/123456</span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../../store/auth'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({ phone: 'admin', password: '' })

async function submit() {
  loading.value = true
  try {
    await auth.login({ ...form })
    if (!auth.isStaff) {
      ElMessage.error('该账号不是后台工作人员')
      auth.logout()
      return
    }
    ElMessage.success('登录成功')
    router.push('/admin/dashboard')
  } catch (e) {
    /* handled */
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #303133, #5c5f66);
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
  font-size: 13px;
}
</style>
