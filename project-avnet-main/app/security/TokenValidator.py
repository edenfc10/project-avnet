# ============================================================================
# TokenValidator - בודק טוקן והרשאות תפקיד
# ============================================================================
# FastAPI Dependency שמשמש כ-middleware לאימות:
#   1. מפענח את הJWT token מה-header
#   2. בודק שהטוקן תקין ולא פג תוקף
#   3. בודק שהתפקיד של המשתמש מתאים לנתיב
#   4. בודק שהמשתמש עדיין קיים בDB
#
# שימוש:
#   allow_admins_only = TokenValidator(allowed_roles=["admin", "super_admin"])
#   @router.get("/endpoint", dependencies=[Depends(allow_admins_only)])
# ============================================================================

import time

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db
from app.models.user import User
from app.security.auth import AuthHand
from sqlalchemy.orm import Session


security = HTTPBearer()

class TokenValidator:
    """ בודק טוקן JWT ומוודא שהתפקיד של המשתמש מורשה """

    def __init__(self, allowed_roles: list[str], allow_theirs_only: bool = False):
        self.allowed_roles = allowed_roles  # רשימת התפקידים המותרים
        self.allow_theirs_only = allow_theirs_only

    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
        """ נקרא אוטומטית על ידי FastAPI בכל endpoint שמשתמש ב-Depends """
       
        # שלב 1: פיענוח הטוקן
        token = credentials.credentials
        
        payload = AuthHand.decode_jwt(token)

        if not payload:
            raise HTTPException(
                status_code=401, 
                detail="Invalid or expired token"
            )

        # שלב 2: שליפת פרטי המשתמש מהטוקן
        user_role = payload.get("role")
        user_UUID = payload.get("UUID")

        # שלב 3: בדיקה שהמשתמש קיים בDB
        user = db.query(User).filter_by(UUID=user_UUID).first()
                
        # שלב 4: בדיקה שהתפקיד מותר לנתיב הזה
        if user_role not in self.allowed_roles:  
            raise HTTPException(
                status_code=403, 
                detail="You do not have the required permissions"
            )
        
        if not user:
            raise HTTPException(
                status_code=404, 
                detail="User not exists"
            )
        
        return user