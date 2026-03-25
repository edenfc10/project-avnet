# ============================================================================
# MeetingRepository - שכבת גישה לנתונים של פגישות
# ============================================================================
# אחראית על כל פעולות הDB הקשורות לפגישות:
#   - CRUD מלא (create/read/update/delete)
#   - חיפוש לפי UUID, מספר פגישה, או מדור
#   - עדכון לפי UUID או לפי מספר פגישה
# ============================================================================

import uuid

from .base import BaseRepository
from app.models.user import User
from app.models.mador import Mador

from app.schema.user import UserInCreate, UserInCreateNoRole, UserOutput
from app.schema.meeting import MeetingInCreate, MeetingInUpdate, MeetingOutput
from app.models.meeting import Meeting
from app.models.member_mador_access import MemberMadorAccess


class MeetingRepository(BaseRepository):

    def create_meeting(self, meeting_data: MeetingInCreate) -> MeetingOutput:
        """ יוצר פגישה חדשה בDB """
        data = meeting_data.model_dump(exclude_none=True)

        new_meeting = Meeting(**data)

        self.session.add(new_meeting)
        self.session.commit()
        self.session.refresh(new_meeting)

        return new_meeting
    
    
    def delete_meeting(self, meeting_uuid: str) -> bool:
        """ מוחק פגישה לפי UUID. מחזיר True אם הצליח """
        meeting = self.session.query(Meeting).filter(Meeting.UUID == meeting_uuid).first()
        if meeting:
            self.session.delete(meeting)
            self.session.commit()
            return True
        return False
    
    def get_meeting_by_uuid(self, meeting_uuid: str) -> MeetingOutput:
        """ מוצא פגישה לפי UUID """
        meeting = self.session.query(Meeting).filter(Meeting.UUID == meeting_uuid).first()
        return meeting

    def user_can_access_meeting(self, user_uuid: str, meeting_uuid: str) -> bool:
        """
        בודק האם למשתמש יש גישה לפגישה:
        - המשתמש צריך להיות חבר בלפחות מדור אחד של הפגישה
        - ובאותו מדור חייבת להיות לו רמת גישה שמתאימה לסוג הפגישה
        """
        try:
            normalized_user_uuid = uuid.UUID(str(user_uuid))
        except (ValueError, TypeError):
            return False

        meeting = self.get_meeting_by_uuid(meeting_uuid=meeting_uuid)
        if not meeting:
            return False

        user = self.session.query(User).filter(User.UUID == normalized_user_uuid).first()
        if not user:
            return False

        meeting_level = getattr(meeting.accessLevel, "value", meeting.accessLevel)
        meeting_level = str(meeting_level).lower().strip()
        if meeting_level not in {"audio", "video", "blast_dial"}:
            return False

        # בדיקת חברות במדור
        user_mador_uuids = {m.UUID for m in user.madors}
        for mador in meeting.madors:
            if mador.UUID not in user_mador_uuids:
                continue

            # בדיקת הרשאה באותו מדור
            for access_row in mador.member_access_levels:
                if access_row.member_uuid != user.UUID:
                    continue

                access_level = getattr(access_row.access_level, "value", access_row.access_level)
                access_level = str(access_level).lower().strip()
                if access_level == meeting_level:
                    return True

        return False
    
    def get_all_meetings(self) -> list[MeetingOutput]:
        """ מחזיר את כל הפגישות במערכת """
        return self.session.query(Meeting).all()
    
    def get_meeting_by_number(self, number: int) -> MeetingOutput:
        """ מוצא פגישה לפי מספר הפגישה (m_number) """
        meeting = self.session.query(Meeting).filter(Meeting.m_number == number).first()
        return meeting
    
    def get_meetings_by_mador_uuid(self, mador_uuid: str) -> list[str]:
        """ מחזיר רשימת UUIDs של פגישות השייכות למדור """
        mador = self.session.query(Mador).filter(Mador.UUID == mador_uuid).first()
        if mador:
            return [meeting.UUID for meeting in mador.meetings]
        return []
    
    def update_meeting_by_number(self, meeting_number: str, meeting_data: MeetingInUpdate) -> MeetingOutput:
        """ מעדכן פגישה לפי מספר - רק שדות שנשלחו """
        meeting = self.session.query(Meeting).filter(Meeting.m_number == meeting_number).first()
        if not meeting:
            return None

        for key, value in meeting_data.model_dump(exclude_none=True).items():
            setattr(meeting, key, value)

        self.session.commit()
        self.session.refresh(meeting)
        return meeting
    
    def update_meeting_by_uuid(self, meeting_uuid: str, meeting_data: MeetingInUpdate) -> MeetingOutput:
        """ מעדכן פגישה לפי UUID - רק שדות שנשלחו """
        meeting = self.session.query(Meeting).filter(Meeting.UUID == meeting_uuid).first()
        if not meeting:
            return None

        for key, value in meeting_data.model_dump(exclude_none=True).items():
            setattr(meeting, key, value)

        self.session.commit()
        self.session.refresh(meeting)
        return meeting