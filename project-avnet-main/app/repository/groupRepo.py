# ============================================================================
# GroupRepository - ×©×›×‘×ª ×’×™×©×” ×œ× ×ª×•× ×™× ×©×œ ×ž×“×•×¨×™×
# ============================================================================
# ××—×¨××™×ª ×¢×œ ×›×œ ×¤×¢×•×œ×•×ª ×”DB ×©×§×©×•×¨×•×ª ×œ×ž×“×•×¨×™×:
#   - CRUD ×ž×œ× (create/read/update/delete)
#   - × ×™×”×•×œ ×—×‘×¨×™×: ×”×•×¡×¤×”, ×”×¡×¨×”, ×¢×“×›×•×Ÿ ×¨×ž×ª ×’×™×©×”
#   - × ×™×”×•×œ ×¤×’×™×©×•×ª: ×©×™×•×š ×¤×’×™×©×” ×œ×ž×“×•×¨
#
# ×ª×”×œ×™×š ×”×•×¡×¤×ª ×—×‘×¨:
#   1. ×‘×•×“×§ ×©×”×ž×“×•×¨ ×•×”×ž×©×ª×ž×© ×§×™×™×ž×™×
#   2. ×× ×”×ž×©×ª×ž×© ×œ× ×—×‘×¨, ×ž×•×¡×™×£ ××•×ª×• ×œ×ž×“×•×¨
#   3. ×ž×•×—×§ ×¨×©×•×ž×ª ×’×™×©×” ×™×©× ×” (×× ×§×™×™×ž×ª) ×•×ž×•×¡×™×£ ×—×“×©×”
# ============================================================================

from .base import BaseRepository
import uuid
from app.models.user import User
from app.models.group import Group
from app.models.meeting import Meeting
from app.models.member_group_access import MemberGroupAccess, MemberGroupAccessLevel
from app.schema.user import GroupInCreate, GroupInUpdate, GroupOutput


