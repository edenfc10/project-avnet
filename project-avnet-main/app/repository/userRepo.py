# ============================================================================
# UserRepository - שכבת גישה לנתונים של משתמשים
# ============================================================================
# אחראית על כל פעולות הDB הקשורות למשתמשים:
#   - יצירת משתמש (agent/admin)
#   - שליפת משתמש לפי s_id
#   - קבלת כל המשתמשים
#   - מחיקת משתמש
#   - שליפת פגישות מדור לפי רמת גישה של משתמש
#
# Pattern: Repository Pattern
#   השכבה הזו מדברת רק עם הDB דרך SQLAlchemy.
#   הService משתמש ברפוזיטורי ומוסיף לוגיקה עסקית.
# ============================================================================

import uuid

from .base import BaseRepository
from app.models.user import User
from app.models.mador import Mador

from app.schema.user import UserInCreate, UserInCreateNoRole, UserOutput
from app.models.member_mador_access import MemberMadorAccess, MemberMadorAccessLevel


class UserRepository(BaseRepository):

    def create_user(self, user_data: UserInCreate) -> UserOutput:
        """  יוצר משתמש חדש בDB ומשייך אותו למדורים אם צוינו """
        data = user_data.model_dump(exclude_none=True)

        # מוציא את רשימת המדורים מהdata לפני יצירת היוזר
        mador_ids = data.pop("mador_ids", [])

        new_user = User(**data)

        # אם צוינו מדורים - משייך את המשתמש אליהם
        if mador_ids and len(mador_ids) > 0:
            madors = self.session.query(Mador).filter(Mador.UUID.in_(mador_ids)).all()
            new_user.madors.extend(madors)

        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)

        return new_user
    
    def create_agent_user(self, user_data: UserInCreateNoRole):
        """ יוצר משתמש עם תפקיד agent אוטומטית """
        data = UserInCreate(**user_data.model_dump(), role="agent").model_dump(exclude_none=True)
        return self.create_user(UserInCreate(**data))
    
    def create_admin_user(self, user_data: UserInCreateNoRole):
        """ יוצר משתמש עם תפקיד admin אוטומטית """
        data = UserInCreate(**user_data.model_dump(), role="admin").model_dump(exclude_none=True)
        return self.create_user(UserInCreate(**data))
    
    def get_user_by_s_id(self, s_id: str) -> UserOutput:
        """ מוצא משתמש לפי מזהה המשתמש (s_id) """
        user = self.session.query(User).filter_by(s_id=s_id).first()
        return user

    def get_all_users(self) -> list[UserOutput]:
        """ מחזיר את כל המשתמשים במערכת """
        users = self.session.query(User).all()
        return users

    def delete_user(self, user_id: str) -> bool:
        """ מוחק משתמש לפי s_id. מחזיר True אם הצליח """
        user = self.session.query(User).filter_by(s_id=user_id).first()
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
    
        return False

    def get_mador_meetings_by_user_uuid(self, user_uuid: str, mador_uuid: str) -> list[str]:
        """
        מחזיר רשימת הפגישות שמשתמש רשאי לראות במדור מסוים.
        הלוגיקה:
          1. שולף את רמות הגישה של המשתמש במדור מטבלת member_mador_access
          2. מסנן את כל הפגישות שה-accessLevel שלהן תואם לרמת הגישה
        זה מאפשר לסוכן agent לראות רק פגישות שהוא הורשה לראות.
        """
        # שליפת הקשרים של המשתמש במדור הנתון
        connections = self.session.query(MemberMadorAccess).filter(MemberMadorAccess.member_uuid == user_uuid, MemberMadorAccess.mador_uuid == mador_uuid).all()
        # יצירת רשימת רמות הגישה המותרות
        access_allowed = [conn.access_level for conn in connections]

        # סינון פגישות - מחזיר רק פגישות שהסוג שלהן תואם לרמת הגישה
        meetings = self.session.query(Mador).filter(Mador.UUID == mador_uuid).first().meetings
        return [str(meeting.UUID) for meeting in meetings if meeting.accessLevel in access_allowed]