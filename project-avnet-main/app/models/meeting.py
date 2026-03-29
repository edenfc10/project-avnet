# ============================================================================
# Meeting Model - ×ž×•×“×œ ×”×¤×’×™×©×”
# ============================================================================
# ×›×œ ×¤×’×™×©×” (Meeting) ×ž×™×™×¦×’×ª ×—×“×¨ ×™×©×™×‘×•×ª ×•×™×¨×˜×•××œ×™ ×¢× ×ž×¡×¤×¨ ×™×™×—×•×“×™.
# ×œ×›×œ ×¤×’×™×©×” ×™×© ×¡×•×’ (AccessLevel): audio/video/blast_dial.
# ×¤×’×™×©×•×ª ×©×™×™×›×•×ª ×œ×ž×“×•×¨×™× ×“×¨×š ×˜×‘×œ×ª ×§×©×¨ Many-to-Many.
#
# ×”×–×™×”×•×™ ×©×œ ×¡×•×’ ×¤×’×™×©×”:
#   - × ×©×ž×¨ ×‘DB ×‘×©×“×” accessLevel
#   - ×‘×¦×“ ×”×œ×§×•×— ×™×© ×’× fallback ×œ×¤×™ ×”×§×™×“×•×ž×ª ×©×œ ×ž×¡×¤×¨ ×”×¤×’×™×©×”:
#     89xxx = audio, 77xxx = video, 55xxx = blast_dial
# ============================================================================

from enum import Enum
import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, Enum as SqlEnum, Table
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID


# --- AccessLevel Enum - ×¡×•×’×™ ×¤×’×™×©×•×ª ---
# ×ž×’×“×™×¨ ××ª ×©×œ×•×©×ª ×¡×•×’×™ ×”×¤×’×™×©×•×ª ×”××¤×©×¨×™×™× ×‘×ž×¢×¨×›×ª
class AccessLevel(str, Enum):
    audio = "audio"           # ×©×™×—×ª ××•×“×™×• ×‘×œ×‘×“
    video = "video"           # ×©×™×—×ª ×•×™×“××•
    blast_dial = "blast_dial" # ×—×™×•×’ ×”×ž×•× ×™ - ×©×œ×™×—×ª ×”×•×“×¢×” ×œ×§×‘×•×¦×” ×’×“×•×œ×”


# --- Association Table: meeting_group_association ---
# ×˜×‘×œ×ª ×§×©×¨ Many-to-Many ×‘×™×Ÿ ×¤×’×™×©×•×ª ×œ×ž×“×•×¨×™×.
# ×¤×’×™×©×” ××—×ª ×™×›×•×œ×” ×œ×”×™×•×ª ×©×™×™×›×ª ×œ×ž×¡×¤×¨ ×ž×“×•×¨×™×, ×•×ž×“×•×¨ ×™×›×•×œ ×œ×”×›×™×œ ×ž×¡×¤×¨ ×¤×’×™×©×•×ª.
meeting_group_association = Table(
    "meeting_group_association",
    Base.metadata,
    Column("meeting_id", PostgresUUID(as_uuid=True), ForeignKey("meetings.UUID", ondelete="CASCADE"), primary_key=True),
    Column("group_id", PostgresUUID(as_uuid=True), ForeignKey("groups.UUID", ondelete="CASCADE"), primary_key=True)
)


# --- Meeting Model - ×˜×‘×œ×ª ×”×¤×’×™×©×•×ª ---
class Meeting(Base):
    __tablename__ = "meetings"

    # ×ž×–×”×” ×™×™×—×•×“×™ ××•× ×™×‘×¨×¡×œ×™
    UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    # ×ž×¡×¤×¨ ×”×¤×’×™×©×” (×™×™×—×•×“×™) - ×œ×ž×©×œ "891234", "771110", "551900"
    m_number = Column(String(15), unique=True, nullable=False, index=True)
    # ×¡×•×’ ×”×¤×’×™×©×” - audio / video / blast_dial
    accessLevel = Column(SqlEnum(AccessLevel), nullable=False)
    # ×¡×™×¡×ž×ª ×”×•×•×¢×™×“×” (××•×¤×¦×™×•× ×œ×™) - × ×©×ž×¨×ª ×‘DB ×œ×¦×¤×™×™×” ×ž×©×•×ª×¤×ª
    password = Column(String(120), nullable=True)

    # --- Relationships (×§×©×¨×™×) ---
    # ×¨×©×™×ž×ª ×”×ž×“×•×¨×™× ×©×”×¤×’×™×©×” ×©×™×™×›×ª ××œ×™×”×
    groups = relationship("Group", secondary="meeting_group_association", back_populates="meetings")


