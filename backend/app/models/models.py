from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import APPT_PENDING_FORM, ROLE_DONOR
from app.core.database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    # user | group_contact | recruiter | collector | admin
    role: Mapped[str] = mapped_column(String(20), default=ROLE_DONOR)
    dept: Mapped[str] = mapped_column(String(50), default="")  # 工作人员所属科室
    openid: Mapped[str] = mapped_column(String(64), default="")  # 微信 openid（模拟）
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    donor_info: Mapped["DonorInfo"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class DonorInfo(Base):
    __tablename__ = "donor_infos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    name: Mapped[str] = mapped_column(String(50), default="")
    id_card: Mapped[str] = mapped_column(String(30), default="")
    gender: Mapped[str] = mapped_column(String(10), default="")
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    occupation: Mapped[str] = mapped_column(String(50), default="")
    phone: Mapped[str] = mapped_column(String(20), default="")
    address: Mapped[str] = mapped_column(String(255), default="")
    emergency_contact: Mapped[str] = mapped_column(String(50), default="")
    emergency_phone: Mapped[str] = mapped_column(String(20), default="")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=now_utc, onupdate=now_utc
    )

    user: Mapped["User"] = relationship(back_populates="donor_info")


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    blood_type: Mapped[str] = mapped_column(String(20))  # 全血 | 成分血
    appoint_date: Mapped[str] = mapped_column(String(20))
    time_slot: Mapped[str] = mapped_column(String(30))
    location: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default=APPT_PENDING_FORM)
    remark: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=now_utc, onupdate=now_utc
    )

    user: Mapped["User"] = relationship(back_populates="appointments")


class HealthSurvey(Base):
    __tablename__ = "health_surveys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_healthy: Mapped[bool] = mapped_column(Boolean, default=True)
    drank_alcohol: Mapped[bool] = mapped_column(Boolean, default=False)
    took_medicine: Mapped[bool] = mapped_column(Boolean, default=False)
    has_symptoms: Mapped[bool] = mapped_column(Boolean, default=False)
    has_major_disease: Mapped[bool] = mapped_column(Boolean, default=False)
    unsuitable: Mapped[bool] = mapped_column(Boolean, default=False)
    other_note: Mapped[str] = mapped_column(Text, default="")
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)


class GroupApplication(Base):
    __tablename__ = "group_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unit_name: Mapped[str] = mapped_column(String(100))
    credit_code: Mapped[str] = mapped_column(String(50), default="")
    unit_address: Mapped[str] = mapped_column(String(255), default="")
    contact_name: Mapped[str] = mapped_column(String(50))
    contact_phone: Mapped[str] = mapped_column(String(20), index=True)
    expected_count: Mapped[int] = mapped_column(Integer, default=0)
    expected_date: Mapped[str] = mapped_column(String(20), default="")
    status: Mapped[str] = mapped_column(String(20), default="待受理")
    admin_remark: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=now_utc, onupdate=now_utc
    )


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"))
    swelling: Mapped[bool] = mapped_column(Boolean, default=False)
    redness: Mapped[bool] = mapped_column(Boolean, default=False)
    arm_pain: Mapped[bool] = mapped_column(Boolean, default=False)
    other_desc: Mapped[str] = mapped_column(Text, default="")
    contact_phone: Mapped[str] = mapped_column(String(20), default="")
    status: Mapped[str] = mapped_column(String(20), default="已反馈")
    result: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=now_utc, onupdate=now_utc
    )


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"))
    env_score: Mapped[int] = mapped_column(Integer, default=5)
    attitude_score: Mapped[int] = mapped_column(Integer, default=5)
    wait_score: Mapped[int] = mapped_column(Integer, default=5)
    skill_score: Mapped[int] = mapped_column(Integer, default=5)
    notice_score: Mapped[int] = mapped_column(Integer, default=5)
    overall_score: Mapped[int] = mapped_column(Integer, default=5)
    suggestion: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(255), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    remark: Mapped[str] = mapped_column(String(255), default="")


class ExternalLog(Base):
    __tablename__ = "external_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_type: Mapped[str] = mapped_column(String(50))
    request: Mapped[str] = mapped_column(Text, default="")
    response: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="success")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)


class AuditLog(Base):
    """操作日志审计表。"""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    user_name: Mapped[str] = mapped_column(String(50), default="")
    role: Mapped[str] = mapped_column(String(20), default="")
    action: Mapped[str] = mapped_column(String(50))  # 操作类型
    target: Mapped[str] = mapped_column(String(100), default="")  # 操作对象
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)


class Dictionary(Base):
    """选项字典表。"""

    __tablename__ = "dictionaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    label: Mapped[str] = mapped_column(String(100))
    value: Mapped[str] = mapped_column(String(100))
    sort: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SignRecord(Base):
    """双表电子签署记录。"""

    __tablename__ = "sign_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"))
    form_name: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="已签署")
    sign_no: Mapped[str] = mapped_column(String(40), default="")  # 模拟签署流水号
    content: Mapped[str] = mapped_column(Text, default="")  # 表单内容快照(JSON)
    signed_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)  # 现场审验
