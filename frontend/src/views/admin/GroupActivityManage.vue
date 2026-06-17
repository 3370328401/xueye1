<template>
  <div>
    <h2>团体活动与统计</h2>

    <el-card class="card-gap">
      <div class="bar">
        <el-form :inline="true">
          <el-form-item label="年度">
            <el-input v-model="filters.year" placeholder="如 2026" style="width: 120px" />
          </el-form-item>
          <el-form-item label="单位类型">
            <el-select v-model="filters.unit_type" clearable placeholder="全部" style="width: 130px">
              <el-option v-for="t in unitTypes" :key="t" :label="t" :value="t" />
            </el-select>
          </el-form-item>
          <el-form-item label="单位名称">
            <el-input v-model="filters.unit_name" placeholder="模糊查询" style="width: 160px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="load">查询</el-button>
            <el-button @click="reset">重置</el-button>
          </el-form-item>
        </el-form>
        <el-button type="success" @click="openCreate">创建团体活动</el-button>
      </div>

      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="flow_no" label="业务流程号" width="180" />
        <el-table-column prop="unit_name" label="单位名称" />
        <el-table-column prop="unit_type" label="类型" width="80" />
        <el-table-column prop="activity_date" label="预约时间" width="120" />
        <el-table-column prop="actual_date" label="实际献血时间" width="120" />
        <el-table-column prop="location" label="采血地点" />
        <el-table-column prop="expected_count" label="预约人数" width="90" />
        <el-table-column prop="actual_count" label="实际人数" width="90" />
        <el-table-column prop="center_contact" label="中心负责人" width="120" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="openUpdate(row)">登记结果</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-row :gutter="16">
      <el-col :xs="24" :md="12">
        <el-card class="card-gap"><div ref="typeRef" class="chart"></div></el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card class="card-gap"><div ref="yearRef" class="chart"></div></el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="createDialog" title="创建团体活动" width="520px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="关联申报">
          <el-select v-model="form.application_id" clearable placeholder="可选择已受理的团体申报" @change="onPickApp">
            <el-option
              v-for="a in applications"
              :key="a.id"
              :label="`${a.unit_name}（${a.unit_type}）`"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="单位名称" required>
          <el-input v-model="form.unit_name" />
        </el-form-item>
        <el-form-item label="单位类型">
          <el-select v-model="form.unit_type" style="width: 160px">
            <el-option v-for="t in unitTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact_name" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.contact_phone" />
        </el-form-item>
        <el-form-item label="中心负责人">
          <el-input v-model="form.center_contact" />
        </el-form-item>
        <el-form-item label="预约时间">
          <el-date-picker v-model="form.activity_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="采血地点">
          <el-input v-model="form.location" />
        </el-form-item>
        <el-form-item label="预约人数">
          <el-input-number v-model="form.expected_count" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">创建（生成流程号）</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="updateDialog" title="登记活动结果" width="460px">
      <el-form v-if="current" label-width="110px">
        <el-form-item label="单位名称">{{ current.unit_name }}</el-form-item>
        <el-form-item label="实际献血时间">
          <el-date-picker v-model="current.actual_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="实际人数">
          <el-input-number v-model="current.actual_count" :min="0" />
        </el-form-item>
        <el-form-item label="中心负责人">
          <el-input v-model="current.center_contact" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="current.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="updateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitUpdate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import api from '../../api'

const unitTypes = ['学校', '政府', '军队', '企业', '其他']
const list = ref([])
const applications = ref([])
const loading = ref(false)
const filters = reactive({ year: '', unit_type: '', unit_name: '' })
const createDialog = ref(false)
const updateDialog = ref(false)
const current = ref(null)
const form = reactive({
  application_id: null,
  unit_name: '',
  unit_type: '其他',
  contact_name: '',
  contact_phone: '',
  center_contact: '',
  activity_date: '',
  location: '',
  expected_count: 0,
})

const typeRef = ref()
const yearRef = ref()
const charts = []

async function load() {
  loading.value = true
  try {
    const params = {}
    if (filters.year) params.year = filters.year
    if (filters.unit_type) params.unit_type = filters.unit_type
    if (filters.unit_name) params.unit_name = filters.unit_name
    list.value = await api.get('/group-applications/activities/admin/list', { params })
  } finally {
    loading.value = false
  }
  await renderStats()
}

function reset() {
  filters.year = ''
  filters.unit_type = ''
  filters.unit_name = ''
  load()
}

async function openCreate() {
  applications.value = await api.get('/group-applications/admin/list')
  Object.assign(form, {
    application_id: null,
    unit_name: '',
    unit_type: '其他',
    contact_name: '',
    contact_phone: '',
    center_contact: '',
    activity_date: '',
    location: '',
    expected_count: 0,
  })
  createDialog.value = true
}

function onPickApp(id) {
  const a = applications.value.find((x) => x.id === id)
  if (a) {
    form.unit_name = a.unit_name
    form.unit_type = a.unit_type
    form.contact_name = a.contact_name
    form.contact_phone = a.contact_phone
    form.expected_count = a.expected_count
  }
}

async function submitCreate() {
  if (!form.unit_name) return ElMessage.warning('请填写单位名称')
  await api.post('/group-applications/activities', { ...form })
  ElMessage.success('团体活动已创建，系统已生成业务流程号')
  createDialog.value = false
  load()
}

function openUpdate(row) {
  current.value = { ...row }
  updateDialog.value = true
}

async function submitUpdate() {
  await api.put(`/group-applications/activities/admin/${current.value.id}`, {
    actual_date: current.value.actual_date || '',
    actual_count: current.value.actual_count || 0,
    center_contact: current.value.center_contact || '',
    remark: current.value.remark || '',
  })
  ElMessage.success('已保存')
  updateDialog.value = false
  load()
}

function renderBar(el, title, names, values, color) {
  const chart = echarts.init(el)
  chart.setOption({
    title: { text: title, left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: names },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ type: 'bar', data: values, itemStyle: { color }, barWidth: '45%' }],
  })
  charts.push(chart)
}

async function renderStats() {
  charts.forEach((c) => c.dispose())
  charts.length = 0
  const [byType, byYear] = await Promise.all([
    api.get('/group-applications/stats/by-type'),
    api.get('/group-applications/stats/by-year'),
  ])
  renderBar(
    typeRef.value,
    '团体活动按单位类型统计（活动数）',
    byType.map((d) => d.unit_type),
    byType.map((d) => d.activities),
    '#409eff',
  )
  renderBar(
    yearRef.value,
    '团体献血按年度统计（实际人数）',
    byYear.map((d) => String(d.year)),
    byYear.map((d) => d.actual),
    '#c62828',
  )
}

const resize = () => charts.forEach((c) => c.resize())
window.addEventListener('resize', resize)
onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  charts.forEach((c) => c.dispose())
})

onMounted(load)
</script>

<style scoped>
.card-gap {
  margin-bottom: 16px;
}
.bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.chart {
  height: 320px;
}
</style>
