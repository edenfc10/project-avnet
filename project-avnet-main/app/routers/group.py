# ============================================================================
# Group Router - API routes for group management
# ============================================================================
# פעולות:
#   POST   /groups/create                          - יצירת קבוצה חדשה
#   GET    /groups/all                             - שליפת כל הקבוצות
#   GET    /groups/{uuid}                          - שליפת קבוצה בודדת
#   DELETE /groups/{uuid}                          - מחיקת קבוצה
#   PUT    /groups/{uuid}                          - עדכון קבוצה
#   POST   /groups/{uuid}/add-member/{s_id}        - הוספת חבר + רמת גישה
#   POST   /groups/{uuid}/remove-member/{s_id}     - הסרת חבר
#   POST   /groups/{uuid}/add-meeting/{meeting_uuid} - שיוך פגישה לקבוצה
#
# הרשאות: admin + super_admin בלבד
# ============================================================================

from fastapi import APIRouter, Depends
from app.schema.user import BoolOutput, GroupInCreate, GroupInUpdate, GroupInUpdate, GroupOutput, UserInCreateNoRole, UserOutput
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.security.TokenValidator import TokenValidator
from app.service.userService import UserService
from app.service.groupService import GroupService
from app.models.member_group_access import MemberGroupAccessLevel

groupRouter = APIRouter()

 # הגדרת רמות הרשאה
allow_super_admin_only = TokenValidator(allowed_roles=["super_admin"])
allow_admins_only = TokenValidator(allowed_roles=["admin", "super_admin"])
validator = TokenValidator(allowed_roles=["admin", "super_admin", "agent", "viewer"])


# --- POST /groups/create ---
@groupRouter.post("/create", status_code=200, response_model=GroupOutput, dependencies=[Depends(allow_admins_only)])
def create_group(group_data: GroupInCreate, session: Session = Depends(get_db)):
    return GroupService(session=session).create_group(group_data=group_data)
 
@groupRouter.get("/all", status_code=200, response_model=list[GroupOutput])
def get_all_groups(session: Session = Depends(get_db), user = Depends(validator)):
    user_role = getattr(user.role, "value", user.role)
    if user_role in ("agent", "viewer"):
        return GroupService(session=session).get_groups_by_user_uuid(user_uuid=str(user.UUID))
    return GroupService(session=session).get_all_groups()
    
@groupRouter.get("/{group_uuid}", status_code=200, response_model=GroupOutput)
def get_group_by_uuid(group_uuid: str, session: Session = Depends(get_db), user = Depends(allow_admins_only)):
    return GroupService(session=session).get_group_by_uuid(group_uuid=group_uuid)
    
@groupRouter.delete("/{group_uuid}", status_code=200, response_model=BoolOutput, dependencies=[Depends(allow_admins_only)])
def delete_group(group_uuid: str, session: Session = Depends(get_db)):
    success = GroupService(session=session).delete_group(group_uuid=group_uuid)
    return BoolOutput(success=success)

@groupRouter.put("/{group_uuid}", status_code=200, response_model=GroupOutput, dependencies=[Depends(allow_admins_only)])
def update_group(group_uuid: str, group_data: GroupInUpdate, session: Session = Depends(get_db)):
    return GroupService(session=session).update_group(group_uuid=group_uuid, group_data=group_data)

# --- POST /groups/{uuid}/add-member/{s_id}?access_level=... ---
# מוסיף חבר לקבוצה עם רמת גישה (נשלח כ-query parameter)
@groupRouter.post("/{group_uuid}/add-member/{user_s_id}", status_code=200, response_model=GroupOutput, dependencies=[Depends(allow_admins_only)])
def add_member_to_group(
    group_uuid: str,
    user_s_id: str,
    access_level: MemberGroupAccessLevel,
    session: Session = Depends(get_db),
):
    return GroupService(session=session).add_member_to_group(
        group_uuid=group_uuid,
        user_s_id=user_s_id,
        access_level=access_level,
    )

# --- POST /groups/{uuid}/remove-member/{s_id} ---
# מסיר חבר מהקבוצה + מוחק הרשאות גישה שלו
@groupRouter.post("/{group_uuid}/remove-member/{user_s_id}", status_code=200, response_model=GroupOutput, dependencies=[Depends(allow_admins_only)])
def remove_member_from_group(group_uuid: str, user_s_id: str, session: Session = Depends(get_db)):
    return GroupService(session=session).remove_member_from_group(group_uuid=group_uuid, user_s_id=user_s_id)

# --- POST /groups/{uuid}/add-meeting/{meeting_uuid} ---
# משייך פגישה קיימת לקבוצה
@groupRouter.post("/{group_uuid}/add-meeting/{meeting_uuid}", status_code=200, response_model=GroupOutput, dependencies=[Depends(allow_admins_only)])
def add_meeting_to_group(group_uuid: str, meeting_uuid: str, session: Session = Depends(get_db)):
    return GroupService(session=session).add_meeting_to_group(group_uuid=group_uuid, meeting_uuid=meeting_uuid)
