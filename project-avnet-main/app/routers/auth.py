# ============================================================================
# Auth Router - נתיבי אימות (Login)
# ============================================================================
# נתיב אחד בלבד: POST /auth/login
# מקבל מהלקוח s_id + סיסמה, מחזיר JWT token + תפקיד.
# זה הנתיב היחיד שלא דורש אימות - כל שאר הנתיבים דורשים token.
# ============================================================================

from ast import Dict

from fastapi import APIRouter, Depends, Header
from app.schema.user import UserInCreate, UserInLogin, UserToken, UserWithToken, UserOutput
from app.core.database import get_db  # יוצרת חיבור לבסיס הנתונים
from sqlalchemy.orm import Session  # ביצוע פעולות על הDB
from app.service.userService import UserService

authRouter = APIRouter()  # יצירת Router לנתיבי auth


# --- POST /auth/login ---
# מקבל: { s_id: string, password: string }
# מחזיר: { token: string, role: string }
@authRouter.post("/login", status_code=200, response_model=UserToken)
def login(loginDetails: UserInLogin, session: Session = Depends(get_db)):
    try:
        return UserService(session=session).login(login_details=loginDetails)
    except Exception as error:
        print(error)
        
    

