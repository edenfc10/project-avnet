# ============================================================================
# Meeting Schemas (Pydantic) - ×¡×›×ž×•×ª ×§×œ×˜/×¤×œ×˜ ×œ×¤×’×™×©×•×ª
# ============================================================================
# ×§×•×‘×¥ ×–×” ×ž×’×“×™×¨ ××ª ×›×œ ×”×¡×›×ž×•×ª ×©×§×©×•×¨×•×ª ×œ×¤×’×™×©×•×ª:
#   - MeetingRole: ×¡×•×’ ×”×¤×’×™×©×” (audio/video/blast_dial)
#   - MeetingInCreate: ×§×œ×˜ ×™×¦×™×¨×”
#   - MeetingInUpdate: ×§×œ×˜ ×¢×“×›×•×Ÿ (×›×œ ×”×©×“×•×ª ××•×¤×¦×™×•× ×œ×™×•×ª)
#   - MeetingOutput: ×ª×©×•×‘×” ×œ×œ×§×•×—
# ============================================================================

from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from uuid import UUID


# --- MeetingRole Enum - ×¡×•×’ ×¤×’×™×©×” ---
# ×ž×’×“×™×¨ ××™×–×• ×¡×•×’ ×¤×’×™×©×” × ×™×ª×Ÿ ×œ×™×¦×•×¨
class MeetingRole(str, Enum):
    audio = "audio"           # ×¤×’×™×©×ª ××•×“×™×•
    video = "video"           # ×¤×’×™×©×ª ×•×™×“××•
    blast_dial = "blast_dial" # ×—×™×•×’ ×”×ž×•× ×™

    model_config = ConfigDict(use_enum_values=True)


# --- MeetingInCreate - ×§×œ×˜ ×œ×™×¦×™×¨×ª ×¤×’×™×©×” ×—×“×©×” ---
class MeetingInCreate(BaseModel):
    m_number: str          # ×ž×¡×¤×¨ ×”×¤×’×™×©×” (×œ×ž×©×œ "891234")
    accessLevel: MeetingRole  # ×¡×•×’ ×”×¤×’×™×©×”


# --- MeetingInUpdate - ×§×œ×˜ ×œ×¢×“×›×•×Ÿ ×¤×’×™×©×” ---
# ×›×œ ×”×©×“×•×ª ××•×¤×¦×™×•× ×œ×™×•×ª - ×ž××¤×©×¨ ×¢×“×›×•×Ÿ ×—×œ×§×™
class MeetingInUpdate(BaseModel):
    m_number: Optional[str] = None           # ×ž×¡×¤×¨ ×¤×’×™×©×” ×—×“×© (××•×¤×¦×™×•× ×œ×™)
    accessLevel: Optional[MeetingRole] = None  # ×¡×•×’ ×—×“×© (××•×¤×¦×™×•× ×œ×™)
    password: Optional[str] = None           # ×¡×™×¡×ž×” ×—×“×©×” (××•×¤×¦×™×•× ×œ×™)

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- MeetingOutput - ×¤×œ×˜ ×¤×’×™×©×” ×ž×œ× ---
# ×–×” ×ž×” ×©×”×œ×§×•×— ×ž×§×‘×œ ×—×–×¨×” ×›×©×©×•××œ ×¢×œ ×¤×’×™×©×”
class MeetingOutput(BaseModel):
    UUID: UUID                                                   # ×ž×–×”×” ×”×¤×’×™×©×”
    m_number: str                                                # ×ž×¡×¤×¨ ×”×¤×’×™×©×”
    accessLevel: MeetingRole                                     # ×¡×•×’ ×”×¤×’×™×©×”
    password: Optional[str] = None                               # ×¡×™×¡×ž×ª ×”×•×•×¢×™×“×” (×× ×§×™×™×ž×ª)
    groups: Optional[List[UUID]] = Field(default_factory=list)   # ×¨×©×™×ž×ª ×”×ž×“×•×¨×™× ×©×”×¤×’×™×©×” ×©×™×™×›×ª ××œ×™×”×
   

    model_config = ConfigDict(extra="forbid", from_attributes=True)


