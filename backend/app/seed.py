"""演示数据初始化脚本。

运行：python -m app.seed
会创建管理员账号、测试用户、采血地点以及示例预约/团体申报/反馈/评价数据。
"""

from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import (
    APPT_COLLECTED,
    APPT_FORM_DONE,
    APPT_PENDING_FORM,
    DICT_DEFAULTS,
    ROLE_ADMIN,
    ROLE_COLLECTOR,
    ROLE_RECRUITER,
    ROLE_DONOR,
)
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import (
    Appointment,
    Dictionary,
    DonorInfo,
    Evaluation,
    Feedback,
    GroupApplication,
    HealthSurvey,
    Location,
    User,
)
from app.routers.appointment import gen_code


def ensure_admin(db: Session):
    admin = db.query(User).filter(User.phone == settings.admin_phone).first()
    if not admin:
        admin = User(
            name=settings.admin_name,
            phone=settings.admin_phone,
            password=hash_password(settings.admin_password),
            role=ROLE_ADMIN,
            dept="信息科",
        )
        db.add(admin)
        db.commit()
    return admin


def seed_staff(db: Session):
    """预置招募科 / 体采科工作人员账号。"""
    staff = [
        ("招募科-张干事", "recruiter", ROLE_RECRUITER, "招募科"),
        ("体采科-李干事", "collector", ROLE_COLLECTOR, "体采科"),
    ]
    for name, phone, role, dept in staff:
        if not db.query(User).filter(User.phone == phone).first():
            db.add(
                User(
                    name=name,
                    phone=phone,
                    password=hash_password("123456"),
                    role=role,
                    dept=dept,
                )
            )
    db.commit()


def seed_dicts(db: Session):
    if db.query(Dictionary).count() > 0:
        return
    for category, labels in DICT_DEFAULTS.items():
        for sort, label in enumerate(labels):
            db.add(
                Dictionary(
                    category=category, label=label, value=label, sort=sort
                )
            )
    db.commit()


def seed_locations(db: Session):
    if db.query(Location).count() > 0:
        return
    locations = [
        Location(name="市中心血站", address="人民路 88 号", remark="工作日 8:00-17:00"),
        Location(name="高新区献血屋", address="科技大道 12 号", remark="每天 9:00-18:00"),
        Location(name="大学城流动采血车", address="学府路口", remark="周末开放"),
    ]
    db.add_all(locations)
    db.commit()


def seed_demo_users(db: Session):
    if db.query(User).filter(User.role == "user").count() > 0:
        return

    user1 = User(
        name="张三",
        phone="13800000001",
        password=hash_password("123456"),
        role=ROLE_DONOR,
    )
    user2 = User(
        name="李四",
        phone="13800000002",
        password=hash_password("123456"),
        role=ROLE_DONOR,
    )
    db.add_all([user1, user2])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    db.add_all(
        [
            DonorInfo(
                user_id=user1.id,
                name="张三",
                id_card="110101199001011234",
                gender="男",
                age=34,
                occupation="工程师",
                phone="13800000001",
                address="幸福路 1 号",
                emergency_contact="王五",
                emergency_phone="13900000001",
            ),
            DonorInfo(
                user_id=user2.id,
                name="李四",
                id_card="110101199202022345",
                gender="女",
                age=32,
                occupation="教师",
                phone="13800000002",
                address="和平路 2 号",
                emergency_contact="赵六",
                emergency_phone="13900000002",
            ),
        ]
    )
    db.commit()

    today = date.today()
    appts = [
        Appointment(
            code=gen_code(),
            user_id=user1.id,
            blood_type="全血",
            appoint_date=today.isoformat(),
            time_slot="09:00-10:00",
            location="市中心血站",
            status=APPT_COLLECTED,
            remark="首次献血",
        ),
        Appointment(
            code=gen_code(),
            user_id=user1.id,
            blood_type="成分血",
            appoint_date=(today + timedelta(days=2)).isoformat(),
            time_slot="14:00-15:00",
            location="高新区献血屋",
            status=APPT_PENDING_FORM,
        ),
        Appointment(
            code=gen_code(),
            user_id=user2.id,
            blood_type="全血",
            appoint_date=(today - timedelta(days=1)).isoformat(),
            time_slot="10:00-11:00",
            location="市中心血站",
            status=APPT_FORM_DONE,
        ),
        Appointment(
            code=gen_code(),
            user_id=user2.id,
            blood_type="成分血",
            appoint_date=(today - timedelta(days=3)).isoformat(),
            time_slot="15:00-16:00",
            location="大学城流动采血车",
            status=APPT_COLLECTED,
        ),
    ]
    db.add_all(appts)
    db.commit()
    for a in appts:
        db.refresh(a)

    db.add(
        HealthSurvey(
            appointment_id=appts[2].id,
            user_id=user2.id,
            is_healthy=True,
            confirmed=True,
            other_note="状态良好",
        )
    )
    db.add(
        Feedback(
            user_id=user1.id,
            appointment_id=appts[0].id,
            swelling=True,
            arm_pain=True,
            other_desc="采血处轻微肿胀",
            contact_phone="13800000001",
            status="已反馈",
        )
    )
    db.add(
        Evaluation(
            user_id=user1.id,
            appointment_id=appts[0].id,
            env_score=5,
            attitude_score=5,
            wait_score=4,
            skill_score=5,
            notice_score=5,
            overall_score=5,
            suggestion="服务很好，环境整洁",
        )
    )
    db.add(
        Evaluation(
            user_id=user2.id,
            appointment_id=appts[3].id,
            env_score=4,
            attitude_score=5,
            wait_score=3,
            skill_score=4,
            notice_score=4,
            overall_score=4,
            suggestion="等待时间稍长",
        )
    )
    db.commit()


def seed_groups(db: Session):
    if db.query(GroupApplication).count() > 0:
        return
    db.add_all(
        [
            GroupApplication(
                unit_name="蓝天科技有限公司",
                credit_code="91110000MA00000001",
                unit_address="创新大厦 10 层",
                contact_name="孙经理",
                contact_phone="13700000001",
                expected_count=50,
                expected_date=(date.today() + timedelta(days=7)).isoformat(),
                status="待受理",
            ),
            GroupApplication(
                unit_name="实验中学",
                credit_code="91110000MA00000002",
                unit_address="文化路 5 号",
                contact_name="周老师",
                contact_phone="13700000002",
                expected_count=120,
                expected_date=(date.today() + timedelta(days=14)).isoformat(),
                status="受理中",
                admin_remark="已联系，安排流动采血车",
            ),
        ]
    )
    db.commit()


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_admin(db)
        seed_staff(db)
        seed_dicts(db)
        seed_locations(db)
        seed_demo_users(db)
        seed_groups(db)
        print("演示数据初始化完成。")
        print(f"管理员账号: {settings.admin_phone} / {settings.admin_password}")
        print("工作人员: recruiter / 123456 (招募科) , collector / 123456 (体采科)")
        print("测试用户: 13800000001 / 123456 , 13800000002 / 123456")
    finally:
        db.close()


if __name__ == "__main__":
    run()
