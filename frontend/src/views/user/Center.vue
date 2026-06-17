<template>
  <div>
    <h2>个人中心</h2>
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="card-gap">
          <template #header>基本信息</template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="姓名">{{ auth.name }}</el-descriptions-item>
            <el-descriptions-item label="手机号">{{ phone }}</el-descriptions-item>
            <el-descriptions-item label="最近一次预约状态">
              <el-tag v-if="latest" type="warning">{{ latest.status }}</el-tag>
              <span v-else class="text-muted">暂无预约</span>
            </el-descriptions-item>
            <el-descriptions-item label="最近预约日期">
              {{ latest ? latest.appoint_date : '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="card-gap">
          <template #header>快捷入口</template>
          <el-button type="primary" class="quick" @click="$router.push('/user/appointment')">我要预约献血</el-button>
          <el-button class="quick" @click="$router.push('/user/profile')">完善个人信息</el-button>
          <el-button class="quick" @click="$router.push('/user/double-form')">双表填写与签署</el-button>
          <el-button class="quick" @click="$router.push('/user/appointments')">查看我的预约</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '../../store/auth'
import api from '../../api'

const auth = useAuthStore()
const phone = ref('')
const latest = ref(null)

onMounted(async () => {
  const me = await api.get('/auth/me')
  phone.value = me.phone
  const appts = await api.get('/appointments/mine')
  if (appts.length) latest.value = appts[0]
})
</script>

<style scoped>
.quick {
  display: block;
  width: 100%;
  margin: 0 0 12px;
}
</style>
