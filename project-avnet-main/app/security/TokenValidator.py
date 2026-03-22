import time

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db
from app.models.user import User
from app.security.auth import AuthHand
from sqlalchemy.orm import Session


security = HTTPBearer()

class TokenValidator:
    def __init__(self, allowed_roles: list[str]):
        
        self.allowed_roles = allowed_roles

    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
       
        token = credentials.credentials
        
        payload = AuthHand.decode_jwt(token)

        if not payload:
            raise HTTPException(
                status_code=401, 
                detail="Invalid or expired token"
            )

        user_role = payload.get("role")
        user_UUID = payload.get("UUID")

        user = db.query(User).filter_by(UUID=user_UUID).first()
                
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