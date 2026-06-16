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
        <el-table :data="list" stripe>
          <el-table-column prop="unit_name" label="单位名称" />
          <el-table-column prop="contact_name" label="联系人" width="100" />
          <el-table-column prop="contact_phone" label="手机号" width="130" />
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
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const phone = ref('')
const list = ref([])
const searched = ref(false)

async function query() {
  if (!phone.value) return ElMessage.warning('请输入手机号')
  list.value = await api.get('/group-applications/query', { params: { phone: phone.value } })
  searched.value = true
}
</script>

<style scoped>
.page-bg {
  min-height: 100vh;
  padding: 20px 0;
}
</style>
