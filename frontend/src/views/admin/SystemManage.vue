<template>
  <div>
    <h2>系统管理</h2>
    <el-tabs v-model="tab">
      <!-- 组织机构 -->
      <el-tab-pane label="组织机构" name="org">
        <el-button type="success" class="card-gap" @click="openOrg()">新增机构</el-button>
        <el-table :data="orgs" stripe>
          <el-table-column prop="name" label="机构名称" />
          <el-table-column prop="code" label="编码" width="100" />
          <el-table-column prop="org_type" label="类型" width="90" />
          <el-table-column label="上级机构" width="140">
            <template #default="{ row }">{{ orgName(row.parent_id) }}</template>
          </el-table-column>
          <el-table-column prop="leader" label="负责人" width="110" />
          <el-table-column prop="phone" label="电话" width="140" />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button size="small" @click="openOrg(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="delOrg(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="staff">
        <el-button type="success" class="card-gap" @click="openStaff()">新增工作人员</el-button>
        <el-table :data="staff" stripe>
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="phone" label="账号/手机号" width="160" />
          <el-table-column prop="role_label" label="角色" width="130" />
          <el-table-column prop="dept" label="科室" width="120" />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="260">
            <template #default="{ row }">
              <el-button size="small" @click="openStaff(row)">编辑</el-button>
              <el-button size="small" type="warning" @click="resetPwd(row)">重置密码</el-button>
              <el-button size="small" type="danger" @click="delStaff(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 角色权限 -->
      <el-tab-pane label="角色权限" name="role">
        <el-table :data="roles" stripe>
          <el-table-column prop="label" label="角色" width="160" />
          <el-table-column label="权限">
            <template #default="{ row }">
              <el-tag v-for="p in row.permissions" :key="p" class="perm-tag">{{ p }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 系统参数 -->
      <el-tab-pane label="系统参数" name="param">
        <el-table :data="params" stripe>
          <el-table-column prop="label" label="参数名称" width="220" />
          <el-table-column label="参数值" width="200">
            <template #default="{ row }">
              <el-input v-model="row.value" size="small" />
            </template>
          </el-table-column>
          <el-table-column prop="remark" label="说明" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="saveParam(row)">保存</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 选项字典 -->
      <el-tab-pane label="选项字典" name="dict">
        <el-button type="success" class="card-gap" @click="openDict()">新增字典项</el-button>
        <el-table :data="dicts" stripe>
          <el-table-column prop="category" label="分类" width="160" />
          <el-table-column prop="label" label="名称" />
          <el-table-column prop="value" label="值" />
          <el-table-column prop="sort" label="排序" width="80" />
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button size="small" @click="openDict(row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 操作日志 -->
      <el-tab-pane label="操作日志" name="log">
        <el-input v-model="logKeyword" placeholder="按操作人/对象/详情搜索" class="log-search" @keyup.enter="loadLogs">
          <template #append><el-button @click="loadLogs">搜索</el-button></template>
        </el-input>
        <el-table :data="logs" stripe>
          <el-table-column prop="created_at" label="时间" width="180">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column prop="user_name" label="操作人" width="120" />
          <el-table-column prop="role" label="角色" width="110" />
          <el-table-column prop="action" label="操作" width="140" />
          <el-table-column prop="target" label="对象" />
          <el-table-column prop="detail" label="详情" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 机构弹窗 -->
    <el-dialog v-model="orgDialog" :title="orgForm.id ? '编辑机构' : '新增机构'" width="480px">
      <el-form :model="orgForm" label-width="90px">
        <el-form-item label="机构名称"><el-input v-model="orgForm.name" /></el-form-item>
        <el-form-item label="编码"><el-input v-model="orgForm.code" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="orgForm.org_type" style="width: 160px">
            <el-option v-for="t in orgTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="上级机构">
          <el-select v-model="orgForm.parent_id" clearable style="width: 200px">
            <el-option v-for="o in orgs" :key="o.id" :label="o.name" :value="o.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人"><el-input v-model="orgForm.leader" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="orgForm.phone" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="orgForm.is_active" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="orgForm.remark" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="orgDialog = false">取消</el-button>
        <el-button type="primary" @click="saveOrg">保存</el-button>
      </template>
    </el-dialog>

    <!-- 工作人员弹窗 -->
    <el-dialog v-model="staffDialog" :title="staffForm.id ? '编辑工作人员' : '新增工作人员'" width="460px">
      <el-form :model="staffForm" label-width="90px">
        <el-form-item label="姓名"><el-input v-model="staffForm.name" /></el-form-item>
        <el-form-item label="账号/手机号">
          <el-input v-model="staffForm.phone" :disabled="!!staffForm.id" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="staffForm.role" style="width: 200px">
            <el-option label="招募科工作人员" value="recruiter" />
            <el-option label="体采科工作人员" value="collector" />
            <el-option label="系统管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="科室"><el-input v-model="staffForm.dept" /></el-form-item>
        <el-form-item label="初始密码" v-if="!staffForm.id">
          <el-input v-model="staffForm.password" />
        </el-form-item>
        <el-form-item label="状态" v-if="staffForm.id"><el-switch v-model="staffForm.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="staffDialog = false">取消</el-button>
        <el-button type="primary" @click="saveStaff">保存</el-button>
      </template>
    </el-dialog>

    <!-- 字典弹窗 -->
    <el-dialog v-model="dictDialog" :title="dictForm.id ? '编辑字典项' : '新增字典项'" width="440px">
      <el-form :model="dictForm" label-width="80px">
        <el-form-item label="分类"><el-input v-model="dictForm.category" placeholder="如 occupation/blood_type" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="dictForm.label" /></el-form-item>
        <el-form-item label="值"><el-input v-model="dictForm.value" placeholder="留空默认同名称" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="dictForm.sort" :min="0" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="dictForm.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dictDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDict">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api'

const tab = ref('org')
const orgs = ref([])
const orgTypes = ref(['中心', '科室', '采血点'])
const staff = ref([])
const roles = ref([])
const params = ref([])
const dicts = ref([])
const logs = ref([])
const logKeyword = ref('')

function formatTime(t) {
  return t ? new Date(t).toLocaleString() : ''
}
function orgName(id) {
  const o = orgs.value.find((x) => x.id === id)
  return o ? o.name : '-'
}

// 组织机构
const orgDialog = ref(false)
const orgForm = reactive({ id: null, name: '', code: '', org_type: '科室', parent_id: null, leader: '', phone: '', is_active: true, remark: '' })
function openOrg(row) {
  if (row) Object.assign(orgForm, row)
  else Object.assign(orgForm, { id: null, name: '', code: '', org_type: '科室', parent_id: null, leader: '', phone: '', is_active: true, remark: '' })
  orgDialog.value = true
}
async function saveOrg() {
  const payload = { name: orgForm.name, code: orgForm.code, org_type: orgForm.org_type, parent_id: orgForm.parent_id, leader: orgForm.leader, phone: orgForm.phone, is_active: orgForm.is_active, remark: orgForm.remark }
  if (orgForm.id) await api.put(`/system/orgs/${orgForm.id}`, payload)
  else await api.post('/system/orgs', payload)
  ElMessage.success('已保存')
  orgDialog.value = false
  loadOrgs()
}
async function delOrg(row) {
  await ElMessageBox.confirm('确认删除该机构？', '提示')
  await api.delete(`/system/orgs/${row.id}`)
  ElMessage.success('已删除')
  loadOrgs()
}
async function loadOrgs() {
  orgs.value = await api.get('/system/orgs')
}

// 工作人员
const staffDialog = ref(false)
const staffForm = reactive({ id: null, name: '', phone: '', role: 'recruiter', dept: '', password: '123456', is_active: true })
function openStaff(row) {
  if (row) Object.assign(staffForm, { id: row.id, name: row.name, phone: row.phone, role: row.role, dept: row.dept, is_active: row.is_active, password: '' })
  else Object.assign(staffForm, { id: null, name: '', phone: '', role: 'recruiter', dept: '', password: '123456', is_active: true })
  staffDialog.value = true
}
async function saveStaff() {
  if (staffForm.id) {
    await api.put(`/system/staff/${staffForm.id}`, { name: staffForm.name, role: staffForm.role, dept: staffForm.dept, is_active: staffForm.is_active })
  } else {
    await api.post('/system/staff', { name: staffForm.name, phone: staffForm.phone, role: staffForm.role, dept: staffForm.dept, password: staffForm.password })
  }
  ElMessage.success('已保存')
  staffDialog.value = false
  loadStaff()
}
async function resetPwd(row) {
  const { value } = await ElMessageBox.prompt('请输入新密码', '重置密码', { inputValue: '123456' })
  await api.post(`/system/staff/${row.id}/reset-password`, { password: value })
  ElMessage.success('密码已重置')
}
async function delStaff(row) {
  await ElMessageBox.confirm(`确认删除工作人员 ${row.name}？`, '提示')
  await api.delete(`/system/staff/${row.id}`)
  ElMessage.success('已删除')
  loadStaff()
}
async function loadStaff() {
  staff.value = await api.get('/system/staff')
}

// 系统参数
async function saveParam(row) {
  await api.put(`/system/params/${row.id}`, { value: row.value })
  ElMessage.success('已保存')
}

// 字典
const dictDialog = ref(false)
const dictForm = reactive({ id: null, category: '', label: '', value: '', sort: 0, is_active: true })
function openDict(row) {
  if (row) Object.assign(dictForm, row)
  else Object.assign(dictForm, { id: null, category: '', label: '', value: '', sort: 0, is_active: true })
  dictDialog.value = true
}
async function saveDict() {
  const payload = { category: dictForm.category, label: dictForm.label, value: dictForm.value, sort: dictForm.sort, is_active: dictForm.is_active }
  if (dictForm.id) await api.put(`/dicts/admin/${dictForm.id}`, payload)
  else await api.post('/dicts/admin', payload)
  ElMessage.success('已保存')
  dictDialog.value = false
  loadDicts()
}
async function loadDicts() {
  dicts.value = await api.get('/dicts/admin/list')
}

// 日志
async function loadLogs() {
  logs.value = await api.get('/audit-logs', { params: { keyword: logKeyword.value || undefined } })
}

onMounted(async () => {
  loadOrgs()
  loadStaff()
  roles.value = await api.get('/system/roles')
  params.value = await api.get('/system/params')
  loadDicts()
  loadLogs()
  try {
    orgTypes.value = await api.get('/system/org-types')
  } catch (e) {
    /* keep default */
  }
})
</script>

<style scoped>
.card-gap {
  margin-bottom: 14px;
}
.perm-tag {
  margin: 2px 4px;
}
.log-search {
  width: 320px;
  margin-bottom: 14px;
}
</style>
