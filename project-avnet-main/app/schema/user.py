from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from uuid import UUID

class UserRole(str, Enum):
    super_admin = "super_admin"
    admin = "admin"
    agent = "agent"


class MeetingType(str, Enum):
    audio = "audio"
    video = "video"
    blast_dial = "blast_dial"


class MeetingBase(BaseModel):
    name: str
    password: str
    type: MeetingType


class MeetingOutput(MeetingBase):
    id: str

    model_config = {"from_attributes": True}


class UserMinimalOutput(BaseModel):
    UUID: str
    username: str
    role: UserRole

    model_config = {"from_attributes": True}


class MadorBase(BaseModel):
    name: str


class MadorOutput(MadorBase):
    id: str
    creator_id: str
    creator: UserMinimalOutput
    members: List["UserOutput"] = []
    meetings: List[MeetingOutput] = []

    model_config = {"from_attributes": True}


class UserInCreate(BaseModel):
    s_id: str
    username: str
    password: str
    role: UserRole
    mador_ids: Optional[List[int]] = None

class UserInCreateNoRole(BaseModel):
    s_id: str
    username: str
    password: str
    mador_ids: Optional[List[int]] = None

class UserOutput(BaseModel):
    UUID: UUID
    s_id: str
    username: str
    role: UserRole
    madors: List["MadorOutput"] = []

    model_config = {"from_attributes": True}

class BoolOutput(BaseModel):
    success: bool

class UserInUpdate(BaseModel):
    UUID: str
    username: Optional[str] = None
    password: Optional[str] = None

# Update forward references
MadorOutput.model_rebuild()
UserOutput.model_rebuild()


class UserInLogin(BaseModel):
    s_id: str
    password: str

class UserJWTData(BaseModel):
    UUID: str
    role: UserRole
    s_id: str

class UserWithToken(BaseModel):
    token: str
    role: UserRole

class UserToken(BaseModel):
    token: str

class SessionOutput(BaseModel):
    id: int
    user_id: int
    session_token: str
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}

