from fastapi import APIRouter, Depends
from app.schema.user import BoolOutput, UserInCreateNoRole, UserOutput
from app.core.database import get_db  # יוצרת חיבור לDB באמצעות הספרייה הבאה 
from sqlalchemy.orm import Session  #ביצוע פעולות על הDB
from app.security.TokenValidator import TokenValidator
from app.service.userService import UserService 

userRouter = APIRouter()   #יצירת ROUTER חדש

allow_super_admin_only = TokenValidator(allowed_roles=["super_admin"])  # יצירת אובייקט של TokenValidator עם הרשאות מתאימות
allow_admins_only = TokenValidator(allowed_roles=["admin", "super_admin"])
validator = TokenValidator(allowed_roles=["admin", "super_admin", "agent"])

# הקובץ שמגדיר איך הלקוח מדבר עם השרת
@userRouter.get("/all", status_code=200, response_model=list[UserOutput])
def get_all_users(session: Session = Depends(get_db), user = Depends(validator)):
    try:
        return UserService(session=session).get_all_users()
    except Exception as error:
        print(error)
        raise error


@userRouter.get("/{s_id}", status_code=200, response_model=UserOutput)
def get_user_by_s_id(s_id: str, session: Session = Depends(get_db), user = Depends(validator)):
    try:
        user = UserService(session=session).get_user_by_s_id(s_id=s_id)
        return UserOutput.model_validate(user, from_attributes=True)
    except Exception as error:
        print(error)
        raise error

@userRouter.post("/create-agent", status_code=200, response_model=UserOutput, dependencies=[Depends(allow_admins_only)])
def create_agent_user(user_data: UserInCreateNoRole, session: Session = Depends(get_db)):
    try:
        return UserService(session=session).create_agent_user(user_data=user_data)
    except Exception as error:
        print(error)
        raise error
        
@userRouter.post("/create-admin", status_code=200, response_model=UserOutput, dependencies=[Depends(allow_super_admin_only)])
def create_admin_user(user_data: UserInCreateNoRole, session: Session = Depends(get_db)):
    try:
        return UserService(session=session).create_admin_user(user_data=user_data)
    except Exception as error:
        print(error)
    
    

@userRouter.delete("/{user_id}", status_code=200, response_model=BoolOutput, dependencies=[Depends(allow_super_admin_only)])
def delete_user(user_id: str, session: Session = Depends(get_db)):
    try:
        success = UserService(session=session).delete_user(user_id=user_id)
        return BoolOutput(success=success)
    except Exception as error:
        print(error)
        
