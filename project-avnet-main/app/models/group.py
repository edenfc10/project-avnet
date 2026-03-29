# ============================================================================
# Group Model - ×ž×•×“×œ ×”×ž×“×•×¨ (×§×‘×•×¦×”)
# ============================================================================
# ×ž×“×•×¨ (Group) = ×§×‘×•×¦×”/×™×—×™×“×” ××¨×’×•× ×™×ª.
# ×›×œ ×ž×“×•×¨ ×ž×›×™×œ ×—×‘×¨×™× (Users) ×•×¤×’×™×©×•×ª (Meetings).
# ×–×”×• ××•×‘×™×™×§×˜ ×”×œ×™×‘×” ×©×ž×—×‘×¨ ×‘×™×Ÿ ×ž×©×ª×ž×©×™× ×œ×¤×’×™×©×•×ª.
#
# ×§×©×¨×™×:
#   Group <-> Users     (Many-to-Many ×“×¨×š user_group_association)
#   Group <-> Meetings  (Many-to-Many ×“×¨×š meeting_group_association)
#   Group <-> MemberGroupAccess (One-to-Many - ×¨×ž×•×ª ×’×™×©×” ×œ×›×œ ×—×‘×¨)
# ============================================================================

from enum import Enum
import uuid
from sqlalchemy import Column, Integer, String, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID


# --- Group Model - ×˜×‘×œ×ª ×”×ž×“×•×¨×™× ---
class Group(Base):
    __tablename__ = "groups"

    # ×ž×–×”×” ×™×™×—×•×“×™ ××•× ×™×‘×¨×¡×œ×™
    UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    # ×©× ×”×ž×“×•×¨ (×œ×ž×©×œ: "×ž×“×•×¨ ×ª×§×©×•×‘", "×ž×“×•×¨ ×ž×‘×¦×¢×™×")
    name = Column(String(50), nullable=False)

    # --- Relationships (×§×©×¨×™×) ---
    # ×—×‘×¨×™ ×”×ž×“×•×¨ - ×¨×©×™×ž×ª ×”×ž×©×ª×ž×©×™× ×©×©×™×™×›×™× ×œ×ž×“×•×¨
    members = relationship("User", secondary="user_group_association", back_populates="groups")
    # ×¤×’×™×©×•×ª ×”×ž×“×•×¨ - ×¨×©×™×ž×ª ×”×¤×’×™×©×•×ª ×©×©×™×™×›×•×ª ×œ×ž×“×•×¨
    meetings = relationship("Meeting", secondary="meeting_group_association", back_populates="groups")
    # ×¨×ž×•×ª ×’×™×©×” - ×ž×’×“×™×¨ ××™×–×• ×¨×ž×ª ×’×™×©×” ×œ×›×œ ×—×‘×¨ ×‘×ž×“×•×¨
    member_access_levels = relationship("MemberGroupAccess", back_populates="group", cascade="all, delete-orphan")



