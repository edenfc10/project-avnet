
# ============================================================================
# UserService - שכבת לוגיקה עסקית למשתמשים
# ============================================================================
# השכבה הזו מכילה את כל הלוגיקה העסקית שקשורה למשתמשים:
#   - התחברות (login): אימות סיסמה, יצירת JWT
#   - יצירת משתמש: הצפנת סיסמה, הגדרת תפקיד
#   - מחיקת משתמש: בדיקות הרשאות (מי יכול למחוק מי)
#   - שליפת פגישות מדור לפי רמת גישה של המשתמש
#
# Pattern: Service Layer
#   הService מתווך בין הRouter (הAPI) לבין הRepository (הDB).
#   מוסיף לוגיקה עסקית כמו הצפנת סיסמאות, בדיקות הרשאות, ופורמט פלט.
# ============================================================================

from typing import Dict

from sqlalchemy import String

from app.models.user import User
from app.repository.userRepo import UserRepository
from app.schema.user import UserInCreateNoRole, UserJWTData, UserOutput, UserInCreate, UserInLogin, UserToken, UserWithToken
from app.security.hashHelper import HashHelp
from app.security.auth import AuthHand
from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid


class UserService:
    def __init__(self, session):
        self.__userRepository = UserRepository(session=session)  # יוצר מופע של הרפוזיטורי
        self.session = session
    
    def login(self, login_details: UserInLogin) -> UserToken:
        """
        תהליך התחברות:
        1. בודק אם המשתמש קיים לפי s_id
        2. משווה סיסמה מול hash בDB (Argon2)
        3. יוצר JWT token עם פרטי המשתמש
        4. מחזיר token + role
        """
        user = self.__userRepository.get_user_by_s_id(s_id=login_details.s_id)
        if not user:  # בדיקה אם המשתמש קיים בDB
            raise HTTPException(status_code=400, detail="Please create an Account")

        # השוואת הסיסמה מול הhash השמור בDB
        if HashHelp.verify_password(
            plain_password=login_details.password, hashed_password=user.password
        ):
            # יצירת טוקן JWT עם פרטי המשתמש (UUID, role, s_id)
            jwt_data = UserJWTData(UUID=str(user.UUID), role=user.role, s_id=user.s_id)
            token = AuthHand.sign_jwt(jwt_data=jwt_data)
            if token:
                return UserToken(token=token, role=user.role)  # החזרת הטוקן והתפקיד
            raise HTTPException(status_code=500, detail="Unable to process request")
        raise HTTPException(status_code=400, detail="Please check your Credentials")

    def _role_value(self, role) -> str:
        """ עוזר - מחזיר את הערך הטקסטואלי של תפקיד (בין אם זה Enum או string) """
        return getattr(role, "value", role)
    
    def get_all_users(self, current_user_role: str, current_user_uuid: str | None = None) -> list[UserOutput]:
        """
        מחזיר את כל המשתמשים.
        אם המשתמש הנוכחי לא super_admin - מסתיר סופרים מהרשימה.
        """
        if current_user_role == "viewer" and current_user_uuid:
            users = self.__userRepository.get_users_in_same_madors(user_uuid=current_user_uuid)
        else:
            users = self.__userRepository.get_all_users()
        if current_user_role != "super_admin":
            users = [
                user
                for user in users
                if self._role_value(user.role) != "super_admin"
            ]
        return [UserOutput.model_validate(user, from_attributes=True) for user in users]


    def get_user_by_s_id(self ,s_id :str) -> User:
        user = self.__userRepository.get_user_by_s_id(s_id = s_id)
        if user:
            return user
        raise HTTPException(status_code = 400 , detail = "User is not available")

    def get_user_by_s_id_for_requester(self, s_id: str, requester_role: str, requester_uuid: str) -> User:
        """
        מחזיר משתמש לפי s_id, עם הגבלת viewer:
        viewer יכול לצפות רק במשתמשים שחולקים איתו מדור.
        """
        user = self.get_user_by_s_id(s_id=s_id)

        if requester_role == "viewer":
            group_users = self.__userRepository.get_users_in_same_madors(user_uuid=requester_uuid)
            allowed_ids = {str(u.UUID) for u in group_users}
            if str(user.UUID) not in allowed_ids:
                raise HTTPException(status_code=403, detail="Viewer can only access users in the same group")

        return user
    
    def delete_user(self, user_id: str, current_user_role: str, current_user_s_id: str) -> bool:
        """
        מוחק משתמש עם בדיקות הרשאות:
        - רק admin או super_admin יכולים למחוק
        - לא ניתן למחוק את עצמך
        - admin לא יכול למחוק super_admin
        """
        if current_user_role not in ("admin", "super_admin"):
            raise HTTPException(status_code=403, detail="Only admin or super_admin can delete users")

        target_user = self.__userRepository.get_user_by_s_id(s_id=user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        if target_user.s_id == current_user_s_id:
            raise HTTPException(status_code=400, detail="You cannot delete your own user")

        target_role = self._role_value(target_user.role)
        if current_user_role == "admin" and target_role == "super_admin":
            raise HTTPException(status_code=403, detail="Admin cannot delete super_admin users")

        return self.__userRepository.delete_user(user_id=user_id)
    
    def create_agent_user(self, user_data: UserInCreateNoRole) -> UserOutput:
        """ יוצר משתמש סוג agent - הסיסמה מוצפנת לפני שמירה """
        hashed_password = HashHelp.get_password_hash(plain_password=user_data.password)
        user_data.password = hashed_password
        user = self.__userRepository.create_agent_user(user_data=user_data)
        user = UserOutput(UUID=user.UUID,s_id=user.s_id,username=user.username, role=user.role, madors=[m.UUID for m in user.madors] )
        return user
    
    def create_admin_user(self, user_data: UserInCreateNoRole) -> UserOutput:
        """ יוצר משתמש סוג admin - הסיסמה מוצפנת לפני שמירה """
        hashed_password = HashHelp.get_password_hash(plain_password=user_data.password)
        user_data.password = hashed_password
        user = self.__userRepository.create_admin_user(user_data=user_data)
        user = UserOutput(UUID=user.UUID,s_id=user.s_id,username=user.username, role=user.role, madors=[m.UUID for m in user.madors] )
        return user

    def create_viewer_user(self, user_data: UserInCreateNoRole) -> UserOutput:
        """ יוצר משתמש סוג viewer - הסיסמה מוצפנת לפני שמירה """
        hashed_password = HashHelp.get_password_hash(plain_password=user_data.password)
        user_data.password = hashed_password
        user = self.__userRepository.create_viewer_user(user_data=user_data)
        user = UserOutput(UUID=user.UUID, s_id=user.s_id, username=user.username, role=user.role, madors=[m.UUID for m in user.madors])
        return user
    
    def get_mador_meetings_by_user_uuid(self, user_uuid: str, mador_uuid: str) -> list[str]:
        """
        מחזיר רשימת פגישות שמשתמש רשאי לראות במדור.
        מסתמך על רמת הגישה מטבלת member_mador_access.
        """
        meetings = self.__userRepository.get_mador_meetings_by_user_uuid(user_uuid=user_uuid, mador_uuid=mador_uuid)
        if meetings is not None:
            return meetings
        else:
            raise HTTPException(status_code=400, detail="User or Mador is not available")