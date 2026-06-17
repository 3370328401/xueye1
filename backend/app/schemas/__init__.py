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
