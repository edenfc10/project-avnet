# ============================================================================
# Mador Router - נתיבי API לניהול מדורים
# ============================================================================
# נתיבים:
#   POST   /madors/create                         - יצירת מדור חדש
#   GET    /madors/all                             - שליפת כל המדורים
#   GET    /madors/{uuid}                          - שליפת מדור בודד
#   DELETE /madors/{uuid}                          - מחיקת מדור
#   PUT    /madors/{uuid}                          - עדכון מדור
#   POST   /madors/{uuid}/add-member/{s_id}        - הוספת חבר + רמת גישה
#   POST   /madors/{uuid}/remove-member/{s_id}     - הסרת חבר
#   POST   /madors/{uuid}/add-meeting/{meeting_uuid} - שיוך פגישה למדור
#
# הרשאות: admin + super_admin בלבד
# ============================================================================

from fastapi import APIRouter, Depends
from app.schema.user import BoolOutput, MadorInCreate, MadorInUpdate, MadorInUpdate, MadorOutput, UserInCreateNoRole, UserOutput
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.security.TokenValidator import TokenValidator
from app.service.userService import UserService
from app.service.madorService import MadorService
from app.models.member_mador_access import MemberMadorAccessLevel

madorRouter = APIRouter()

# הגדרת רמות הרשאה
allow_super_admin_only = TokenValidator(allowed_roles=["super_admin"])
allow_admins_only = TokenValidator(allowed_roles=["admin", "super_admin"])
validator = TokenValidator(allowed_roles=["admin", "super_admin", "agent"])


# --- POST /madors/create ---
@madorRouter.post("/create", status_code=200, response_model=MadorOutput, dependencies=[Depends(allow_admins_only)])
def create_mador(mador_data: MadorInCreate, session: Session = Depends(get_db)):
    return MadorService(session=session).create_mador(mador_data=mador_data)
 
@madorRouter.get("/all", status_code=200, response_model=list[MadorOutput])
def get_all_madors(session: Session = Depends(get_db), user = Depends(validator)):
    user_role = getattr(user.role, "value", user.role)
    if user_role == "agent":
        return MadorService(session=session).get_madors_by_user_uuid(user_uuid=str(user.UUID))
    return MadorService(session=session).get_all_madors()
    
@madorRouter.get("/{mador_uuid}", status_code=200, response_model=MadorOutput)
def get_mador_by_uuid(mador_uuid: str, session: Session = Depends(get_db), user = Depends(allow_admins_only)):
    return MadorService(session=session).get_mador_by_uuid(mador_uuid=mador_uuid)
    
@madorRouter.delete("/{mador_uuid}", status_code=200, response_model=BoolOutput, dependencies=[Depends(allow_admins_only)])
def delete_mador(mador_uuid: str, session: Session = Depends(get_db)):
    success = MadorService(session=session).delete_mador(mador_uuid=mador_uuid)
    return BoolOutput(success=success)

@madorRouter.put("/{mador_uuid}", status_code=200, response_model=MadorOutput, dependencies=[Depends(allow_admins_only)])
def update_mador(mador_uuid: str, mador_data: MadorInUpdate, session: Session = Depends(get_db)):
    return MadorService(session=session).update_mador(mador_uuid=mador_uuid, mador_data=mador_data)

# --- POST /madors/{uuid}/add-member/{s_id}?access_level=... ---
# מוסיף חבר למדור עם רמת גישה (נשלח כ-query parameter)
@madorRouter.post("/{mador_uuid}/add-member/{user_s_id}", status_code=200, response_model=MadorOutput, dependencies=[Depends(allow_admins_only)])
def add_member_to_mador(
    mador_uuid: str,
    user_s_id: str,
    access_level: MemberMadorAccessLevel,
    session: Session = Depends(get_db),
):
    return MadorService(session=session).add_member_to_mador(
        mador_uuid=mador_uuid,
        user_s_id=user_s_id,
        access_level=access_level,
    )

# --- POST /madors/{uuid}/remove-member/{s_id} ---
# מסיר חבר מהמדור + מוחק רשומת הגישה שלו
@madorRouter.post("/{mador_uuid}/remove-member/{user_s_id}", status_code=200, response_model=MadorOutput, dependencies=[Depends(allow_admins_only)])
def remove_member_from_mador(mador_uuid: str, user_s_id: str, session: Session = Depends(get_db)):
    return MadorService(session=session).remove_member_from_mador(mador_uuid=mador_uuid, user_s_id=user_s_id)

# --- POST /madors/{uuid}/add-meeting/{meeting_uuid} ---
# משייך פגישה קיימת למדור
@madorRouter.post("/{mador_uuid}/add-meeting/{meeting_uuid}", status_code=200, response_model=MadorOutput, dependencies=[Depends(allow_admins_only)])
def add_meeting_to_mador(mador_uuid: str, meeting_uuid: str, session: Session = Depends(get_db)):
    return MadorService(session=session).add_meeting_to_mador(mador_uuid=mador_uuid, meeting_uuid=meeting_uuid)