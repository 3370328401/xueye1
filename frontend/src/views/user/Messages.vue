<template>
  <div>
    <h2>消息通知</h2>
    <el-card>
      <el-empty v-if="!list.length" description="暂无消息" />
      <el-timeline v-else>
        <el-timeline-item
          v-for="m in list"
          :key="m.id"
          :timestamp="formatTime(m.published_at)"
          :type="m.is_read ? 'info' : 'primary'"
        >
          <el-card shadow="hover" @click="open(m)" class="msg">
            <div class="msg-head">
              <span class="msg-title">
                <el-badge is-dot :hidden="m.is_read" />
                {{ m.title }}
              </span>
              <el-tag size="small">{{ m.msg_type }}</el-tag>
            </div>
            <div class="msg-content">{{ m.content }}</div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <el-dialog v-model="dialog" :title="current.title" width="520px">
      <el-tag size="small" class="card-gap">{{ current.msg_type }}</el-tag>
      <p class="detail-content">{{ current.content }}</p>
      <div class="detail-time">发布时间：{{ formatTime(current.published_at) }}</div>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../../api'

const list = ref([])
const dialog = ref(false)
const current = ref({})

function formatTime(t) {
  return t ? new Date(t).toLocaleString() : ''
}

async function load() {
  list.value = await api.get('/messages/mine')
}

async function open(m) {
  current.value = m
  dialog.value = true
  if (!m.is_read) {
    await api.post(`/messages/${m.id}/read`)
    m.is_read = true
  }
}

onMounted(load)
</script>

<style scoped>
.msg {
  cursor: pointer;
}
.msg-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.msg-title {
  font-weight: bold;
}
.msg-content {
  color: #606266;
  margin-top: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-gap {
  margin-bottom: 12px;
}
.detail-content {
  line-height: 1.8;
  white-space: pre-wrap;
}
.detail-time {
  color: #909399;
  font-size: 12px;
}
</style>