class GroupRepository(BaseRepository):

    def create_group(self, group_data: GroupInCreate) -> GroupOutput:
        """ ×™×•×¦×¨ ×ž×“×•×¨ ×—×“×© ×‘DB """
        data = group_data.model_dump(exclude_none=True)
        new_group = Group(**data)

        self.session.add(new_group)
        self.session.commit()
        self.session.refresh(new_group)
        return new_group

    def get_all_groups(self) -> list[GroupOutput]:
        """ ×ž×—×–×™×¨ ××ª ×›×œ ×”×ž×“×•×¨×™× """
        return self.session.query(Group).all()

    def get_groups_by_user_uuid(self, user_uuid: str) -> list[GroupOutput]:
        """ ×ž×—×–×™×¨ ×¨×§ ××ª ×”×ž×“×•×¨×™× ×©×”×ž×©×ª×ž×© ×©×™×™×š ××œ×™×”× """
        try:
            normalized_user_uuid = uuid.UUID(str(user_uuid))
        except (ValueError, TypeError):
            return []

        user = self.session.query(User).filter(User.UUID == normalized_user_uuid).first()
        if not user:
            return []
        return list(user.groups)

    def get_group_by_uuid(self, group_uuid: str) -> GroupOutput:
        """ ×ž×•×¦× ×ž×“×•×¨ ×œ×¤×™ UUID """
        return self.session.query(Group).filter(Group.UUID == group_uuid).first()

    def delete_group(self, group_uuid: str) -> bool:
        """ ×ž×•×—×§ ×ž×“×•×¨ ×œ×¤×™ UUID. ×ž×—×–×™×¨ True ×× ×”×¦×œ×™×— """
        group = self.session.query(Group).filter(Group.UUID == group_uuid).first()
        if group:
            self.session.delete(group)
            self.session.commit()
            return True
        return False

    def update_group(self, group_uuid: str, group_data: GroupInUpdate) -> GroupOutput:
        """ ×ž×¢×“×›×Ÿ ×¤×¨×˜×™ ×ž×“×•×¨ (×œ×ž×©×œ ×©×) - ×¨×§ ×©×“×•×ª ×©× ×©×œ×—×• """
        group = self.session.query(Group).filter(Group.UUID == group_uuid).first()
        if not group:
            return None

        for key, value in group_data.model_dump(exclude_none=True).items():
            setattr(group, key, value)

        self.session.commit()
        self.session.refresh(group)
        return group

    def add_member_to_group(
        self,
        group_uuid: str,
        user_s_id: str,
        access_level: MemberGroupAccessLevel,
    ) -> GroupOutput:
        """
        ×ž×•×¡×™×£ ×—×‘×¨ ×œ×ž×“×•×¨ ×¢× ×¨×ž×ª ×’×™×©×” ×ž×¡×•×™×ž×ª.
        ×× ×”×—×‘×¨ ×›×‘×¨ ×§×™×™× - ×ž×•×¡×™×£ ×¨×ž×ª ×’×™×©×” × ×•×¡×¤×ª (×œ×œ× ×ž×—×™×§×” ×©×œ ×”×§×™×™×ž×•×ª).
        """
        group = self.session.query(Group).filter(Group.UUID == group_uuid).first()
        user = self.session.query(User).filter(User.s_id == user_s_id).first()

        if not group or not user:
            return None

        # ×× ×”×ž×©×ª×ž×© ×œ× ×—×‘×¨ ×¢×“×™×™×Ÿ - ×ž×•×¡×™×£ ××•×ª×• ×œ×ž×“×•×¨
        if user not in group.members:
            group.members.append(user)

        # ×× ×¨×ž×ª ×”×’×™×©×” ×›×‘×¨ ×§×™×™×ž×ª - ×œ× ×ž×•×¡×™×¤×™× ×›×¤×™×œ×•×ª.
        existing = self.session.query(MemberGroupAccess).filter(
            MemberGroupAccess.member_uuid == user.UUID,
            MemberGroupAccess.group_uuid == group.UUID,
            MemberGroupAccess.access_level == access_level,
        ).first()

        if not existing:
            self.session.add(
                MemberGroupAccess(
                    member_uuid=user.UUID,
                    group_uuid=group.UUID,
                    access_level=access_level,
                )
            )

        self.session.commit()
        self.session.refresh(group)
        return group

    def remove_member_from_group(self, group_uuid: str, user_s_id: str) -> GroupOutput:
        """
        ×ž×¡×™×¨ ×—×‘×¨ ×ž×”×ž×“×•×¨.
        ×’× ×ž×•×—×§ ××ª ×¨×©×•×ž×ª ×”×’×™×©×” ×©×œ×• ×ž×”×˜×‘×œ×” member_group_access.
        """
        group = self.session.query(Group).filter(Group.UUID == group_uuid).first()
        user = self.session.query(User).filter(User.s_id == user_s_id).first()

        if not group or not user:
            return None

        if user in group.members:
            group.members.remove(user)
            self.session.query(MemberGroupAccess).filter(
                MemberGroupAccess.member_uuid == user.UUID,
                MemberGroupAccess.group_uuid == group.UUID,
            ).delete()
            self.session.commit()
            self.session.refresh(group)

        return group

    def add_meeting_to_group_by_uuid(self, group_uuid: str, meeting_uuid: str) -> GroupOutput:
        """
        ×ž×©×™×™×š ×¤×’×™×©×” ×œ×ž×“×•×¨ (×œ×¤×™ UUID ×©×œ ×©× ×™×”×).
        ×ž×•× ×¢ ×›×¤×™×œ×•×™×•×ª - ×œ× ×ž×•×¡×™×£ ×× ×”×¤×’×™×©×” ×›×‘×¨ ×©×™×™×›×ª.
        """
        group = self.session.query(Group).filter(Group.UUID == group_uuid).first()
        meeting = self.session.query(Meeting).filter(Meeting.UUID == meeting_uuid).first()

        if not group or not meeting:
            return None

        if meeting not in group.meetings:
            group.meetings.append(meeting)

        self.session.commit()
        self.session.refresh(group)
        return group


