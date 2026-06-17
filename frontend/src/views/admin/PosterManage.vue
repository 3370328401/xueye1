<template>
  <div>
    <h2>宣传海报管理</h2>
    <el-tabs v-model="tab">
      <el-tab-pane label="海报生成与推送" name="posters">
        <el-card class="card-gap">
          <el-button type="success" @click="openCreate">生成宣传海报</el-button>
        </el-card>
        <el-card>
          <el-table :data="posters" v-loading="loading" stripe>
            <el-table-column prop="unit_name" label="单位名称" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="activity_date" label="活动时间" width="120" />
            <el-table-column prop="location" label="采血地点" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.status === '已推送' ? 'success' : 'info'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="small" @click="preview(row)">预览</el-button>
                <el-button
                  size="small"
                  type="primary"
                  :disabled="row.status === '已推送'"
                  @click="push(row)"
                >推送</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="海报模板" name="templates">
        <el-card>
          <el-table :data="templates" stripe>
            <el-table-column prop="name" label="模板名称" />
            <el-table-column label="背景色" width="120">
              <template #default="{ row }">
                <span class="swatch" :style="{ background: row.bg_color }"></span>{{ row.bg_color }}
              </template>
            </el-table-column>
            <el-table-column prop="contact" label="联系方式" />
            <el-table-column prop="qrcode_text" label="二维码说明" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="createDialog" title="生成宣传海报" width="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="海报模板">
          <el-select v-model="form.template_id" placeholder="选择模板" @change="onPickTpl">
            <el-option v-for="t in templates" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="团体单位" required>
          <el-select v-model="form.unit_name" filterable placeholder="选择团体单位" @change="onPickUnit">
            <el-option v-for="g in units" :key="g.id" :label="g.unit_name" :value="g.unit_name" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系人手机">
          <el-input v-model="form.contact_phone" />
        </el-form-item>
        <el-form-item label="海报标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="活动时间">
          <el-date-picker v-model="form.activity_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="采血地点">
          <el-input v-model="form.location" />
        </el-form-item>
        <el-form-item label="背景色">
          <el-color-picker v-model="form.bg_color" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">生成</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="previewDialog" title="海报预览" width="380px">
      <div v-if="current" class="poster" :style="{ background: current.bg_color }">
        <div class="poster-title">{{ current.title }}</div>
        <div class="poster-unit">{{ current.unit_name }}</div>
        <div class="poster-line">活动时间：{{ current.activity_date || '待定' }}</div>
        <div class="poster-line">采血地点：{{ current.location || '待定' }}</div>
        <div class="poster-qr">[ 二维码 ] {{ current.qrcode_text }}</div>
        <div class="poster-contact">{{ current.contact }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const tab = ref('posters')
const posters = ref([])
const templates = ref([])
const units = ref([])
const loading = ref(false)
const createDialog = ref(false)
const previewDialog = ref(false)
const current = ref(null)
const form = reactive({
  template_id: null,
  unit_name: '',
  contact_phone: '',
  title: '无偿献血，从我做起',
  activity_date: '',
  location: '',
  bg_color: '#c62828',
})

async function load() {
  loading.value = true
  try {
    posters.value = await api.get('/posters/admin/list')
  } finally {
    loading.value = false
  }
}

async function openCreate() {
  units.value = await api.get('/group-applications/admin/list')
  Object.assign(form, {
    template_id: templates.value[0]?.id || null,
    unit_name: '',
    contact_phone: '',
    title: '无偿献血，从我做起',
    activity_date: '',
    location: '',
    bg_color: templates.value[0]?.bg_color || '#c62828',
  })
  createDialog.value = true
}

function onPickTpl(id) {
  const t = templates.value.find((x) => x.id === id)
  if (t) form.bg_color = t.bg_color
}

function onPickUnit(name) {
  const g = units.value.find((x) => x.unit_name === name)
  if (g) form.contact_phone = g.contact_phone
}

async function submitCreate() {
  if (!form.unit_name) return ElMessage.warning('请选择团体单位')
  await api.post('/posters', { ...form })
  ElMessage.success('海报已生成')
  createDialog.value = false
  load()
}

async function push(row) {
  await api.post(`/posters/${row.id}/push`)
  ElMessage.success('海报已推送给团体单位联系人（模拟微信公众号推送）')
  load()
}

function preview(row) {
  current.value = row
  previewDialog.value = true
}

onMounted(async () => {
  templates.value = await api.get('/posters/templates')
  await load()
})
</script>

<style scoped>
.card-gap {
  margin-bottom: 16px;
}
.swatch {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 3px;
  vertical-align: middle;
  margin-right: 6px;
}
.poster {
  color: #fff;
  border-radius: 8px;
  padding: 28px 18px;
  text-align: center;
  min-height: 320px;
}
.poster-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 18px;
}
.poster-unit {
  font-size: 18px;
  margin-bottom: 24px;
}
.poster-line {
  margin: 8px 0;
}
.poster-qr {
  margin: 28px 0 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
}
.poster-contact {
  margin-top: 12px;
  font-size: 13px;
  opacity: 0.9;
}
</style>
