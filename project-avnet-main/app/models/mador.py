# ============================================================================
# Mador Model - מודל המדור (קבוצה)
# ============================================================================
# מדור (Mador) = קבוצה/יחידה ארגונית.
# כל מדור מכיל חברים (Users) ופגישות (Meetings).
# זהו אובייקט הליבה שמחבר בין משתמשים לפגישות.
#
# קשרים:
#   Mador <-> Users     (Many-to-Many דרך user_mador_association)
#   Mador <-> Meetings  (Many-to-Many דרך meeting_mador_association)
#   Mador <-> MemberMadorAccess (One-to-Many - רמות גישה לכל חבר)
# ============================================================================

from enum import Enum
import uuid
from sqlalchemy import Column, Integer, String, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID


# --- Mador Model - טבלת המדורים ---
class Mador(Base):
    __tablename__ = "madors"

    # מזהה ייחודי אוניברסלי
    UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    # שם המדור (למשל: "מדור תקשוב", "מדור מבצעים")
    name = Column(String(50), nullable=False)

    # --- Relationships (קשרים) ---
    # חברי המדור - רשימת המשתמשים ששייכים למדור
    members = relationship("User", secondary="user_mador_association", back_populates="madors")
    # פגישות המדור - רשימת הפגישות ששייכות למדור
    meetings = relationship("Meeting", secondary="meeting_mador_association", back_populates="madors")
    # רמות גישה - מגדיר איזו רמת גישה לכל חבר במדור
    member_access_levels = relationship("MemberMadorAccess", back_populates="mador", cascade="all, delete-orphan")


