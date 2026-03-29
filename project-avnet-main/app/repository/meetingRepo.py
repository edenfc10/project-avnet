# ============================================================================
# MeetingRepository - ×©×›×‘×ª ×’×™×©×” ×œ× ×ª×•× ×™× ×©×œ ×¤×’×™×©×•×ª
# ============================================================================
# ××—×¨××™×ª ×¢×œ ×›×œ ×¤×¢×•×œ×•×ª ×”DB ×”×§×©×•×¨×•×ª ×œ×¤×’×™×©×•×ª:
#   - CRUD ×ž×œ× (create/read/update/delete)
#   - ×—×™×¤×•×© ×œ×¤×™ UUID, ×ž×¡×¤×¨ ×¤×’×™×©×”, ××• ×ž×“×•×¨
#   - ×¢×“×›×•×Ÿ ×œ×¤×™ UUID ××• ×œ×¤×™ ×ž×¡×¤×¨ ×¤×’×™×©×”
# ============================================================================

import uuid

from .base import BaseRepository
from app.models.user import User
from app.models.group import Group

from app.schema.user import UserInCreate, UserInCreateNoRole, UserOutput
from app.schema.meeting import MeetingInCreate, MeetingInUpdate, MeetingOutput
from app.models.meeting import Meeting
from app.models.member_group_access import MemberGroupAccess


class MeetingRepository(BaseRepository):

    def create_meeting(self, meeting_data: MeetingInCreate) -> MeetingOutput:
        """ ×™×•×¦×¨ ×¤×’×™×©×” ×—×“×©×” ×‘DB """
        data = meeting_data.model_dump(exclude_none=True)

        new_meeting = Meeting(**data)

        self.session.add(new_meeting)
        self.session.commit()
        self.session.refresh(new_meeting)

        return new_meeting
    
    
    def delete_meeting(self, meeting_uuid: str) -> bool:
        """ ×ž×•×—×§ ×¤×’×™×©×” ×œ×¤×™ UUID. ×ž×—×–×™×¨ True ×× ×”×¦×œ×™×— """
        meeting = self.session.query(Meeting).filter(Meeting.UUID == meeting_uuid).first()
        if meeting:
            self.session.delete(meeting)
            self.session.commit()
            return True
        return False
    
    def get_meeting_by_uuid(self, meeting_uuid: str) -> MeetingOutput:
        """ ×ž×•×¦× ×¤×’×™×©×” ×œ×¤×™ UUID """
        meeting = self.session.query(Meeting).filter(Meeting.UUID == meeting_uuid).first()
        return meeting

    def user_can_access_meeting(self, user_uuid: str, meeting_uuid: str, user_role: str | None = None) -> bool:
        """
        ×‘×•×“×§ ×”×× ×œ×ž×©×ª×ž×© ×™×© ×’×™×©×” ×œ×¤×’×™×©×”:
        - ×”×ž×©×ª×ž×© ×¦×¨×™×š ×œ×”×™×•×ª ×—×‘×¨ ×‘×œ×¤×—×•×ª ×ž×“×•×¨ ××—×“ ×©×œ ×”×¤×’×™×©×”
        - ×•×‘××•×ª×• ×ž×“×•×¨ ×—×™×™×‘×ª ×œ×”×™×•×ª ×œ×• ×¨×ž×ª ×’×™×©×” ×©×ž×ª××™×ž×” ×œ×¡×•×’ ×”×¤×’×™×©×”
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

        # ×‘×“×™×§×ª ×—×‘×¨×•×ª ×‘×ž×“×•×¨
        user_group_uuids = {m.UUID for m in user.groups}

        # viewer ×¨×•××” ×›×œ ×¤×’×™×©×” ×‘×ž×“×•×¨×™× ×©×œ×• (×œ× ×œ×¤×™ access_level ×ž×“×•×™×§)
        if user_role == "viewer":
            return any(group.UUID in user_group_uuids for group in meeting.groups)

        meeting_level = getattr(meeting.accessLevel, "value", meeting.accessLevel)
        meeting_level = str(meeting_level).lower().strip()
        if meeting_level not in {"audio", "video", "blast_dial"}:
            return False

        for group in meeting.groups:
            if group.UUID not in user_group_uuids:
                continue

            # ×‘×“×™×§×ª ×”×¨×©××” ×‘××•×ª×• ×ž×“×•×¨
            for access_row in group.member_access_levels:
                if access_row.member_uuid != user.UUID:
                    continue

                access_level = getattr(access_row.access_level, "value", access_row.access_level)
                access_level = str(access_level).lower().strip()
                if access_level == meeting_level:
                    return True

        return False
    
    def get_all_meetings(self) -> list[MeetingOutput]:
        """ ×ž×—×–×™×¨ ××ª ×›×œ ×”×¤×’×™×©×•×ª ×‘×ž×¢×¨×›×ª """
        return self.session.query(Meeting).all()
    
    def get_meeting_by_number(self, number: int) -> MeetingOutput:
        """ ×ž×•×¦× ×¤×’×™×©×” ×œ×¤×™ ×ž×¡×¤×¨ ×”×¤×’×™×©×” (m_number) """
        meeting = self.session.query(Meeting).filter(Meeting.m_number == number).first()
        return meeting
    
    def get_meetings_by_group_uuid(self, group_uuid: str) -> list[str]:
        """ ×ž×—×–×™×¨ ×¨×©×™×ž×ª UUIDs ×©×œ ×¤×’×™×©×•×ª ×”×©×™×™×›×•×ª ×œ×ž×“×•×¨ """
        group = self.session.query(Group).filter(Group.UUID == group_uuid).first()
        if group:
            return [meeting.UUID for meeting in group.meetings]
        return []
    
    def update_meeting_by_number(self, meeting_number: str, meeting_data: MeetingInUpdate) -> MeetingOutput:
        """ ×ž×¢×“×›×Ÿ ×¤×’×™×©×” ×œ×¤×™ ×ž×¡×¤×¨ - ×¨×§ ×©×“×•×ª ×©× ×©×œ×—×• """
        meeting = self.session.query(Meeting).filter(Meeting.m_number == meeting_number).first()
        if not meeting:
            return None

        for key, value in meeting_data.model_dump(exclude_none=True).items():
            setattr(meeting, key, value)

        self.session.commit()
        self.session.refresh(meeting)
        return meeting
    
    def update_meeting_by_uuid(self, meeting_uuid: str, meeting_data: MeetingInUpdate) -> MeetingOutput:
        """ ×ž×¢×“×›×Ÿ ×¤×’×™×©×” ×œ×¤×™ UUID - ×¨×§ ×©×“×•×ª ×©× ×©×œ×—×• """
        meeting = self.session.query(Meeting).filter(Meeting.UUID == meeting_uuid).first()
        if not meeting:
            return None

        for key, value in meeting_data.model_dump(exclude_none=True).items():
            setattr(meeting, key, value)

        self.session.commit()
        self.session.refresh(meeting)
        return meeting
