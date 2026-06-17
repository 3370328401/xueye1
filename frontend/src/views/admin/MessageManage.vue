<template>
  <div>
    <h2>消息推送管理</h2>
    <el-card class="card-gap">
      <el-button type="success" @click="openCreate">新增消息</el-button>
    </el-card>
    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="msg_type" label="类型" width="110" />
        <el-table-column prop="scope" label="范围" width="80" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="read_count" label="已读数" width="80" />
        <el-table-column prop="published_at" label="发布时间" width="180">
          <template #default="{ row }">{{ formatTime(row.published_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="300">
          <template #default="{ row }">
            <el-button size="small" v-if="row.status !== '已发布'" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="primary" v-if="row.status !== '已发布'" @click="publish(row)">发布</el-button>
            <el-button size="small" type="warning" v-if="row.status === '已发布'" @click="revoke(row)">撤回</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" :title="form.id ? '编辑消息' : '新增消息'" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.msg_type" style="width: 160px">
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="推送范围">
          <el-radio-group v-model="form.scope">
            <el-radio label="普发">普发（所有献血者）</el-radio>
            <el-radio label="定向">定向</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="定向手机号" v-if="form.scope === '定向'">
          <el-input v-model="phonesText" placeholder="多个手机号用逗号分隔，留空表示按角色全部个人献血者" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="5" />
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
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api'

const list = ref([])
const loading = ref(false)
const dialog = ref(false)
const types = ref([])
const phonesText = ref('')
const form = reactive({ id: null, title: '', content: '', msg_type: '系统通知', scope: '普发' })

function formatTime(t) {
  return t ? new Date(t).toLocaleString() : ''
}
function statusType(s) {
  return { 已发布: 'success', 已撤回: 'info' }[s] || 'warning'
}

async function load() {
  loading.value = true
  try {
    list.value = await api.get('/messages/admin/list')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, { id: null, title: '', content: '', msg_type: '系统通知', scope: '普发' })
  phonesText.value = ''
  dialog.value = true
}

function openEdit(row) {
  Object.assign(form, { id: row.id, title: row.title, content: row.content, msg_type: row.msg_type, scope: row.scope })
  let t = {}
  try {
    t = JSON.parse(row.target || '{}')
  } catch (e) {
    t = {}
  }
  phonesText.value = (t.phones || []).join(',')
  dialog.value = true
}

function buildTarget() {
  if (form.scope !== '定向') return {}
  const target = { roles: ['user'] }
  const phones = phonesText.value.split(',').map((p) => p.trim()).filter(Boolean)
  if (phones.length) target.phones = phones
  return target
}

async function save() {
  const payload = {
    title: form.title,
    content: form.content,
    msg_type: form.msg_type,
    scope: form.scope,
    target: buildTarget(),
  }
  if (form.id) {
    await api.put(`/messages/${form.id}`, payload)
  } else {
    await api.post('/messages', payload)
  }
  ElMessage.success('已保存')
  dialog.value = false
  load()
}

async function publish(row) {
  await api.post(`/messages/${row.id}/publish`)
  ElMessage.success('已发布并推送（模拟）')
  load()
}
async function revoke(row) {
  await api.post(`/messages/${row.id}/revoke`)
  ElMessage.success('已撤回')
  load()
}
async function remove(row) {
  await ElMessageBox.confirm('确认删除该消息？', '提示')
  await api.delete(`/messages/${row.id}`)
  ElMessage.success('已删除')
  load()
}

onMounted(async () => {
  try {
    const meta = await api.get('/messages/meta')
    types.value = meta.types
  } catch (e) {
    types.value = ['系统通知']
  }
  load()
})
</script>

<style scoped>
.card-gap {
  margin-bottom: 16px;
}
</style>
