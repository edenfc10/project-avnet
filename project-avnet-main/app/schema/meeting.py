# ============================================================================
# Meeting Schemas (Pydantic) - סכמות קלט/פלט לפגישות
# ============================================================================
# קובץ זה מגדיר את כל הסכמות שקשורות לפגישות:
#   - MeetingRole: סוג הפגישה (audio/video/blast_dial)
#   - MeetingInCreate: קלט יצירה
#   - MeetingInUpdate: קלט עדכון (כל השדות אופציונליות)
#   - MeetingOutput: תשובה ללקוח
# ============================================================================

from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from uuid import UUID


# --- MeetingRole Enum - סוג פגישה ---
# מגדיר איזו סוג פגישה ניתן ליצור
class MeetingRole(str, Enum):
    audio = "audio"           # פגישת אודיו
    video = "video"           # פגישת וידאו
    blast_dial = "blast_dial" # חיוג המוני

    model_config = ConfigDict(use_enum_values=True)


# --- MeetingInCreate - קלט ליצירת פגישה חדשה ---
class MeetingInCreate(BaseModel):
    m_number: str          # מספר הפגישה (למשל "891234")
    accessLevel: MeetingRole  # סוג הפגישה


# --- MeetingInUpdate - קלט לעדכון פגישה ---
# כל השדות אופציונליות - מאפשר עדכון חלקי
class MeetingInUpdate(BaseModel):
    m_number: Optional[str] = None           # מספר פגישה חדש (אופציונלי)
    accessLevel: Optional[MeetingRole] = None  # סוג חדש (אופציונלי)
    password: Optional[str] = None           # סיסמה חדשה (אופציונלי)

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- MeetingOutput - פלט פגישה מלא ---
# זה מה שהלקוח מקבל חזרה כששואל על פגישה
class MeetingOutput(BaseModel):
    UUID: UUID                                                   # מזהה הפגישה
    m_number: str                                                # מספר הפגישה
    accessLevel: MeetingRole                                     # סוג הפגישה
    password: Optional[str] = None                               # סיסמת הוועידה (אם קיימת)
    madors: Optional[List[UUID]] = Field(default_factory=list)   # רשימת המדורים שהפגישה שייכת אליהם
   

    model_config = ConfigDict(extra="forbid", from_attributes=True)

