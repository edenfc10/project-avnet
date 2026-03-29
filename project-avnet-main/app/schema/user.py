# ============================================================================
# User Schemas (Pydantic) - ×¡×›×ž×•×ª ×§×œ×˜/×¤×œ×˜ ×œ×ž×©×ª×ž×©×™× ×•×ž×“×•×¨×™×
# ============================================================================
# ×§×•×‘×¥ ×–×” ×ž×’×“×™×¨ ××ª ×›×œ ×”×ž×•×“×œ×™× (DTOs) ×©×œ Pydantic ×œ×•×œ×™×“×¦×™×” ×•×¡×¨×™××œ×™×–×¦×™×”.
# ×”× ×ž×©×ž×©×™× ×œ:
#   1. ×•×œ×™×“×¦×™×” ×©×œ ×§×œ×˜ ×ž×”×œ×§×•×— (request body)
#   2. ×¤×•×¨×ž×˜ ×”×ª×©×•×‘×” ×œ×œ×§×•×— (response_model)
#   3. ××•×‘×™×™×§×˜×™ ×”×¢×‘×¨×” ×¤× ×™×ž×™×™× ×‘×™×Ÿ ×”×©×›×‘×•×ª
#
# ×”×ž× ×”×’ ConfigDict:
#   - extra="forbid" -> ×—×•×¡× ×©×“×•×ª × ×•×¡×¤×™× ×‘×§×œ×˜ (×ž× ×™×¢×ª ×”×–×¨×§×”)
#   - from_attributes=True -> ×ž××¤×©×¨ ×”×ž×¨×” ×©×œ ORM objects ×œ-Pydantic
# ============================================================================

from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from uuid import UUID
from app.models.member_group_access import MemberGroupAccessLevel


# --- UserRole Enum (×©×›×‘×ª Schema) ---
# ×©×›×¤×•×œ ×©×œ ×”-Enum ×ž×”×ž×•×“×œ ×œ×©×™×ž×•×© ×‘-Pydantic schemas
class UserRole(str, Enum):
    super_admin = "super_admin"
    admin = "admin"
    agent = "agent"
    viewer = "viewer"

    model_config = ConfigDict(use_enum_values=True)  # ×©×•×ž×¨ ××ª ×”×¢×¨×š ×”×˜×§×¡×˜×•××œ×™ ×•×œ× ××ª ×”××•×‘×™×™×§×˜


# --- GroupInCreate - ×§×œ×˜ ×œ×™×¦×™×¨×ª ×ž×“×•×¨ ---
class GroupInCreate(BaseModel):
    name: str  # ×©× ×”×ž×“×•×¨ ×”×—×“×©
    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- GroupInUpdate - ×§×œ×˜ ×œ×¢×“×›×•×Ÿ ×ž×“×•×¨ ---
class GroupInUpdate(BaseModel):
    name: Optional[str] = None  # ××•×¤×¦×™×•× ×œ×™ - ××¤×©×¨ ×œ×¢×“×›×Ÿ ×¨×§ ××ª ×ž×” ×©×¨×œ×•×•× ×˜×™

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- MemberAccessOutput - ×¤×œ×˜ ×¨×ž×ª ×’×™×©×” ×©×œ ×—×‘×¨ ---
# ×ž×™×™×¦×’ ××ª ×”×¨×ž×” ×©×œ ×›×œ ×ž×©×ª×ž×© ×‘×ª×•×š ×ž×“×•×¨ ×ž×¡×•×™×
class MemberAccessOutput(BaseModel):
    user_id: UUID                          # UUID ×©×œ ×”×ž×©×ª×ž×©
    access_level: MemberGroupAccessLevel   # ×¨×ž×ª ×”×’×™×©×” ×©×œ×• ×‘×ž×“×•×¨

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- GroupOutput - ×¤×œ×˜ ×©×œ ×ž×“×•×¨ ×ž×œ× ---
# ×–×” ×ž×” ×©×—×•×–×¨ ×œ×œ×§×•×— ×›×©×©×•××œ×™× ×ž×™×“×¢ ×¢×œ ×ž×“×•×¨
class GroupOutput(BaseModel):
    UUID: UUID                                                                     # ×ž×–×”×” ×”×ž×“×•×¨
    name: str                                                                      # ×©× ×”×ž×“×•×¨
    members: Optional[List[UUID]] = Field(default_factory=list)                    # ×¨×©×™×ž×ª UUIDs ×©×œ ×”×—×‘×¨×™×
    meetings: Optional[List[UUID]] = Field(default_factory=list)                   # ×¨×©×™×ž×ª UUIDs ×©×œ ×”×¤×’×™×©×•×ª
    member_access_levels: Optional[List[MemberAccessOutput]] = Field(default_factory=list)  # ×¨×ž×•×ª ×’×™×©×” ×œ×›×œ ×—×‘×¨


    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- UserInCreate - ×§×œ×˜ ×œ×™×¦×™×¨×ª ×ž×©×ª×ž×© (×¢× ×ª×¤×§×™×“) ---
