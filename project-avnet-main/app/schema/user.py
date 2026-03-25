# ============================================================================
# User Schemas (Pydantic) - סכמות קלט/פלט למשתמשים ומדורים
# ============================================================================
# קובץ זה מגדיר את כל המודלים (DTOs) של Pydantic לולידציה וסריאליזציה.
# הם משמשים ל:
#   1. ולידציה של קלט מהלקוח (request body)
#   2. פורמט התשובה ללקוח (response_model)
#   3. אובייקטי העברה פנימיים בין השכבות
#
# המנהג ConfigDict:
#   - extra="forbid" -> חוסם שדות נוספים בקלט (מניעת הזרקה)
#   - from_attributes=True -> מאפשר המרה של ORM objects ל-Pydantic
# ============================================================================

from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from uuid import UUID
from app.models.member_mador_access import MemberMadorAccessLevel


# --- UserRole Enum (שכבת Schema) ---
# שכפול של ה-Enum מהמודל לשימוש ב-Pydantic schemas
class UserRole(str, Enum):
    super_admin = "super_admin"
    admin = "admin"
    agent = "agent"

    model_config = ConfigDict(use_enum_values=True)  # שומר את הערך הטקסטואלי ולא את האובייקט


# --- MadorInCreate - קלט ליצירת מדור ---
class MadorInCreate(BaseModel):
    name: str  # שם המדור החדש
    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- MadorInUpdate - קלט לעדכון מדור ---
class MadorInUpdate(BaseModel):
    name: Optional[str] = None  # אופציונלי - אפשר לעדכן רק את מה שרלוונטי

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- MemberAccessOutput - פלט רמת גישה של חבר ---
# מייצג את הרמה של כל משתמש בתוך מדור מסוים
class MemberAccessOutput(BaseModel):
    user_id: UUID                          # UUID של המשתמש
    access_level: MemberMadorAccessLevel   # רמת הגישה שלו במדור

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- MadorOutput - פלט של מדור מלא ---
# זה מה שחוזר ללקוח כששואלים מידע על מדור
class MadorOutput(BaseModel):
    UUID: UUID                                                                     # מזהה המדור
    name: str                                                                      # שם המדור
    members: Optional[List[UUID]] = Field(default_factory=list)                    # רשימת UUIDs של החברים
    meetings: Optional[List[UUID]] = Field(default_factory=list)                   # רשימת UUIDs של הפגישות
    member_access_levels: Optional[List[MemberAccessOutput]] = Field(default_factory=list)  # רמות גישה לכל חבר


    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- UserInCreate - קלט ליצירת משתמש (עם תפקיד) ---
class UserInCreate(BaseModel):
    s_id: str                                              # מזהה משתמש (כמו מספר עובד)
    username: str                                          # שם תצוגה
    password: str                                          # סיסמה (תוצפן לפני שמירה)
    role: UserRole                                         # תפקיד (super_admin/admin/agent)
    mador_ids: Optional[List[UUID]] = Field(default_factory=list)  # מדורים לשיוך (אופציונלי)

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- UserInCreateNoRole - קלט ליצירת משתמש (בלי תפקיד) ---
# משמש כשה-role נקבע אוטומטית לפי הנתיב: create-agent -> role=agent, create-admin -> role=admin
class UserInCreateNoRole(BaseModel):
    s_id: str
    username: str
    password: str
    mador_ids: Optional[List[UUID]] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- UserOutput - פלט של משתמש ---
# זה מה שחוזר ללקוח - לעולם לא כולל סיסמה!
class UserOutput(BaseModel):
    UUID: UUID
    s_id: str
    username: str
    role: UserRole
    madors: Optional[List[UUID]] = Field(default_factory=list)  # רשימת UUIDs של המדורים

    # ולידטור מותאם אישית - ממיר אובייקטי Mador ל-UUID בלבד
    # נדרש כי SQLAlchemy מחזיר אובייקטים מלאים ולא UUIDs
    @field_validator('madors', mode='before')
    @classmethod
    def extract_mador_uuids(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return [getattr(mador, 'UUID', mador) for mador in v]
        return v

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- BoolOutput - תשובה בווליאנית פשוטה ---
# משמש לפעולות כמו מחיקה - הצליח/נכשל
class BoolOutput(BaseModel):
    success: bool
    model_config = ConfigDict(extra="forbid", from_attributes=True)


# עדכון הפניות קדימה (forward references) - נדרש ל-Pydantic v2
UserOutput.model_rebuild()


# --- UserInLogin - קלט להתחברות ---
class UserInLogin(BaseModel):
    s_id: str       # מזהה משתמש
    password: str   # סיסמה (תושווה מול hash בDB)
    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- UserJWTData - מידע שנשמר בתוך הטוקן JWT ---
# המידע הזה מוצפן בתוך ה-payload של הטוקן
class UserJWTData(BaseModel):
    UUID: str       # UUID כטקסט
    role: UserRole  # תפקיד
    s_id: str       # מזהה משתמש

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- UserToken - תשובת התחברות ---
# חוזר ללקוח אחרי login מוצלח
class UserToken(BaseModel):
    token: str      # הטוקן JWT
    role: UserRole  # התפקיד של המשתמש

    model_config = ConfigDict(extra="forbid", from_attributes=True)


# --- UserWithToken - משתמש מלא + טוקן ---
# מרחיב את UserOutput ומוסיף טוקן
class UserWithToken(UserOutput):
    token: str

    model_config = ConfigDict(extra="forbid", from_attributes=True)
