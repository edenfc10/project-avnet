# ============================================================================
# MadorRepository - שכבת גישה לנתונים של מדורים
# ============================================================================
# אחראית על כל פעולות הDB שקשורות למדורים:
#   - CRUD מלא (create/read/update/delete)
#   - ניהול חברים: הוספה, הסרה, עדכון רמת גישה
#   - ניהול פגישות: שיוך פגישה למדור
#
# תהליך הוספת חבר:
#   1. בודק שהמדור והמשתמש קיימים
#   2. אם המשתמש לא חבר, מוסיף אותו למדור
#   3. מוחק רשומת גישה ישנה (אם קיימת) ומוסיף חדשה
# ============================================================================

from .base import BaseRepository
import uuid
from app.models.user import User
from app.models.mador import Mador
from app.models.meeting import Meeting
from app.models.member_mador_access import MemberMadorAccess, MemberMadorAccessLevel
from app.schema.user import MadorInCreate, MadorInUpdate, MadorOutput


class MadorRepository(BaseRepository):

    def create_mador(self, mador_data: MadorInCreate) -> MadorOutput:
        """ יוצר מדור חדש בDB """
        data = mador_data.model_dump(exclude_none=True)
        new_mador = Mador(**data)

        self.session.add(new_mador)
        self.session.commit()
        self.session.refresh(new_mador)
        return new_mador

    def get_all_madors(self) -> list[MadorOutput]:
        """ מחזיר את כל המדורים """
        return self.session.query(Mador).all()

    def get_madors_by_user_uuid(self, user_uuid: str) -> list[MadorOutput]:
        """ מחזיר רק את המדורים שהמשתמש שייך אליהם """
        try:
            normalized_user_uuid = uuid.UUID(str(user_uuid))
        except (ValueError, TypeError):
            return []

        user = self.session.query(User).filter(User.UUID == normalized_user_uuid).first()
        if not user:
            return []
        return list(user.madors)

    def get_mador_by_uuid(self, mador_uuid: str) -> MadorOutput:
        """ מוצא מדור לפי UUID """
        return self.session.query(Mador).filter(Mador.UUID == mador_uuid).first()

    def delete_mador(self, mador_uuid: str) -> bool:
        """ מוחק מדור לפי UUID. מחזיר True אם הצליח """
        mador = self.session.query(Mador).filter(Mador.UUID == mador_uuid).first()
        if mador:
            self.session.delete(mador)
            self.session.commit()
            return True
        return False

    def update_mador(self, mador_uuid: str, mador_data: MadorInUpdate) -> MadorOutput:
        """ מעדכן פרטי מדור (למשל שם) - רק שדות שנשלחו """
        mador = self.session.query(Mador).filter(Mador.UUID == mador_uuid).first()
        if not mador:
            return None

        for key, value in mador_data.model_dump(exclude_none=True).items():
            setattr(mador, key, value)

        self.session.commit()
        self.session.refresh(mador)
        return mador

    def add_member_to_mador(
        self,
        mador_uuid: str,
        user_s_id: str,
        access_level: MemberMadorAccessLevel,
    ) -> MadorOutput:
        """
        מוסיף חבר למדור עם רמת גישה מסוימת.
        אם החבר כבר קיים - מוסיף רמת גישה נוספת (ללא מחיקה של הקיימות).
        """
        mador = self.session.query(Mador).filter(Mador.UUID == mador_uuid).first()
        user = self.session.query(User).filter(User.s_id == user_s_id).first()

        if not mador or not user:
            return None

        # אם המשתמש לא חבר עדיין - מוסיף אותו למדור
        if user not in mador.members:
            mador.members.append(user)

        # אם רמת הגישה כבר קיימת - לא מוסיפים כפילות.
        existing = self.session.query(MemberMadorAccess).filter(
            MemberMadorAccess.member_uuid == user.UUID,
            MemberMadorAccess.mador_uuid == mador.UUID,
            MemberMadorAccess.access_level == access_level,
        ).first()

        if not existing:
            self.session.add(
                MemberMadorAccess(
                    member_uuid=user.UUID,
                    mador_uuid=mador.UUID,
                    access_level=access_level,
                )
            )

        self.session.commit()
        self.session.refresh(mador)
        return mador

    def remove_member_from_mador(self, mador_uuid: str, user_s_id: str) -> MadorOutput:
        """
        מסיר חבר מהמדור.
        גם מוחק את רשומת הגישה שלו מהטבלה member_mador_access.
        """
        mador = self.session.query(Mador).filter(Mador.UUID == mador_uuid).first()
        user = self.session.query(User).filter(User.s_id == user_s_id).first()

        if not mador or not user:
            return None

        if user in mador.members:
            mador.members.remove(user)
            self.session.query(MemberMadorAccess).filter(
                MemberMadorAccess.member_uuid == user.UUID,
                MemberMadorAccess.mador_uuid == mador.UUID,
            ).delete()
            self.session.commit()
            self.session.refresh(mador)

        return mador

    def add_meeting_to_mador_by_uuid(self, mador_uuid: str, meeting_uuid: str) -> MadorOutput:
        """
        משייך פגישה למדור (לפי UUID של שניהם).
        מונע כפילויות - לא מוסיף אם הפגישה כבר שייכת.
        """
        mador = self.session.query(Mador).filter(Mador.UUID == mador_uuid).first()
        meeting = self.session.query(Meeting).filter(Meeting.UUID == meeting_uuid).first()

        if not mador or not meeting:
            return None

        if meeting not in mador.meetings:
            mador.meetings.append(meeting)

        self.session.commit()
        self.session.refresh(mador)
        return mador