class UserInCreate(BaseModel):
    s_id: str                                              # ×ž×–×”×” ×ž×©×ª×ž×© (×›×ž×• ×ž×¡×¤×¨ ×¢×•×‘×“)
    username: str                                          # ×©× ×ª×¦×•×’×”
    password: str                                          # ×¡×™×¡×ž×” (×ª×•×¦×¤×Ÿ ×œ×¤× ×™ ×©×ž×™×¨×”)
    role: UserRole                                         # ×ª×¤×§×™×“ (super_admin/admin/agent)
    group_ids: Optional[List[UUID]] = Field(default_factory=list)  # ×ž×“×•×¨×™× ×œ×©×™×•×š (××•×¤×¦×™×•× ×œ×™)

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- UserInCreateNoRole - ×§×œ×˜ ×œ×™×¦×™×¨×ª ×ž×©×ª×ž×© (×‘×œ×™ ×ª×¤×§×™×“) ---
# ×ž×©×ž×© ×›×©×”-role × ×§×‘×¢ ××•×˜×•×ž×˜×™×ª ×œ×¤×™ ×”× ×ª×™×‘: create-agent -> role=agent, create-admin -> role=admin
class UserInCreateNoRole(BaseModel):
    s_id: str
    username: str
    password: str
    group_ids: Optional[List[UUID]] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- UserOutput - ×¤×œ×˜ ×©×œ ×ž×©×ª×ž×© ---
# ×–×” ×ž×” ×©×—×•×–×¨ ×œ×œ×§×•×— - ×œ×¢×•×œ× ×œ× ×›×•×œ×œ ×¡×™×¡×ž×”!
class UserOutput(BaseModel):
    UUID: UUID
    s_id: str
    username: str
    role: UserRole
    groups: Optional[List[UUID]] = Field(default_factory=list)  # ×¨×©×™×ž×ª UUIDs ×©×œ ×”×ž×“×•×¨×™×

    # ×•×œ×™×“×˜×•×¨ ×ž×•×ª×× ××™×©×™×ª - ×ž×ž×™×¨ ××•×‘×™×™×§×˜×™ Group ×œ-UUID ×‘×œ×‘×“
    # × ×“×¨×© ×›×™ SQLAlchemy ×ž×—×–×™×¨ ××•×‘×™×™×§×˜×™× ×ž×œ××™× ×•×œ× UUIDs
    @field_validator('groups', mode='before')
    @classmethod
    def extract_group_uuids(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return [getattr(group, 'UUID', group) for group in v]
        return v

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- BoolOutput - ×ª×©×•×‘×” ×‘×•×•×œ×™×× ×™×ª ×¤×©×•×˜×” ---
# ×ž×©×ž×© ×œ×¤×¢×•×œ×•×ª ×›×ž×• ×ž×—×™×§×” - ×”×¦×œ×™×—/× ×›×©×œ
class BoolOutput(BaseModel):
    success: bool
    model_config = ConfigDict(extra="forbid", from_attributes=True)


# ×¢×“×›×•×Ÿ ×”×¤× ×™×•×ª ×§×“×™×ž×” (forward references) - × ×“×¨×© ×œ-Pydantic v2
UserOutput.model_rebuild()


# --- UserInLogin - ×§×œ×˜ ×œ×”×ª×—×‘×¨×•×ª ---
class UserInLogin(BaseModel):
    s_id: str       # ×ž×–×”×” ×ž×©×ª×ž×©
    password: str   # ×¡×™×¡×ž×” (×ª×•×©×•×•×” ×ž×•×œ hash ×‘DB)
    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- UserJWTData - ×ž×™×“×¢ ×©× ×©×ž×¨ ×‘×ª×•×š ×”×˜×•×§×Ÿ JWT ---
# ×”×ž×™×“×¢ ×”×–×” ×ž×•×¦×¤×Ÿ ×‘×ª×•×š ×”-payload ×©×œ ×”×˜×•×§×Ÿ
class UserJWTData(BaseModel):
    UUID: str       # UUID ×›×˜×§×¡×˜
    role: UserRole  # ×ª×¤×§×™×“
    s_id: str       # ×ž×–×”×” ×ž×©×ª×ž×©

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- UserToken - ×ª×©×•×‘×ª ×”×ª×—×‘×¨×•×ª ---
# ×—×•×–×¨ ×œ×œ×§×•×— ××—×¨×™ login ×ž×•×¦×œ×—
class UserToken(BaseModel):
    token: str      # ×”×˜×•×§×Ÿ JWT
    role: UserRole  # ×”×ª×¤×§×™×“ ×©×œ ×”×ž×©×ª×ž×©

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- UserWithToken - ×ž×©×ª×ž×© ×ž×œ× + ×˜×•×§×Ÿ ---
# ×ž×¨×—×™×‘ ××ª UserOutput ×•×ž×•×¡×™×£ ×˜×•×§×Ÿ
class UserWithToken(UserOutput):
    token: str

    model_config = ConfigDict(extra="forbid", from_attributes=True)

