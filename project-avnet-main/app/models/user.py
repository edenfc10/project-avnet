# ============================================================================
# User Model - ×ž×•×“×œ ×”×ž×©×ª×ž×©
# ============================================================================
# ×§×•×‘×¥ ×–×” ×ž×’×“×™×¨ ××ª ×ž×•×“×œ ×”×ž×©×ª×ž×© (User) ×‘×ž×¡×“ ×”× ×ª×•× ×™×.
# ×›×•×œ×œ: ×ª×¤×§×™×“×™× (roles), ×˜×‘×œ×ª ×§×©×¨ ×‘×™×Ÿ ×ž×©×ª×ž×©×™× ×œ×ž×“×•×¨×™×,
# ×•××ª ×›×œ ×”×©×“×•×ª ×©×œ ×”×ž×©×ª×ž×© ×‘DB.
#
# Permission Hierarchy (×”×™×¨×¨×›×™×™×ª ×”×¨×©××•×ª):
#   super_admin > admin > agent
#   - super_admin: ×’×™×©×” ×ž×œ××” - × ×™×”×•×œ ×›×œ ×”×ž×©×ª×ž×©×™×, ×ž×“×•×¨×™× ×•×¤×’×™×©×•×ª
#   - admin: ×™×›×•×œ ×œ×™×¦×•×¨ agents, ×œ× ×”×œ ×ž×“×•×¨×™× ×•×¤×’×™×©×•×ª
#   - agent: ×¦×¤×™×™×” ×‘×œ×‘×“ - ×¨×•××” ×¨×§ ××ª ×”×¤×’×™×©×•×ª ×œ×¤×™ ×”×ž×“×•×¨×™× ×•×”×’×™×©×” ×©×œ×•
# ============================================================================

from enum import Enum
import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, Enum as SqlEnum, Table
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID


# --- UserRole Enum - ×ª×¤×§×™×“×™ ×”×ž×©×ª×ž×© ---
# ×›×œ ×ž×©×ª×ž×© ×—×™×™×‘ ×œ×”×™×•×ª ××—×“ ×ž-3 ×”×ª×¤×§×™×“×™× ×”××œ×”.
# ×”Enum ×™×•×¨×© ×ž-str ×›×“×™ ×©×”×¢×¨×š ×™×™×©×ž×¨ ×›×˜×§×¡×˜ ×‘DB ×•×™×”×™×” ×§×œ ×œ×”×©×•×•×ª.
class UserRole(str, Enum):
    super_admin = "super_admin"  # ×ž× ×”×œ ×¢×œ - ×©×œ×™×˜×” ×ž×œ××” ×¢×œ ×”×ž×¢×¨×›×ª
    admin = "admin"              # ×ž× ×”×œ - ×™×›×•×œ ×œ× ×”×œ agents ×•×¤×’×™×©×•×ª
    agent = "agent"              # ×¡×•×›×Ÿ - ×¦×¤×™×™×” ×‘×œ×‘×“ ×œ×¤×™ ×”×¨×©××•×ª
    viewer = "viewer"            # ×¦×•×¤×” - ×¦×¤×™×™×” ×‘×¡×™×¡×™×ª ×œ×¤×™ ×”×¨×©××•×ª ×ž×“×•×¨


# --- Association Table: user_group_association ---
# ×˜×‘×œ×ª ×§×©×¨ Many-to-Many ×‘×™×Ÿ ×ž×©×ª×ž×©×™× (users) ×œ×ž×“×•×¨×™× (groups).
# ×›×œ ×©×•×¨×” ×ž×™×™×¦×’×ª ×©×™×•×š ×©×œ ×ž×©×ª×ž×© ×œ×ž×“×•×¨ ×ž×¡×•×™×.
# ondelete="CASCADE" - ×× ×ž×•×—×§×™× ×ž×©×ª×ž×© ××• ×ž×“×•×¨, ×”×©×™×•×š × ×ž×—×§ ××•×˜×•×ž×˜×™×ª.
user_group_association = Table(
    "user_group_association",
    Base.metadata,
    Column("user_id", PostgresUUID(as_uuid=True), ForeignKey("users.UUID", ondelete="CASCADE"), primary_key=True),
    Column("group_id", PostgresUUID(as_uuid=True), ForeignKey("groups.UUID", ondelete="CASCADE"), primary_key=True)
)


# --- User Model - ×˜×‘×œ×ª ×”×ž×©×ª×ž×©×™× ---
class User(Base):
    __tablename__ = "users"

    # ×ž×–×”×” ×™×™×—×•×“×™ ××•× ×™×‘×¨×¡×œ×™ - × ×•×¦×¨ ××•×˜×•×ž×˜×™×ª
    UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    # ×ž×–×”×” ×ž×©×ª×ž×© (×›×ž×• ×ž×¡×¤×¨ ×¢×•×‘×“) - ×—×™×™×‘ ×œ×”×™×•×ª ×™×™×—×•×“×™
    s_id = Column(String(50), unique=True, nullable=False, index=True)
    # ×©× ×”×ž×©×ª×ž×© ×œ×ª×¦×•×’×”
    username = Column(String(50), nullable=False)
    # ×¡×™×¡×ž×” ×ž×•×¦×¤× ×ª (Argon2 hash) - ×œ×¢×•×œ× ×œ× × ×©×ž×¨×ª ×›×˜×§×¡×˜ ×¨×’×™×œ
    password = Column(String(250), nullable=False)
    # ×ª×¤×§×™×“ ×”×ž×©×ª×ž×© - ×‘×¨×™×¨×ª ×ž×—×“×œ: agent
    role = Column(SqlEnum(UserRole), nullable=False, default=UserRole.agent)

    # --- Relationships (×§×©×¨×™×) ---
    # ×¨×©×™×ž×ª ×”×ž×“×•×¨×™× ×©×”×ž×©×ª×ž×© ×©×™×™×š ××œ×™×”× (×“×¨×š ×˜×‘×œ×ª ×”×§×©×¨)
    groups = relationship("Group", secondary="user_group_association", back_populates="members")
    # ×¨×ž×•×ª ×”×’×™×©×” ×©×œ ×”×ž×©×ª×ž×© ×œ×›×œ ×ž×“×•×¨ (audio/video/blast_dial/voice)
    group_access_levels = relationship("MemberGroupAccess", back_populates="member", cascade="all, delete-orphan")





