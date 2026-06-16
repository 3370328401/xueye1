<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="brand" @click="$router.push('/')">献血志愿者平台 · 个人中心</div>
      <div class="header-right">
        <span>你好，{{ auth.name }}</span>
        <el-button text type="primary" @click="logout">退出登录</el-button>
      </div>
    </el-header>
    <el-container>
      <el-aside width="210px">
        <el-menu :default-active="active" router>
          <el-menu-item index="/user/center"><el-icon><HomeFilled /></el-icon>个人中心</el-menu-item>
          <el-menu-item index="/user/profile"><el-icon><User /></el-icon>我的个人信息</el-menu-item>
          <el-menu-item index="/user/appointment"><el-icon><Calendar /></el-icon>我要预约献血</el-menu-item>
          <el-menu-item index="/user/appointments"><el-icon><List /></el-icon>我的预约</el-menu-item>
          <el-menu-item index="/user/health-survey"><el-icon><Document /></el-icon>健康征询表</el-menu-item>
          <el-menu-item index="/user/feedback"><el-icon><Warning /></el-icon>身体异常反馈</el-menu-item>
          <el-menu-item index="/user/evaluation"><el-icon><Star /></el-icon>献血过程评价</el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import api from '../../api'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const active = computed(() => route.path)

async function logout() {
  try {
    await api.post('/auth/logout')
  } catch (e) {
    /* ignore */
  }
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
}
.header {
  background: #c62828;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand {
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.el-aside {
  background: #fff;
  border-right: 1px solid #ebeef5;
}
.el-main {
  background: #f5f7fa;
}
</style>
