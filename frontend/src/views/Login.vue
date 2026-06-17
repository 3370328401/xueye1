<template>
  <div class="auth-wrap">
    <el-card class="auth-card">
      <h2>用户登录</h2>
      <el-tabs v-model="tab">
        <el-tab-pane label="密码登录" name="password">
          <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入手机号" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
            </el-form-item>
            <el-button type="primary" :loading="loading" class="full" @click="submit">登录</el-button>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="验证码登录" name="code">
          <el-form :model="codeForm" label-position="top">
            <el-form-item label="手机号">
              <el-input v-model="codeForm.phone" placeholder="请输入手机号" />
            </el-form-item>
            <el-form-item label="验证码">
              <div class="code-row">
                <el-input v-model="codeForm.code" placeholder="模拟验证码 123456" />
                <el-button :disabled="counting > 0" @click="sendCode">
                  {{ counting > 0 ? `${counting}s` : '获取验证码' }}
                </el-button>
              </div>
            </el-form-item>
            <el-button type="primary" :loading="loading" class="full" @click="submitCode">登录 / 注册</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <el-divider>其他方式</el-divider>
      <el-button class="full wechat" :loading="loading" @click="submitWechat">微信授权登录（模拟）</el-button>
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
import api from '../api'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)
const tab = ref('password')
const counting = ref(0)
const form = reactive({ phone: '', password: '' })
const codeForm = reactive({ phone: '', code: '' })
const rules = {
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

function gotoHome() {
  router.push(auth.isStaff ? '/admin/dashboard' : '/user/center')
}

async function submit() {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await auth.login({ ...form })
      ElMessage.success('登录成功')
      gotoHome()
    } catch (e) {
      /* handled by interceptor */
    } finally {
      loading.value = false
    }
  })
}

async function sendCode() {
  if (!codeForm.phone) {
    ElMessage.warning('请先输入手机号')
    return
  }
  const res = await api.get('/auth/send-code', { params: { phone: codeForm.phone } })
  codeForm.code = res.code
  ElMessage.success('验证码已发送（模拟）')
  counting.value = 60
  const timer = setInterval(() => {
    counting.value -= 1
    if (counting.value <= 0) clearInterval(timer)
  }, 1000)
}

async function submitCode() {
  if (!codeForm.phone || !codeForm.code) {
    ElMessage.warning('请输入手机号和验证码')
    return
  }
  loading.value = true
  try {
    const data = await api.post('/auth/login-code', { ...codeForm })
    auth.setAuth(data)
    ElMessage.success('登录成功')
    gotoHome()
  } catch (e) {
    /* handled */
  } finally {
    loading.value = false
  }
}

async function submitWechat() {
  loading.value = true
  try {
    const data = await api.post('/auth/login-wechat', {})
    auth.setAuth(data)
    ElMessage.success('微信登录成功（模拟）')
    gotoHome()
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
  background: linear-gradient(135deg, #fdecea, #f5f7fa);
}
.auth-card {
  width: 380px;
  padding: 10px 20px 20px;
}
.auth-card h2 {
  text-align: center;
  margin-bottom: 12px;
}
.full {
  width: 100%;
}
.wechat {
  color: #07c160;
  border-color: #07c160;
}
.code-row {
  display: flex;
  gap: 8px;
  width: 100%;
}
.links {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  font-size: 14px;
}
</style>
