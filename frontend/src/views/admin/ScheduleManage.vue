<template>
  <div>
    <h2>排班计划管理</h2>
    <el-tabs v-model="tab">
      <el-tab-pane label="团体献血计划" name="plans">
        <el-card class="card-gap">
          <el-form :inline="true">
            <el-form-item label="计划类型">
              <el-select v-model="planType" style="width: 100px">
                <el-option label="周计划" value="周" />
                <el-option label="月计划" value="月" />
              </el-select>
            </el-form-item>
            <el-form-item label="起始日期">
              <el-date-picker v-model="planRange.start" type="date" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="结束日期">
              <el-date-picker v-model="planRange.end" type="date" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="generatePlans">自动生成计划</el-button>
              <el-button @click="loadPlans">刷新</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        <el-card>
          <el-table :data="plans" stripe>
            <el-table-column prop="plan_type" label="类型" width="70" />
            <el-table-column prop="plan_date" label="日期" width="120" />
            <el-table-column prop="weekday" label="星期" width="70" />
            <el-table-column prop="unit_name" label="单位名称" />
            <el-table-column prop="location" label="采血地点" />
            <el-table-column prop="expected_count" label="预约人数" width="90" />
            <el-table-column prop="arrive_time" label="到达时间" width="90" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.status === '已发布' ? 'success' : 'info'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="170">
              <template #default="{ row }">
                <el-button size="small" @click="editPlan(row)">修改</el-button>
                <el-button
                  size="small"
                  type="primary"
                  :disabled="row.status === '已发布'"
                  @click="publishPlan(row)"
                >发布</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="体采人员排班" name="shifts">
        <el-card class="card-gap">
          <el-form :inline="true">
            <el-form-item label="起始日期">
              <el-date-picker v-model="shiftRange.start" type="date" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="结束日期">
              <el-date-picker v-model="shiftRange.end" type="date" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="generateShifts">自动生成排班</el-button>
            </el-form-item>
            <el-form-item label="人员">
              <el-input v-model="shiftFilter.staff_name" placeholder="姓名" style="width: 110px" />
            </el-form-item>
            <el-form-item label="点位/车辆">
              <el-input v-model="shiftFilter.location" placeholder="点位" style="width: 110px" />
            </el-form-item>
            <el-form-item>
              <el-button @click="loadShifts">查询</el-button>
            </el-form-item>
          </el-form>
        </el-card>
        <el-card>
          <el-table :data="shifts" stripe>
            <el-table-column prop="shift" label="班次" width="70" />
            <el-table-column prop="shift_date" label="日期" width="120" />
            <el-table-column prop="weekday" label="星期" width="70" />
            <el-table-column prop="location" label="点位名称" />
            <el-table-column prop="expected_count" label="预约人数" width="90" />
            <el-table-column prop="staff_names" label="人员" />
            <el-table-column label="工作时间" width="130">
              <template #default="{ row }">{{ row.start_time }}~{{ row.end_time }}</template>
            </el-table-column>
            <el-table-column prop="vehicle" label="车辆" width="140" />
            <el-table-column prop="driver" label="司机" width="80" />
            <el-table-column prop="notice" label="注意事项" />
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === '已发布' ? 'success' : 'info'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="170" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="editShift(row)">审核修改</el-button>
                <el-button
                  size="small"
                  type="primary"
                  :disabled="row.status === '已发布'"
                  @click="publishShift(row)"
                >发布</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="planDialog" title="修改献血计划" width="440px">
      <el-form v-if="curPlan" label-width="100px">
        <el-form-item label="单位名称">{{ curPlan.unit_name }}</el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="curPlan.plan_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="采血地点"><el-input v-model="curPlan.location" /></el-form-item>
        <el-form-item label="预约人数"><el-input-number v-model="curPlan.expected_count" :min="0" /></el-form-item>
        <el-form-item label="到达时间"><el-input v-model="curPlan.arrive_time" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="curPlan.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialog = false">取消</el-button>
        <el-button type="primary" @click="savePlan">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="shiftDialog" title="审核修改排班" width="440px">
      <el-form v-if="curShift" label-width="100px">
        <el-form-item label="班次">
          <el-select v-model="curShift.shift" style="width: 140px">
            <el-option label="全天" value="全天" />
            <el-option label="上午" value="上午" />
            <el-option label="下午" value="下午" />
          </el-select>
        </el-form-item>
        <el-form-item label="人员"><el-input v-model="curShift.staff_names" /></el-form-item>
        <el-form-item label="上班时间"><el-input v-model="curShift.start_time" /></el-form-item>
        <el-form-item label="下班时间"><el-input v-model="curShift.end_time" /></el-form-item>
        <el-form-item label="车辆"><el-input v-model="curShift.vehicle" /></el-form-item>
        <el-form-item label="司机"><el-input v-model="curShift.driver" /></el-form-item>
        <el-form-item label="注意事项"><el-input v-model="curShift.notice" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shiftDialog = false">取消</el-button>
        <el-button type="primary" @click="saveShift">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'

