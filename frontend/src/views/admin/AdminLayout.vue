<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">献血平台管理端</div>
      <el-menu :default-active="active" router background-color="#1f2d3d" text-color="#c0c4cc" active-text-color="#fff">
        <el-menu-item index="/admin/dashboard"><el-icon><DataBoard /></el-icon>统计首页</el-menu-item>
        <el-menu-item index="/admin/appointments"><el-icon><Calendar /></el-icon>预约管理</el-menu-item>
        <el-menu-item index="/admin/health"><el-icon><Document /></el-icon>健康征询表</el-menu-item>
        <el-menu-item index="/admin/groups"><el-icon><OfficeBuilding /></el-icon>团体申报管理</el-menu-item>
        <el-menu-item index="/admin/group-activities"><el-icon><Tickets /></el-icon>团体活动与统计</el-menu-item>
        <el-menu-item index="/admin/posters"><el-icon><Picture /></el-icon>宣传海报管理</el-menu-item>
        <el-menu-item index="/admin/feedbacks"><el-icon><Warning /></el-icon>异常反馈管理</el-menu-item>
        <el-menu-item index="/admin/evaluations"><el-icon><Star /></el-icon>献血评价管理</el-menu-item>
        <el-menu-item index="/admin/external"><el-icon><Connection /></el-icon>外部接口演示</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>数字化献血志愿者招募平台 · 管理后台</span>
        <div class="header-right">
          <span>{{ auth.name }}</span>
          <el-button text @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main><router-view /></el-main>
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
  router.push('/admin/login')
}
</script>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background: #1f2d3d;
}
.logo {
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  text-align: center;
  line-height: 60px;
  border-bottom: 1px solid #2a3a4d;
}
.header {
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.el-main {
  background: #f5f7fa;
}
</style>
