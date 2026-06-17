<template>
  <div>
    <h2>积分与兑换</h2>
    <el-card class="card-gap">
      <div class="balance">
        当前积分：<span class="num">{{ summary.balance }}</span>
      </div>
    </el-card>

    <el-tabs v-model="tab">
      <el-tab-pane label="可兑换礼品" name="gifts">
        <el-row :gutter="16">
          <el-col :xs="12" :sm="8" :md="6" v-for="g in gifts" :key="g.id">
            <el-card class="gift card-gap" shadow="hover">
              <div class="gift-name">{{ g.name }}</div>
              <div class="gift-desc">{{ g.description }}</div>
              <div class="gift-foot">
                <span class="cost">{{ g.points_cost }} 积分</span>
                <span class="stock">库存 {{ g.stock }}</span>
              </div>
              <el-button
                type="primary"
                size="small"
                :disabled="g.stock <= 0 || summary.balance < g.points_cost"
                @click="exchange(g)"
              >兑换</el-button>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="积分明细" name="records">
        <el-card>
          <el-table :data="summary.records" stripe>
            <el-table-column prop="created_at" label="时间" width="200">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column prop="reason" label="说明" />
            <el-table-column label="变动" width="100">
              <template #default="{ row }">
                <span :style="{ color: row.change >= 0 ? '#67c23a' : '#f56c6c' }">
                  {{ row.change >= 0 ? '+' : '' }}{{ row.change }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="balance_after" label="余额" width="90" />
          </el-table>
          <el-empty v-if="!summary.records.length" description="暂无积分记录" />
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="我的兑换" name="exchanges">
        <el-card>
          <el-table :data="exchanges" stripe>
            <el-table-column prop="gift_name" label="礼品" />
            <el-table-column prop="points_cost" label="消耗积分" width="100" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="tagType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="申请时间" width="200">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button
                  size="small"
                  type="danger"
                  v-if="['待处理', '处理中'].includes(row.status)"
                  @click="cancel(row)"
                >取消</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!exchanges.length" description="暂无兑换记录" />
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api'

const tab = ref('gifts')
const summary = ref({ balance: 0, records: [] })
const gifts = ref([])
const exchanges = ref([])

function formatTime(t) {
  return t ? new Date(t).toLocaleString() : ''
}

function tagType(s) {
  return { 已兑换: 'success', 已取消: 'info', 处理中: 'warning' }[s] || ''
}

async function loadAll() {
  ;[summary.value, gifts.value, exchanges.value] = await Promise.all([
    api.get('/points/mine'),
    api.get('/points/gifts'),
    api.get('/points/exchanges/mine'),
  ])
}

async function exchange(g) {
  await ElMessageBox.confirm(`确认使用 ${g.points_cost} 积分兑换「${g.name}」？`, '兑换确认')
  await api.post('/points/exchanges', { gift_id: g.id })
  ElMessage.success('兑换申请已提交')
  loadAll()
}

async function cancel(row) {
  await ElMessageBox.confirm('确认取消该兑换？积分将退还', '提示')
  await api.post(`/points/exchanges/${row.id}/cancel`)
  ElMessage.success('已取消，积分已退还')
  loadAll()
}

onMounted(loadAll)
</script>

<style scoped>
.card-gap {
  margin-bottom: 16px;
}
.balance {
  font-size: 16px;
}
.balance .num {
  font-size: 28px;
  font-weight: bold;
  color: #c62828;
}
.gift {
  text-align: center;
}
.gift-name {
  font-weight: bold;
  margin-bottom: 6px;
}
.gift-desc {
  color: #909399;
  font-size: 12px;
  min-height: 32px;
}
.gift-foot {
  display: flex;
  justify-content: space-between;
  margin: 8px 0;
  font-size: 13px;
}
.cost {
  color: #c62828;
  font-weight: bold;
}
.stock {
  color: #909399;
}
</style>
