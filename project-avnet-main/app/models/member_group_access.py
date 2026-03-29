# ============================================================================
# MemberGroupAccess Model - ×¨×ž×ª ×’×™×©×” ×©×œ ×—×‘×¨ ×œ×ž×“×•×¨
# ============================================================================
# ×˜×‘×œ×” ×–×• ×ž×’×“×™×¨×” ××™×–×• ×¨×ž×ª ×’×™×©×” ×™×© ×œ×›×œ ×ž×©×ª×ž×© ×‘×›×œ ×ž×“×•×¨.
# ×–×” ×ž××¤×©×¨ ×©×œ×™×˜×” ×¤×¨×˜× ×™×ª: ×ž×©×ª×ž×© ×' ×™×›×•×œ ×œ×¨××•×ª ×¨×§ ×¤×’×™×©×•×ª ××•×“×™×• ×‘×ž×“×•×¨ ×ž×¡×•×™×,
# ××‘×œ ×ž×©×ª×ž×© ×‘' ×™×›×•×œ ×œ×¨××•×ª ×’× ×•×™×“××• ×‘××•×ª×• ×ž×“×•×¨.
#
# Composite Primary Key (×ž×¤×ª×— ×ž×•×¨×›×‘):
#   (member_uuid, group_uuid, access_level)
#   -> ×‘×¤×•×¢×œ × ×©×ž×¨×ª ×¨×©×•×ž×” ××—×ª ×œ×›×œ ×©×™×•×š (×ž×—×œ×™×¤×™× ××ª ×”×§×•×“× ×‘×›×œ ×¢×“×›×•×Ÿ)
#
# ×”×–×¨×™×ž×”:
#   1. Admin ×ž×•×¡×™×£ agent ×œ×ž×“×•×¨ ×¢× ×¨×ž×ª ×’×™×©×” (audio/video/blast_dial/voice)
#   2. ×”×¨×ž×” × ×©×ž×¨×ª ×‘×˜×‘×œ×” ×”×–×•
#   3. ×›×©×”agent × ×›× ×¡ ×œ×“×£ ×”×¤×’×™×©×•×ª, ×”frontend ×‘×•×“×§ ××ª ×”×¨×ž×” ×•×ž×¦×™×’ ×‘×”×ª××
# ============================================================================

from enum import Enum

from sqlalchemy import Column, Enum as SqlEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


# --- MemberGroupAccessLevel Enum - ×¨×ž×•×ª ×’×™×©×” ××¤×©×¨×™×•×ª ---
# voice = ×’×™×©×” ×œ×§×•×œ×™×ª ×‘×œ×‘×“
# audio = ×’×™×©×” ×œ×¤×’×™×©×•×ª ××•×“×™×•
# video = ×’×™×©×” ×œ×¤×’×™×©×•×ª ×•×™×“××•
# blast_dial = ×’×™×©×” ×œ×—×™×•×’ ×”×ž×•× ×™
class MemberGroupAccessLevel(str, Enum):
    voice = "voice"
    audio = "audio"
    video = "video"
    blast_dial = "blast_dial"


# --- MemberGroupAccess Model - ×˜×‘×œ×ª ×”×¨×©××•×ª ×—×‘×¨-×ž×“×•×¨ ---
class MemberGroupAccess(Base):
    __tablename__ = "member_group_access"

    # UUID ×©×œ ×”×ž×©×ª×ž×© (FK ×œ×˜×‘×œ×ª users)
    member_uuid = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("users.UUID", ondelete="CASCADE"),
        primary_key=True,
    )
    # UUID ×©×œ ×”×ž×“×•×¨ (FK ×œ×˜×‘×œ×ª groups)
    group_uuid = Column(
        PostgresUUID(as_uuid=True),
        ForeignKey("groups.UUID", ondelete="CASCADE"),
        primary_key=True,
    )
    # ×¨×ž×ª ×”×’×™×©×” ×©×ž×•×’×“×¨×ª ×œ×ž×©×ª×ž×© ×”×–×” ×‘×ž×“×•×¨ ×”×–×”
    access_level = Column(SqlEnum(MemberGroupAccessLevel), primary_key=True)

    # --- Relationships (×§×©×¨×™×) ---
    member = relationship("User", back_populates="group_access_levels")  # ×—×–×¨×” ×œ×ž×©×ª×ž×©
    group = relationship("Group", back_populates="member_access_levels")  # ×—×–×¨×” ×œ×ž×“×•×¨

