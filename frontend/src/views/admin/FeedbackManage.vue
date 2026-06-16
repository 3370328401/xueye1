<template>
  <div>
    <h2>异常反馈管理</h2>
    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="user_name" label="姓名" width="90" />
        <el-table-column prop="user_phone" label="手机号" width="130" />
        <el-table-column prop="appointment_code" label="预约编号" width="170" />
        <el-table-column label="肿包" width="70"><template #default="{ row }">{{ row.swelling ? '是' : '否' }}</template></el-table-column>
        <el-table-column label="发红" width="70"><template #default="{ row }">{{ row.redness ? '是' : '否' }}</template></el-table-column>
        <el-table-column label="手臂疼痛" width="90"><template #default="{ row }">{{ row.arm_pain ? '是' : '否' }}</template></el-table-column>
        <el-table-column prop="other_desc" label="其他描述" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }"><el-tag :type="row.status === '已解决' ? 'success' : 'warning'">{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }"><el-button size="small" type="primary" @click="open(row)">处理</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" title="处理异常反馈" width="460px">
      <el-form v-if="current" label-width="100px">
        <el-form-item label="处理状态">
          <el-select v-model="current.status">
            <el-option v-for="s in statuses" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="处理结果">
          <el-input v-model="current.result" type="textarea" :rows="3" />
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

const statuses = ['已反馈', '正在联系处理', '已解决']
const list = ref([])
const loading = ref(false)
const dialog = ref(false)
const current = ref(null)

async function load() {
  loading.value = true
  try {
    list.value = await api.get('/feedbacks/admin/list')
  } finally {
    loading.value = false
  }
}

function open(row) {
  current.value = { ...row }
  dialog.value = true
}

async function save() {
  await api.put(`/feedbacks/admin/${current.value.id}/status`, {
    status: current.value.status,
    result: current.value.result || '',
  })
  ElMessage.success('已保存')
  dialog.value = false
  load()
}

onMounted(load)
</script>
