# ============================================================================
# User Model - מודל המשתמש
# ============================================================================
# קובץ זה מגדיר את מודל המשתמש (User) במסד הנתונים.
# כולל: תפקידים (roles), טבלת קשר בין משתמשים למדורים,
# ואת כל השדות של המשתמש בDB.
#
# Permission Hierarchy (היררכיית הרשאות):
#   super_admin > admin > agent
#   - super_admin: גישה מלאה - ניהול כל המשתמשים, מדורים ופגישות
#   - admin: יכול ליצור agents, לנהל מדורים ופגישות
#   - agent: צפייה בלבד - רואה רק את הפגישות לפי המדורים והגישה שלו
# ============================================================================

from enum import Enum
import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, Enum as SqlEnum, Table
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID


# --- UserRole Enum - תפקידי המשתמש ---
# כל משתמש חייב להיות אחד מ-3 התפקידים האלה.
# הEnum יורש מ-str כדי שהערך יישמר כטקסט בDB ויהיה קל להשוות.
class UserRole(str, Enum):
    super_admin = "super_admin"  # מנהל על - שליטה מלאה על המערכת
    admin = "admin"              # מנהל - יכול לנהל agents ופגישות
    agent = "agent"              # סוכן - צפייה בלבד לפי הרשאות
    viewer = "viewer"            # צופה - צפייה בסיסית לפי הרשאות מדור


# --- Association Table: user_mador_association ---
# טבלת קשר Many-to-Many בין משתמשים (users) למדורים (madors).
# כל שורה מייצגת שיוך של משתמש למדור מסוים.
# ondelete="CASCADE" - אם מוחקים משתמש או מדור, השיוך נמחק אוטומטית.
user_mador_association = Table(
    "user_mador_association",
    Base.metadata,
    Column("user_id", PostgresUUID(as_uuid=True), ForeignKey("users.UUID", ondelete="CASCADE"), primary_key=True),
    Column("mador_id", PostgresUUID(as_uuid=True), ForeignKey("madors.UUID", ondelete="CASCADE"), primary_key=True)
)


# --- User Model - טבלת המשתמשים ---
class User(Base):
    __tablename__ = "users"

    # מזהה ייחודי אוניברסלי - נוצר אוטומטית
    UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    # מזהה משתמש (כמו מספר עובד) - חייב להיות ייחודי
    s_id = Column(String(50), unique=True, nullable=False, index=True)
    # שם המשתמש לתצוגה
    username = Column(String(50), nullable=False)
    # סיסמה מוצפנת (Argon2 hash) - לעולם לא נשמרת כטקסט רגיל
    password = Column(String(250), nullable=False)
    # תפקיד המשתמש - ברירת מחדל: agent
    role = Column(SqlEnum(UserRole), nullable=False, default=UserRole.agent)

    # --- Relationships (קשרים) ---
    # רשימת המדורים שהמשתמש שייך אליהם (דרך טבלת הקשר)
    madors = relationship("Mador", secondary="user_mador_association", back_populates="members")
    # רמות הגישה של המשתמש לכל מדור (audio/video/blast_dial/voice)
    mador_access_levels = relationship("MemberMadorAccess", back_populates="member", cascade="all, delete-orphan")




