"""全局业务常量：角色、预约状态机、字典分类等。"""

# ---------- 角色 ----------
ROLE_DONOR = "user"  # 个人献血者
ROLE_GROUP = "group_contact"  # 团体单位联系人
ROLE_RECRUITER = "recruiter"  # 招募科工作人员
ROLE_COLLECTOR = "collector"  # 体采科工作人员
ROLE_ADMIN = "admin"  # 系统管理员

ROLE_LABELS = {
    ROLE_DONOR: "个人献血者",
    ROLE_GROUP: "团体单位联系人",
    ROLE_RECRUITER: "招募科工作人员",
    ROLE_COLLECTOR: "体采科工作人员",
    ROLE_ADMIN: "系统管理员",
}

# 后台工作人员角色（可进入管理端）
STAFF_ROLES = (ROLE_RECRUITER, ROLE_COLLECTOR, ROLE_ADMIN)

# ---------- 预约状态机 ----------
APPT_PENDING_FORM = "待填双表及签字确认"
APPT_FORM_DONE = "双表已填且确认"
APPT_WAIT_COLLECT = "待现场采血"
APPT_COLLECTING = "正在现场采血"
APPT_COLLECTED = "已完成现场采血"
APPT_VOID = "作废"

APPOINTMENT_STATUSES = [
    APPT_PENDING_FORM,
    APPT_FORM_DONE,
    APPT_WAIT_COLLECT,
    APPT_COLLECTING,
    APPT_COLLECTED,
    APPT_VOID,
]

# 允许的状态流转：当前状态 -> 可流转到的状态集合
APPOINTMENT_TRANSITIONS = {
    APPT_PENDING_FORM: {APPT_FORM_DONE, APPT_VOID},
    APPT_FORM_DONE: {APPT_WAIT_COLLECT, APPT_VOID},
    APPT_WAIT_COLLECT: {APPT_COLLECTING, APPT_VOID},
    APPT_COLLECTING: {APPT_COLLECTED, APPT_VOID},
    APPT_COLLECTED: set(),
    APPT_VOID: set(),
}


def can_transition(current: str, target: str) -> bool:
    return target in APPOINTMENT_TRANSITIONS.get(current, set())


# ---------- 双表 / 电子签署 ----------
FORM_PERSONAL = "献血者个人信息登记表"
FORM_HEALTH = "健康征询表"
DOUBLE_FORM_NAMES = [FORM_PERSONAL, FORM_HEALTH]

SIGN_PENDING = "待签署"
SIGN_DONE = "已签署"

# ---------- 献血间隔规则（天）----------
# 全血两次间隔不少于 6 个月；单采成分血间隔不少于 14 天
DONATE_INTERVAL_DAYS = {
    "全血": 180,
    "成分血": 14,
}

# ---------- 团体申报状态 ----------
GROUP_STATUSES = ["待受理", "受理中", "受理已完成", "已驳回"]

# ---------- 团体单位类型 ----------
UNIT_TYPES = ["学校", "政府", "军队", "企业", "其他"]

# ---------- 反馈处理状态 ----------
FEEDBACK_STATUSES = ["已反馈", "正在联系处理", "已解决"]

# ---------- 积分兑换状态 ----------
EXCHANGE_STATUSES = ["待处理", "处理中", "已兑换", "已取消"]

# ---------- 现场采血/叫号相关状态 ----------
QUEUE_STATUSES = [APPT_WAIT_COLLECT, APPT_COLLECTING]

# ---------- 消息推送 ----------
MESSAGE_TYPES = [
    "国家政策",
    "地方政策",
    "科普知识",
    "活动通知",
    "预约提醒",
    "健康指导",
    "系统通知",
]
MESSAGE_SCOPES = ["普发", "定向"]
MESSAGE_STATUSES = ["草稿", "已发布", "已撤回"]

# ---------- 组织机构类型 ----------
ORG_TYPES = ["中心", "科室", "采血点"]

# ---------- 角色权限矩阵（用于系统管理-角色权限展示与说明） ----------
ROLE_PERMISSIONS = {
    ROLE_DONOR: ["注册登录", "个人信息维护", "健康信息填写", "预约管理", "双表签署", "评价", "反馈", "积分查询", "消息查看"],
    ROLE_GROUP: ["团体申报", "申报状态查看", "团体活动查看", "宣传海报查看", "团体预约信息查看"],
    ROLE_RECRUITER: ["团体受理", "预约统计", "海报生成", "消息推送", "反馈处理", "招募计划管理"],
    ROLE_COLLECTOR: ["排班管理", "现场预约查看", "双表审验", "采血状态查看"],
    ROLE_ADMIN: ["用户管理", "角色权限", "组织机构", "参数配置", "模板配置", "日志查看"],
}

# ---------- 系统参数默认值 ----------
SYS_PARAM_DEFAULTS = [
    ("list_page_size", "20", "列表默认行数", "工作台列表每页默认显示条数"),
    ("remind_advance_hours", "24", "预约提前提醒时间(小时)", "预约前多少小时发送提醒"),
    ("appointment_editable_hours", "24", "预约可修改时间范围(小时)", "预约开始前多少小时内可修改"),
    ("eval_reward_points", "20", "评价默认送积分", "未匹配模板时的默认评价积分"),
    ("whole_blood_interval_days", "180", "全血献血间隔(天)", "两次全血献血最小间隔"),
    ("apheresis_interval_days", "14", "成分血献血间隔(天)", "两次成分血献血最小间隔"),
]

# ---------- 字典分类（选项字典） ----------
DICT_DEFAULTS = {
    "gender": ["男", "女"],
    "occupation": ["工人", "农民", "教师", "学生", "医务人员", "公务员", "工程师", "自由职业", "其他"],
    "education": ["初中及以下", "高中/中专", "大专", "本科", "硕士及以上"],
    "blood_type": ["全血", "成分血"],
    "unit_type": ["学校", "政府", "军队", "企业", "其他"],
    "feedback_type": ["肿包", "发红", "手臂疼痛", "头晕乏力", "其他"],
    "eval_indicator": ["采血环境", "工作人员态度", "等待时间", "业务技能", "注意事项讲解", "小礼品满意度"],
    "message_type": ["国家政策", "地方政策", "科普知识", "活动通知", "预约提醒", "健康指导", "系统通知"],
    "time_slot": ["09:00-10:00", "10:00-11:00", "11:00-12:00", "14:00-15:00", "15:00-16:00", "16:00-17:00"],
}
