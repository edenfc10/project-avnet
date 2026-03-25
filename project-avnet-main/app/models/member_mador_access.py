# ============================================================================
# MemberMadorAccess Model - רמת גישה של חבר למדור
# ============================================================================
# טבלה זו מגדירה איזו רמת גישה יש לכל משתמש בכל מדור.
# זה מאפשר שליטה פרטנית: משתמש א' יכול לראות רק פגישות אודיו במדור מסוים,
# אבל משתמש ב' יכול לראות גם וידאו באותו מדור.
#
# Composite Primary Key (מפתח מורכב):
#   (member_uuid, mador_uuid, access_level)
#   -> בפועל נשמרת רשומה אחת לכל שיוך (מחליפים את הקודם בכל עדכון)
#
# הזרימה:
#   1. Admin מוסיף agent למדור עם רמת גישה (audio/video/blast_dial/voice)
#   2. הרמה נשמרת בטבלה הזו
#   3. כשהagent נכנס לדף הפגישות, הfrontend בודק את הרמה ומציג בהתאם
# ============================================================================

from enum import Enum

from sqlalchemy import Column, Enum as SqlEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


# --- MemberMadorAccessLevel Enum - רמות גישה אפשריות ---
# voice = גישה לקולית בלבד
# audio = גישה לפגישות אודיו
# video = גישה לפגישות וידאו
# blast_dial = גישה לחיוג המוני
class MemberMadorAccessLevel(str, Enum):
    voice = "voice"
    audio = "audio"
    video = "video"
    blast_dial = "blast_dial"


# --- MemberMadorAccess Model - טבלת הרשאות חבר-מדור ---
class MemberMadorAccess(Base):
    __tablename__ = "member_mador_access"

    # UUID של המשתמש (FK לטבלת users)
    member_uuid = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.UUID", ondelete="CASCADE"),
        primary_key=True,
    )
    # UUID של המדור (FK לטבלת madors)
    mador_uuid = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("madors.UUID", ondelete="CASCADE"),
        primary_key=True,
    )
    # רמת הגישה שמוגדרת למשתמש הזה במדור הזה
    access_level = Column(SqlEnum(MemberMadorAccessLevel), primary_key=True)

    # --- Relationships (קשרים) ---
    member = relationship("User", back_populates="mador_access_levels")  # חזרה למשתמש
    mador = relationship("Mador", back_populates="member_access_levels")  # חזרה למדור
