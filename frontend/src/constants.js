// 预约状态（与后端 app/core/constants.py 对齐）
export const APPOINTMENT_STATUSES = [
  '待填双表及签字确认',
  '双表已填且确认',
  '待现场采血',
  '正在现场采血',
  '已完成现场采血',
  '作废',
]

export const APPOINTMENT_STATUS_TYPE = {
  待填双表及签字确认: 'warning',
  双表已填且确认: 'info',
  待现场采血: 'info',
  正在现场采血: 'primary',
  已完成现场采血: 'success',
  作废: 'danger',
}

export const appointmentStatusType = (s) => APPOINTMENT_STATUS_TYPE[s] || 'info'

export const GROUP_STATUSES = ['待受理', '受理中', '受理已完成', '已驳回']
export const GROUP_STATUS_TYPE = {
  待受理: 'warning',
  受理中: 'primary',
  受理已完成: 'success',
  已驳回: 'danger',
}

export const FEEDBACK_STATUSES = ['已反馈', '正在联系处理', '已解决']
export const FEEDBACK_STATUS_TYPE = {
  已反馈: 'warning',
  正在联系处理: 'primary',
  已解决: 'success',
}

export const ROLE_LABELS = {
  user: '个人献血者',
  group_contact: '团体单位联系人',
  recruiter: '招募科',
  collector: '体采科',
  admin: '系统管理员',
}
