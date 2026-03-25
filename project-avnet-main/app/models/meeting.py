# ============================================================================
# Meeting Model - מודל הפגישה
# ============================================================================
# כל פגישה (Meeting) מייצגת חדר ישיבות וירטואלי עם מספר ייחודי.
# לכל פגישה יש סוג (AccessLevel): audio/video/blast_dial.
# פגישות שייכות למדורים דרך טבלת קשר Many-to-Many.
#
# הזיהוי של סוג פגישה:
#   - נשמר בDB בשדה accessLevel
#   - בצד הלקוח יש גם fallback לפי הקידומת של מספר הפגישה:
#     89xxx = audio, 77xxx = video, 55xxx = blast_dial
# ============================================================================

from enum import Enum
import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, Enum as SqlEnum, Table
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID


# --- AccessLevel Enum - סוגי פגישות ---
# מגדיר את שלושת סוגי הפגישות האפשריים במערכת
class AccessLevel(str, Enum):
    audio = "audio"           # שיחת אודיו בלבד
    video = "video"           # שיחת וידאו
    blast_dial = "blast_dial" # חיוג המוני - שליחת הודעה לקבוצה גדולה


# --- Association Table: meeting_mador_association ---
# טבלת קשר Many-to-Many בין פגישות למדורים.
# פגישה אחת יכולה להיות שייכת למספר מדורים, ומדור יכול להכיל מספר פגישות.
meeting_mador_association = Table(
    "meeting_mador_association",
    Base.metadata,
    Column("meeting_id", PostgresUUID(as_uuid=True), ForeignKey("meetings.UUID", ondelete="CASCADE"), primary_key=True),
    Column("mador_id", PostgresUUID(as_uuid=True), ForeignKey("madors.UUID", ondelete="CASCADE"), primary_key=True)
)


# --- Meeting Model - טבלת הפגישות ---
class Meeting(Base):
    __tablename__ = "meetings"

    # מזהה ייחודי אוניברסלי
    UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    # מספר הפגישה (ייחודי) - למשל "891234", "771110", "551900"
    m_number = Column(String(15), unique=True, nullable=False, index=True)
    # סוג הפגישה - audio / video / blast_dial
    accessLevel = Column(SqlEnum(AccessLevel), nullable=False)

    # --- Relationships (קשרים) ---
    # רשימת המדורים שהפגישה שייכת אליהם
    madors = relationship("Mador", secondary="meeting_mador_association", back_populates="meetings")

