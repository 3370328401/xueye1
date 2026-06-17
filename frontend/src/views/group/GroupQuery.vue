<template>
  <div class="page-bg">
    <div class="page-container">
      <el-page-header @back="$router.push('/')" content="团体申报查询" class="card-gap" />
      <el-card class="card-gap">
        <el-input
          v-model="phone"
          placeholder="请输入联系人手机号"
          style="max-width: 320px"
          @keyup.enter="query"
        >
          <template #append>
            <el-button @click="query">查询</el-button>
          </template>
        </el-input>
      </el-card>
      <el-card v-if="searched">
        <el-tabs v-model="tab">
          <el-tab-pane label="申报记录" name="apps">
            <el-table :data="list" stripe>
              <el-table-column prop="unit_name" label="单位名称" />
              <el-table-column prop="unit_type" label="类型" width="80" />
              <el-table-column prop="contact_name" label="联系人" width="100" />
              <el-table-column prop="expected_count" label="预计人数" width="90" />
              <el-table-column prop="expected_date" label="期望日期" width="120" />
              <el-table-column label="当前状态" width="110">
                <template #default="{ row }">
                  <el-tag>{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="admin_remark" label="管理员备注" />
            </el-table>
            <el-empty v-if="!list.length" description="未查询到申报记录" />
          </el-tab-pane>
          <el-tab-pane label="活动预约" name="activities">
            <el-table :data="activities" stripe>
              <el-table-column prop="flow_no" label="业务流程号" width="180" />
              <el-table-column prop="unit_name" label="单位名称" />
              <el-table-column prop="activity_date" label="预约时间" width="120" />
              <el-table-column prop="actual_date" label="实际时间" width="120" />
              <el-table-column prop="location" label="采血地点" />
              <el-table-column prop="expected_count" label="预约人数" width="90" />
              <el-table-column prop="center_contact" label="中心负责人" width="120" />
            </el-table>
            <el-empty v-if="!activities.length" description="暂无活动预约" />
          </el-tab-pane>
          <el-tab-pane label="宣传海报" name="posters">
            <div v-if="posters.length" class="poster-grid">
              <div v-for="p in posters" :key="p.id" class="poster" :style="{ background: p.bg_color }">
                <div class="poster-title">{{ p.title }}</div>
                <div class="poster-unit">{{ p.unit_name }}</div>
                <div class="poster-line">活动时间：{{ p.activity_date || '待定' }}</div>
                <div class="poster-line">采血地点：{{ p.location || '待定' }}</div>
                <div class="poster-qr">[ 二维码 ] {{ p.qrcode_text }}</div>
                <div class="poster-contact">{{ p.contact }}</div>
              </div>
            </div>
            <el-empty v-else description="暂无已推送海报" />
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const phone = ref('')
const tab = ref('apps')
const list = ref([])
const activities = ref([])
const posters = ref([])
const searched = ref(false)

async function query() {
  if (!phone.value) return ElMessage.warning('请输入手机号')
  const params = { phone: phone.value }
  ;[list.value, activities.value, posters.value] = await Promise.all([
    api.get('/group-applications/query', { params }),
    api.get('/group-applications/activities/query', { params }),
    api.get('/posters/query', { params }),
  ])
  searched.value = true
}
</script>

<style scoped>
.page-bg {
  min-height: 100vh;
  padding: 20px 0;
}
.poster-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.poster {
  width: 240px;
  color: #fff;
  border-radius: 8px;
  padding: 24px 16px;
  text-align: center;
}
.poster-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 16px;
}
.poster-unit {
  font-size: 16px;
  margin-bottom: 20px;
}
.poster-line {
  margin: 6px 0;
  font-size: 13px;
}
.poster-qr {
  margin: 20px 0 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  font-size: 13px;
}
.poster-contact {
  margin-top: 10px;
  font-size: 12px;
  opacity: 0.9;
}
</style>
