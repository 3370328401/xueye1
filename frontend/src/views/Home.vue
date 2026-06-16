<template>
  <div class="home">
    <div class="hero">
      <h1>数字化献血志愿者招募平台</h1>
      <p>
        让爱心献血更简单。在线预约、健康征询、团体申报、过程评价，一站式完成献血志愿服务全流程。
      </p>
    </div>

    <div class="page-container">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="entry in entries" :key="entry.title">
          <el-card class="entry-card card-gap" shadow="hover" @click="go(entry.to)">
            <el-icon :size="40" color="#c62828"><component :is="entry.icon" /></el-icon>
            <h3>{{ entry.title }}</h3>
            <p class="text-muted">{{ entry.desc }}</p>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <footer class="home-footer text-muted">
      MVP 演示系统 · FastAPI + Vue3 + Element Plus + ECharts + SQLite
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const entries = [
  { title: '个人用户登录', desc: '已有账号，登录个人中心', to: '/login', icon: 'User' },
  { title: '个人用户注册', desc: '新用户快速注册', to: '/register', icon: 'EditPen' },
  { title: '献血预约', desc: '登录后在线预约献血', to: '/login', icon: 'Calendar' },
  { title: '团体献血申报', desc: '单位组织集体献血', to: '/group/apply', icon: 'OfficeBuilding' },
  { title: '团体申报查询', desc: '凭手机号查询申报进度', to: '/group/query', icon: 'Search' },
  { title: '管理端入口', desc: '管理员登录后台', to: '/admin/login', icon: 'Setting' },
]

function go(to) {
  router.push(to)
}
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, #c62828, #e53935);
  color: #fff;
  padding: 60px 20px;
  text-align: center;
}
.hero h1 {
  margin: 0 0 16px;
  font-size: 34px;
}
.hero p {
  max-width: 720px;
  margin: 0 auto;
  font-size: 16px;
  line-height: 1.8;
  opacity: 0.95;
}
.entry-card {
  text-align: center;
  cursor: pointer;
  padding: 16px 0;
  transition: transform 0.2s;
}
.entry-card:hover {
  transform: translateY(-4px);
}
.entry-card h3 {
  margin: 12px 0 6px;
}
.home-footer {
  text-align: center;
  padding: 30px;
}
</style>
