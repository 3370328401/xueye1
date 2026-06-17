<template>
  <div>
    <h2>献血评价管理</h2>
    <el-tabs v-model="tab">
      <el-tab-pane label="评价记录" name="list">
        <el-card>
          <el-table :data="list" v-loading="loading" stripe>
            <el-table-column prop="user_name" label="姓名" width="90" />
            <el-table-column prop="user_phone" label="手机号" width="130" />
            <el-table-column prop="appointment_code" label="预约编号" width="170" />
            <el-table-column prop="env_score" label="环境" width="70" />
            <el-table-column prop="attitude_score" label="态度" width="70" />
            <el-table-column prop="wait_score" label="等待" width="70" />
            <el-table-column prop="skill_score" label="技能" width="70" />
            <el-table-column prop="notice_score" label="讲解" width="70" />
            <el-table-column label="总体" width="90">
              <template #default="{ row }"><el-tag type="success">{{ row.overall_score }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="suggestion" label="改进建议" />
            <el-table-column prop="created_at" label="提交时间" width="180" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="评价模板" name="templates">
        <el-card class="card-gap">
          <el-button type="success" @click="openCreate">新增模板</el-button>
        </el-card>
        <el-card>
          <el-table :data="templates" stripe>
            <el-table-column prop="name" label="模板名称" />
            <el-table-column prop="blood_type" label="献血类型" width="100" />
            <el-table-column label="评价指标">
              <template #default="{ row }">{{ parseIndicators(row.indicators).join('、') }}</template>
            </el-table-column>
            <el-table-column prop="reward_points" label="评价送积分" width="110" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }"><el-button size="small" @click="openEdit(row)">编辑</el-button></template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialog" :title="form.id ? '编辑评价模板' : '新增评价模板'" width="480px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="模板名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="献血类型">
          <el-select v-model="form.blood_type" style="width: 140px">
            <el-option label="全血" value="全血" />
            <el-option label="成分血" value="成分血" />
          </el-select>
        </el-form-item>
        <el-form-item label="评价指标">
          <el-select v-model="form.indicators" multiple filterable allow-create default-first-option style="width: 100%">
            <el-option v-for="i in indicatorOptions" :key="i" :label="i" :value="i" />
          </el-select>
        </el-form-item>
        <el-form-item label="评价送积分"><el-input-number v-model="form.reward_points" :min="0" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
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
import { ElMessage } from 'element-plus'
import api from '../../api'

const tab = ref('list')
const list = ref([])
const templates = ref([])
const loading = ref(false)
const dialog = ref(false)
const indicatorOptions = ['采血环境', '工作人员态度', '等待时间', '业务技能', '注意事项讲解', '小礼品满意度']
const form = reactive({ id: null, name: '', blood_type: '全血', indicators: [], reward_points: 20, is_active: true })

function parseIndicators(s) {
  try {
    return JSON.parse(s || '[]')
  } catch (e) {
    return []
  }
}

async function load() {
  loading.value = true
  try {
    ;[list.value, templates.value] = await Promise.all([
      api.get('/evaluations/admin/list'),
      api.get('/evaluations/templates/admin/list'),
    ])
  } finally {
    loading.value = false
  }
}

function openCreate() {
  Object.assign(form, { id: null, name: '', blood_type: '全血', indicators: [...indicatorOptions], reward_points: 20, is_active: true })
  dialog.value = true
}

function openEdit(row) {
  Object.assign(form, {
    id: row.id,
    name: row.name,
    blood_type: row.blood_type,
    indicators: parseIndicators(row.indicators),
    reward_points: row.reward_points,
    is_active: row.is_active,
  })
  dialog.value = true
}

async function save() {
  const payload = {
    name: form.name,
    blood_type: form.blood_type,
    indicators: form.indicators,
    reward_points: form.reward_points,
    is_active: form.is_active,
  }
  if (form.id) {
    await api.put(`/evaluations/templates/${form.id}`, payload)
  } else {
    await api.post('/evaluations/templates', payload)
  }
  ElMessage.success('已保存')
  dialog.value = false
  load()
}

onMounted(load)
</script>

<style scoped>
.card-gap {
  margin-bottom: 16px;
}
</style>
