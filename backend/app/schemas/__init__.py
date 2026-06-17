from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ---------- Auth ----------
class RegisterIn(BaseModel):
    name: str
    phone: str
    password: str


class LoginIn(BaseModel):
    phone: str
    password: str


class CodeLoginIn(BaseModel):
    phone: str
    code: str


class WechatLoginIn(BaseModel):
    openid: str = ""


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str
    user_id: int


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    role: str
    is_active: bool
    created_at: datetime


# ---------- Donor info ----------
class DonorInfoIn(BaseModel):
    name: str = ""
    id_card: str = ""
    gender: str = ""
    age: int | None = None
    occupation: str = ""
    phone: str = ""
    address: str = ""
    emergency_contact: str = ""
    emergency_phone: str = ""


class DonorInfoOut(DonorInfoIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    updated_at: datetime


# ---------- Appointment ----------
class AppointmentIn(BaseModel):
    blood_type: str
    appoint_date: str
    time_slot: str
    location: str
    remark: str = ""


class AppointmentStatusIn(BaseModel):
    status: str


class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    user_id: int
    blood_type: str
    appoint_date: str
    time_slot: str
    location: str
    status: str
    remark: str
    created_at: datetime
    updated_at: datetime


class AdminAppointmentOut(AppointmentOut):
    user_name: str = ""
    user_phone: str = ""


# ---------- Health survey ----------
class HealthSurveyIn(BaseModel):
    appointment_id: int
    is_healthy: bool = True
    drank_alcohol: bool = False
    took_medicine: bool = False
    has_symptoms: bool = False
    has_major_disease: bool = False
    unsuitable: bool = False
    other_note: str = ""
    confirmed: bool = False


class HealthSurveyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    appointment_id: int
    user_id: int
    is_healthy: bool
    drank_alcohol: bool
    took_medicine: bool
    has_symptoms: bool
    has_major_disease: bool
    unsuitable: bool
    other_note: str
    confirmed: bool
    created_at: datetime


class AdminHealthSurveyOut(HealthSurveyOut):
    user_name: str = ""
    user_phone: str = ""
    appointment_code: str = ""


# ---------- Group application ----------
class GroupApplicationIn(BaseModel):
    unit_name: str
    credit_code: str = ""
    unit_address: str = ""
    contact_name: str
    contact_phone: str
    unit_type: str = "其他"
    expected_count: int = 0
    expected_date: str = ""
    remark: str = ""


class GroupStatusIn(BaseModel):
    status: str
    admin_remark: str = ""


class GroupApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    unit_name: str
    credit_code: str
    unit_address: str
    contact_name: str
    contact_phone: str
    unit_type: str
    expected_count: int
    expected_date: str
    status: str
    admin_remark: str
    created_at: datetime
    updated_at: datetime


# ---------- Group activity ----------
class GroupActivityIn(BaseModel):
    application_id: int | None = None
    unit_name: str
    unit_type: str = "其他"
    contact_name: str = ""
    contact_phone: str = ""
    center_contact: str = ""
    activity_date: str = ""
    location: str = ""
    expected_count: int = 0
    remark: str = ""


class GroupActivityUpdate(BaseModel):
    actual_date: str = ""
    actual_count: int = 0
    center_contact: str = ""
    remark: str = ""


class GroupActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    flow_no: str
    application_id: int | None
    unit_name: str
    unit_type: str
    contact_name: str
    contact_phone: str
    center_contact: str
    activity_date: str
    actual_date: str
    location: str
    expected_count: int
    actual_count: int
    year: int
    poster_id: int | None
    remark: str
    created_at: datetime


# ---------- Poster ----------
class PosterTemplateIn(BaseModel):
    name: str
    bg_color: str = "#c62828"
    title_style: str = "default"
    contact: str = ""
    qrcode_text: str = ""
    is_active: bool = True


class PosterTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    bg_color: str
    title_style: str
    contact: str
    qrcode_text: str
    is_active: bool
    created_at: datetime


class PosterIn(BaseModel):
    template_id: int | None = None
    unit_name: str
    contact_phone: str = ""
    title: str = "无偿献血，从我做起"
    activity_date: str = ""
    location: str = ""
    bg_color: str = "#c62828"
    contact: str = ""
    qrcode_text: str = ""


class PosterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    template_id: int | None
    unit_name: str
    contact_phone: str
    title: str
    activity_date: str
    location: str
    bg_color: str
    contact: str
    qrcode_text: str
    status: str
    pushed_at: datetime | None
    created_at: datetime


# ---------- 排班计划 ----------
class PlanGenerateIn(BaseModel):
    plan_type: str = "周"
    start_date: str
    end_date: str


class BloodPlanUpdate(BaseModel):
    plan_date: str = ""
    location: str = ""
    expected_count: int = 0
    arrive_time: str = ""
    remark: str = ""


class BloodPlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_type: str
    activity_id: int | None
    plan_date: str
    weekday: str
    location: str
    unit_name: str
    contact_phone: str
    expected_count: int
    arrive_time: str
    status: str
    remark: str
    created_at: datetime


class ShiftGenerateIn(BaseModel):
    start_date: str
    end_date: str


class StaffShiftUpdate(BaseModel):
    shift: str = ""
    staff_names: str = ""
    start_time: str = ""
    end_time: str = ""
    vehicle: str = ""
    driver: str = ""
    notice: str = ""


class StaffShiftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shift: str
    shift_date: str
    weekday: str
    location: str
    expected_count: int
    staff_names: str
    start_time: str
    end_time: str
    vehicle: str
    driver: str
    notice: str
    status: str
    created_at: datetime


# ---------- Feedback ----------
class FeedbackIn(BaseModel):
    appointment_id: int
    swelling: bool = False
    redness: bool = False
    arm_pain: bool = False
    other_desc: str = ""
    contact_phone: str = ""


class FeedbackStatusIn(BaseModel):
    status: str
    result: str = ""


class FeedbackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    appointment_id: int
    swelling: bool
    redness: bool
    arm_pain: bool
    other_desc: str
    contact_phone: str
    status: str
    result: str
    created_at: datetime
    updated_at: datetime


class AdminFeedbackOut(FeedbackOut):
    user_name: str = ""
    user_phone: str = ""
    appointment_code: str = ""


# ---------- Evaluation ----------
class EvaluationIn(BaseModel):
    appointment_id: int
    env_score: int = 5
    attitude_score: int = 5
    wait_score: int = 5
    skill_score: int = 5
    notice_score: int = 5
    overall_score: int = 5
    suggestion: str = ""


class EvaluationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    appointment_id: int
    env_score: int
    attitude_score: int
    wait_score: int
    skill_score: int
    notice_score: int
    overall_score: int
    suggestion: str
    created_at: datetime


class AdminEvaluationOut(EvaluationOut):
    user_name: str = ""
    user_phone: str = ""
    appointment_code: str = ""


# ---------- 评价模板 ----------
class EvalTemplateIn(BaseModel):
    name: str
    blood_type: str = "全血"
    indicators: list[str] = []
    reward_points: int = 20
    is_active: bool = True


class EvalTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    blood_type: str
    indicators: str
    reward_points: int
    is_active: bool
    created_at: datetime


# ---------- 积分 / 兑换 ----------
class PointRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    change: int
    balance_after: int
    reason: str
    ref: str
    created_at: datetime


class PointSummaryOut(BaseModel):
    balance: int
    records: list[PointRecordOut]


class GiftIn(BaseModel):
    name: str
    points_cost: int = 0
    stock: int = 0
    description: str = ""
    is_active: bool = True


class GiftOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    points_cost: int
    stock: int
    description: str
    is_active: bool


class ExchangeIn(BaseModel):
    gift_id: int


class ExchangeStatusIn(BaseModel):
    status: str


class ExchangeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    gift_id: int
    gift_name: str
    points_cost: int
    status: str
    created_at: datetime
    updated_at: datetime


class AdminExchangeOut(ExchangeOut):
    user_name: str = ""
    user_phone: str = ""


# ---------- 叫号显示 ----------
class QueueItemOut(BaseModel):
    code: str
    name: str
    blood_type: str
    status: str
    ahead: int


# ---------- 消息推送 ----------
class MessageIn(BaseModel):
    title: str
    content: str = ""
    msg_type: str = "系统通知"
    scope: str = "普发"
    target: dict = {}


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    msg_type: str
    scope: str
    target: str
    status: str
    created_at: datetime
    published_at: datetime | None = None


class AdminMessageOut(MessageOut):
    read_count: int = 0


class UserMessageOut(MessageOut):
    is_read: bool = False


# ---------- 个人信息查询（嵌入，mock） ----------
class BloodTestOut(BaseModel):
    seq: int
    test_date: str
    result: str
    detail: str = ""


class DonationTraceOut(BaseModel):
    seq: int
    donate_date: str
    location: str
    volume_ml: int
    blood_type: str
    identity: str


class PersonalInfoOut(BaseModel):
    e_cert_no: str
    total_volume_ml: int
    donate_count: int
    points_balance: int
    blood_usage: list[dict]
    tests: list[BloodTestOut]
    traces: list[DonationTraceOut]


# ---------- 系统管理：组织机构 ----------
class OrgIn(BaseModel):
    name: str
    code: str = ""
    org_type: str = "科室"
    parent_id: int | None = None
    leader: str = ""
    phone: str = ""
    is_active: bool = True
    remark: str = ""


class OrgOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    org_type: str
    parent_id: int | None
    leader: str
    phone: str
    is_active: bool
    remark: str


# ---------- 系统管理：用户管理 ----------
class StaffIn(BaseModel):
    name: str
    phone: str
    password: str = "123456"
    role: str
    dept: str = ""


class StaffUpdateIn(BaseModel):
    name: str
    role: str
    dept: str = ""
    is_active: bool = True


class StaffOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    role: str
    role_label: str = ""
    dept: str
    is_active: bool
    created_at: datetime


class PasswordResetIn(BaseModel):
    password: str = "123456"


# ---------- 系统管理：角色权限 ----------
class RoleOut(BaseModel):
    role: str
    label: str
    permissions: list[str]


# ---------- 系统管理：系统参数 ----------
class SysParamIn(BaseModel):
    value: str


class SysParamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    value: str
    label: str
    remark: str


# ---------- Location ----------
class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    is_active: bool
    remark: str


# ---------- External ----------
class ExternalLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    api_type: str
    request: str
    response: str
    status: str
    created_at: datetime


# ---------- Dictionary ----------
class DictIn(BaseModel):
    category: str
    label: str
    value: str = ""
    sort: int = 0
    is_active: bool = True


class DictOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    label: str
    value: str
    sort: int
    is_active: bool


# ---------- 双表 / 电子签署 ----------
class SignIn(BaseModel):
    appointment_id: int
    confirmed: bool = True
    signature: str = ""  # 模拟手写签名/确认串


class SignRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    appointment_id: int
    form_name: str
    status: str
    sign_no: str
    content: str
    signed_at: datetime
    verified: bool
    appointment_code: str = ""
    user_name: str = ""
    user_phone: str = ""


# ---------- Audit log ----------
class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    user_name: str
    role: str
    action: str
    target: str
    detail: str
    created_at: datetime
