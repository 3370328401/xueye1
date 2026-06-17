<template>
  <div>
    <h2>团体申报管理</h2>
    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="unit_name" label="单位名称" />
        <el-table-column prop="unit_type" label="单位类型" width="90" />
        <el-table-column prop="contact_name" label="联系人" width="90" />
        <el-table-column prop="contact_phone" label="手机号" width="130" />
        <el-table-column prop="expected_count" label="预计人数" width="90" />
        <el-table-column prop="expected_date" label="期望日期" width="120" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }"><el-tag>{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="admin_remark" label="管理员备注" />
        <el-table-column label="操作" width="110">
          <template #default="{ row }"><el-button size="small" type="primary" @click="open(row)">处理</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" title="处理团体申报" width="460px">
      <el-form v-if="current" label-width="100px">
        <el-form-item label="单位名称">{{ current.unit_name }}</el-form-item>
        <el-form-item label="申报状态">
          <el-select v-model="current.status">
            <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理备注">
          <el-input v-model="current.admin_remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const statuses = ['待受理', '受理中', '受理已完成', '已驳回']
const list = ref([])
const loading = ref(false)
const dialog = ref(false)
const current = ref(null)

async function load() {
  loading.value = true
  try {
    list.value = await api.get('/group-applications/admin/list')
  } finally {
    loading.value = false
  }
}

function open(row) {
  current.value = { ...row }
  dialog.value = true
}

async function save() {
  await api.put(`/group-applications/admin/${current.value.id}/status`, {
    status: current.value.status,
    admin_remark: current.value.admin_remark || '',
  })
  ElMessage.success('已保存')
  dialog.value = false
  load()
}

onMounted(load)
</script>
