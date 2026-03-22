from fastapi import Depends , HTTPException , status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Any
from app.security.auth import AuthHand
from app.service.userService import UserService
from app.core.database import get_db
from app.schema.user import UserOutput


from fastapi import APIRouter

AUTH_PREFIX = 'Bearer ' #קבוע Authorization

security = HTTPBearer()

def get_current_user(
    credentials: Any = Depends(security),
    session: Session = Depends(get_db)
) -> UserOutput:
    auth_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED ,        
        detail = "Invalid Authentication Credentials"
    )
    
    token = credentials.credentials
    payload = AuthHand.decode_jwt(token)

    if payload and payload.get("s_id"):
        try:
            user = UserService(session=session).get_user_by_s_id(payload["s_id"])
            return UserOutput(UUID=user.UUID, s_id=user.s_id, username=user.username, role=user.role, madors=user.madors)
        except Exception as error:
            raise error
    raise auth_exception


protectRouter = APIRouter()

@protectRouter.get("/me")
def get_protected_data(user: UserOutput = Depends(get_current_user)):
    return {"message": "This is a protected route", "user": user}
