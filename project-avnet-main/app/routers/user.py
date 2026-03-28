# ============================================================================
# User Router - נתיבי API לניהול משתמשים
# ============================================================================
# נתיבים:
#   GET    /users/all              - שליפת כל המשתמשים
#   GET    /users/{s_id}           - שליפת משתמש לפי מזהה
#   POST   /users/create-agent     - יצירת agent (לאדמינים בלבד)
#   POST   /users/create-admin     - יצירת admin (לsuper_admin בלבד)
#   DELETE /users/{user_id}        - מחיקת משתמש
#   GET    /users/mador/{uuid}/meetings - פגישות מדור לפי רמת גישה
#
# הרשאות (TokenValidator):
#   - allow_super_admin_only: רק super_admin
#   - allow_admins_only: admin + super_admin
#   - validator: כל התפקידים (כולל agent)
# ============================================================================

from fastapi import APIRouter, Depends, HTTPException
from app.schema.user import BoolOutput, UserInCreateNoRole, UserOutput
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.security.TokenValidator import TokenValidator
from app.service.userService import UserService

userRouter = APIRouter()

# הגדרת רמות הרשאה - מי יכול לגשת לכל נתיב
allow_super_admin_only = TokenValidator(allowed_roles=["super_admin"])
allow_admins_only = TokenValidator(allowed_roles=["admin", "super_admin"])
validator = TokenValidator(allowed_roles=["admin", "super_admin", "agent", "viewer"])
theirs_only = TokenValidator(allowed_roles=["admin", "super_admin", "agent" ,"viewer"], allow_theirs_only=True)


# --- GET /users/all ---
# מחזיר את כל המשתמשים (מסנן super_admin אם הקורא לא סופר)
@userRouter.get("/all", status_code=200, response_model=list[UserOutput])
def get_all_users(session: Session = Depends(get_db), user = Depends(validator)):
    try:
        return UserService(session=session).get_all_users(
            current_user_role=user.role.value,
            current_user_uuid=str(user.UUID),
        )
    except Exception as error:
        print(error)
        raise HTTPException(status_code=500, detail=str(error))
       

# --- GET /users/{s_id} ---
# שולף משתמש בודד לפי מזהה המשתמש
@userRouter.get("/{s_id}", status_code=200, response_model=UserOutput)
def get_user_by_s_id(s_id: str, session: Session = Depends(get_db), user = Depends(validator)):
    requested_user = UserService(session=session).get_user_by_s_id_for_requester(
        s_id=s_id,
        requester_role=user.role.value,
        requester_uuid=str(user.UUID),
    )
    return UserOutput.model_validate(requested_user, from_attributes=True)
   

# --- POST /users/create-agent ---
# יוצר משתמש agent - רק admin או super_admin
@userRouter.post("/create-agent", status_code=200, response_model=UserOutput, dependencies=[Depends(allow_admins_only)])
def create_agent_user(user_data: UserInCreateNoRole, session: Session = Depends(get_db)):
        return UserService(session=session).create_agent_user(user_data=user_data)

       
        
# --- POST /users/create-admin ---
# יוצר משתמש admin - רק super_admin
@userRouter.post("/create-admin", status_code=200, response_model=UserOutput, dependencies=[Depends(allow_super_admin_only)])
def create_admin_user(user_data: UserInCreateNoRole, session: Session = Depends(get_db)):
    return UserService(session=session).create_admin_user(user_data=user_data)


# --- POST /users/create-viewer ---
# יוצר משתמש viewer - רק admin או super_admin
@userRouter.post("/create-viewer", status_code=200, response_model=UserOutput, dependencies=[Depends(allow_admins_only)])
def create_viewer_user(user_data: UserInCreateNoRole, session: Session = Depends(get_db)):
    return UserService(session=session).create_viewer_user(user_data=user_data)
    

# --- DELETE /users/{user_id} ---
# מוחק משתמש - רק admin או super_admin
@userRouter.delete("/{user_id}", status_code=200, response_model=BoolOutput, dependencies=[Depends(allow_admins_only)])
def delete_user(user_id: str, session: Session = Depends(get_db), user = Depends(allow_admins_only)):
    success = UserService(session=session).delete_user(
        user_id=user_id,
        current_user_role=user.role.value,
        current_user_s_id=user.s_id,
    )
    return BoolOutput(success=success)

# --- GET /users/mador/{mador_uuid}/meetings ---
# מחזיר פגישות שהמשתמש הנוכחי רשאי לראות במדור (לפי access level)
@userRouter.get("/mador/{mador_uuid}/meetings", status_code=200, response_model=list[str])
def get_mador_meetings_by_user_uuid(mador_uuid: str, session: Session = Depends(get_db), user = Depends(validator)):
    return UserService(session=session).get_mador_meetings_by_user_uuid(user_uuid=str(user.UUID), mador_uuid=mador_uuid)