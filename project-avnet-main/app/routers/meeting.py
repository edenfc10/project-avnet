# ============================================================================
# Meeting Router - × ×ª×™×‘×™ API ×œ× ×™×”×•×œ ×¤×’×™×©×•×ª
# ============================================================================
# × ×ª×™×‘×™×:
#   GET    /meetings/all                   - ×©×œ×™×¤×ª ×›×œ ×”×¤×’×™×©×•×ª
#   GET    /meetings/{uuid}                - ×©×œ×™×¤×ª ×¤×’×™×©×” ×‘×•×“×“×ª ×œ×¤×™ UUID
#   POST   /meetings/create                - ×™×¦×™×¨×ª ×¤×’×™×©×” ×—×“×©×”
#   DELETE /meetings/{uuid}                - ×ž×—×™×§×ª ×¤×’×™×©×”
#   PUT    /meetings/{uuid}                - ×¢×“×›×•×Ÿ ×¤×’×™×©×” ×œ×¤×™ UUID
#   GET    /meetings/number/{number}       - ×©×œ×™×¤×ª ×¤×’×™×©×” ×œ×¤×™ ×ž×¡×¤×¨
#   PUT    /meetings/number/{number}       - ×¢×“×›×•×Ÿ ×¤×’×™×©×” ×œ×¤×™ ×ž×¡×¤×¨
#   GET    /meetings/group/{group_uuid}    - ×¨×©×™×ž×ª ×¤×’×™×©×•×ª ×œ×¤×™ ×ž×“×•×¨
#
# ×”×¨×©××•×ª: admin + super_admin ×‘×œ×‘×“
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException
from app.schema.meeting import MeetingInCreate, MeetingInUpdate, MeetingOutput
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.security.TokenValidator import TokenValidator
from app.service.meetingService import MeetingService

meetingRouter = APIRouter()

# ×”×’×“×¨×ª ×¨×ž×•×ª ×”×¨×©××”
allow_super_admin_only = TokenValidator(allowed_roles=["super_admin"])
allow_admins_only = TokenValidator(allowed_roles=["admin", "super_admin"])
validator = TokenValidator(allowed_roles=["admin", "super_admin", "agent", "viewer"])

# ×”×§×•×‘×¥ ×©×ž×’×“×™×¨ ××™×š ×”×œ×§×•×— ×ž×“×‘×¨ ×¢× ×”×©×¨×ª
@meetingRouter.get("/all", status_code=200, response_model=list[MeetingOutput])
def get_all_meetings(session: Session = Depends(get_db), user = Depends(allow_admins_only)):
    try:
        return MeetingService(session=session).get_all_meetings()
    except Exception as error:
        print(error)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@meetingRouter.get("/{meeting_uuid}", status_code=200, response_model=MeetingOutput)
def get_meeting_by_uuid(meeting_uuid: str, session: Session = Depends(get_db), user = Depends(validator)):
    user_role = getattr(user.role, "value", user.role)
    return MeetingService(session=session).get_meeting_by_uuid_for_user(
        meeting_uuid=meeting_uuid,
        user_uuid=str(user.UUID),
        user_role=user_role,
    )
   
@meetingRouter.post("/create", status_code=200, response_model=MeetingOutput, dependencies=[Depends(allow_super_admin_only)])
def create_meeting(meeting_data: MeetingInCreate, session: Session = Depends(get_db)):
    return MeetingService(session=session).create_meeting(meeting_data=meeting_data)

@meetingRouter.delete("/{meeting_uuid}", status_code=200, dependencies=[Depends(allow_admins_only)])
def delete_meeting(meeting_uuid: str, session: Session = Depends(get_db)):
    success = MeetingService(session=session).delete_meeting(meeting_uuid=meeting_uuid)
    if success:
        return {"detail": "Meeting deleted successfully"}

@meetingRouter.put("/{meeting_uuid}", status_code=200, response_model=MeetingOutput, dependencies=[Depends(allow_admins_only)])
def update_meeting_by_uuid(meeting_uuid: str, meeting_data: MeetingInUpdate, session: Session = Depends(get_db)):
    return MeetingService(session=session).update_meeting_by_uuid(meeting_uuid=meeting_uuid, meeting_data=meeting_data)

@meetingRouter.get("/number/{number}", status_code=200, response_model=MeetingOutput)
def get_meeting_by_number(number: int, session: Session = Depends(get_db), user = Depends(allow_admins_only)):
    return MeetingService(session=session).get_meeting_by_number(number=number)

@meetingRouter.put("/number/{meeting_number}", status_code=200, response_model=MeetingOutput, dependencies=[Depends(allow_admins_only)])
def update_meeting_by_number(meeting_number: str, meeting_data: MeetingInUpdate, session: Session = Depends(get_db)):
    return MeetingService(session=session).update_meeting_by_number(meeting_number=meeting_number, meeting_data=meeting_data)

@meetingRouter.get("/group/{group_uuid}", status_code=200, response_model=list[str])
def get_meetings_by_group_uuid(group_uuid: str, session: Session = Depends(get_db), user = Depends(allow_admins_only)):
    return MeetingService(session=session).get_meetings_by_group_uuid(group_uuid=group_uuid)
