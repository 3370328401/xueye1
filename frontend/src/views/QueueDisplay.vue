<template>
  <div class="screen">
    <div class="head">
      <div class="title">现场采血叫号显示</div>
      <div class="filters">
        <el-select v-model="location" clearable placeholder="采血点" @change="load" class="sel">
          <el-option v-for="l in locations" :key="l.id" :label="l.name" :value="l.name" />
        </el-select>
        <el-select v-model="bloodType" clearable placeholder="献血类型" @change="load" class="sel">
          <el-option label="全血" value="全血" />
          <el-option label="成分血" value="成分血" />
        </el-select>
        <el-button @click="$router.push('/')" plain>返回首页</el-button>
      </div>
    </div>

    <div class="now">
      <div class="now-label">正在采血</div>
      <div class="now-list">
        <div v-for="q in collecting" :key="q.code" class="now-card">
          <div class="now-name">{{ q.name }}</div>
          <div class="now-meta">{{ q.blood_type }} · {{ q.code.slice(-6) }}</div>
        </div>
        <div v-if="!collecting.length" class="empty">暂无</div>
      </div>
    </div>

    <div class="waiting">
      <div class="now-label">等待队列</div>
      <el-table :data="waiting" class="wtable">
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column prop="name" label="献血者" />
        <el-table-column prop="blood_type" label="献血类型" />
        <el-table-column label="前方等待人数">
          <template #default="{ row }">{{ row.ahead }}</template>
        </el-table-column>
      </el-table>
      <div v-if="!waiting.length" class="empty">当前无人排队</div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import api from '../api'

const location = ref('')
const bloodType = ref('')
const items = ref([])
const locations = ref([])
let timer = null

const collecting = computed(() => items.value.filter((q) => q.status === '正在现场采血'))
const waiting = computed(() => items.value.filter((q) => q.status === '待现场采血'))

async function load() {
  const params = {}
  if (location.value) params.location = location.value
  if (bloodType.value) params.blood_type = bloodType.value
  items.value = await api.get('/queue', { params })
}

onMounted(async () => {
  try {
    locations.value = await api.get('/locations')
  } catch (e) {
    locations.value = []
  }
  load()
  timer = setInterval(load, 10000)
})
onBeforeUnmount(() => timer && clearInterval(timer))
</script>

<style scoped>
.screen {
  min-height: 100vh;
  background: #0d1b2a;
  color: #fff;
  padding: 24px 32px;
}
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.title {
  font-size: 30px;
  font-weight: bold;
  letter-spacing: 2px;
}
.filters {
  display: flex;
  gap: 12px;
}
.sel {
  width: 150px;
}
.now-label {
  font-size: 18px;
  color: #90caf9;
  margin-bottom: 12px;
}
.now-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 32px;
}
.now-card {
  background: #c62828;
  border-radius: 10px;
  padding: 20px 36px;
  text-align: center;
}
.now-name {
  font-size: 32px;
  font-weight: bold;
}
.now-meta {
  margin-top: 6px;
  opacity: 0.85;
}
.wtable {
  background: transparent;
}
.empty {
  color: #607d8b;
  padding: 12px 0;
}
</style>