const tab = ref('plans')
const planType = ref('周')
const planRange = reactive({ start: '', end: '' })
const shiftRange = reactive({ start: '', end: '' })
const shiftFilter = reactive({ staff_name: '', location: '' })
const plans = ref([])
const shifts = ref([])
const planDialog = ref(false)
const shiftDialog = ref(false)
const curPlan = ref(null)
const curShift = ref(null)

async function loadPlans() {
  plans.value = await api.get('/schedules/blood-plans/admin/list', {
    params: { plan_type: planType.value },
  })
}

async function generatePlans() {
  if (!planRange.start || !planRange.end) return ElMessage.warning('请选择起止日期')
  const created = await api.post('/schedules/blood-plans/generate', {
    plan_type: planType.value,
    start_date: planRange.start,
    end_date: planRange.end,
  })
  ElMessage.success(`已生成 ${created.length} 条计划`)
  loadPlans()
}

function editPlan(row) {
  curPlan.value = { ...row }
  planDialog.value = true
}

async function savePlan() {
  await api.put(`/schedules/blood-plans/${curPlan.value.id}`, {
    plan_date: curPlan.value.plan_date,
    location: curPlan.value.location,
    expected_count: curPlan.value.expected_count,
    arrive_time: curPlan.value.arrive_time,
    remark: curPlan.value.remark || '',
  })
  ElMessage.success('已保存')
  planDialog.value = false
  loadPlans()
}

async function publishPlan(row) {
  await api.post(`/schedules/blood-plans/${row.id}/publish`)
  ElMessage.success('计划已发布，团体单位可查看')
  loadPlans()
}

async function loadShifts() {
  const params = {}
  if (shiftFilter.staff_name) params.staff_name = shiftFilter.staff_name
  if (shiftFilter.location) params.location = shiftFilter.location
  shifts.value = await api.get('/schedules/staff-shifts/admin/list', { params })
}

async function generateShifts() {
  if (!shiftRange.start || !shiftRange.end) return ElMessage.warning('请选择起止日期')
  const created = await api.post('/schedules/staff-shifts/generate', {
    start_date: shiftRange.start,
    end_date: shiftRange.end,
  })
  ElMessage.success(`已生成 ${created.length} 条排班`)
  loadShifts()
}

function editShift(row) {
  curShift.value = { ...row }
  shiftDialog.value = true
}

async function saveShift() {
  await api.put(`/schedules/staff-shifts/${curShift.value.id}`, {
    shift: curShift.value.shift,
    staff_names: curShift.value.staff_names,
    start_time: curShift.value.start_time,
    end_time: curShift.value.end_time,
    vehicle: curShift.value.vehicle,
    driver: curShift.value.driver,
    notice: curShift.value.notice,
  })
  ElMessage.success('已保存')
  shiftDialog.value = false
  loadShifts()
}

async function publishShift(row) {
  await api.post(`/schedules/staff-shifts/${row.id}/publish`)
  ElMessage.success('排班已发布')
  loadShifts()
}

onMounted(() => {
  loadPlans()
  loadShifts()
})
</script>

<style scoped>
.card-gap {
  margin-bottom: 16px;
}
</style>
