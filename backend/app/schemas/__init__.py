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
    expected_count: int
    expected_date: str
    status: str
    admin_remark: str
    created_at: datetime
    updated_at: datetime


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
