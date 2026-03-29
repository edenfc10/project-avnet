
# ============================================================================
# GroupService - ×©×›×‘×ª ×œ×•×’×™×§×” ×¢×¡×§×™×ª ×œ×ž×“×•×¨×™×
# ============================================================================
# ×”×©×›×‘×” ×”×–×• ×ž×›×™×œ×” ××ª ×›×œ ×”×œ×•×’×™×§×” ×”×¢×¡×§×™×ª ×©×§×©×•×¨×” ×œ×ž×“×•×¨×™×:
#   - CRUD ×ž×“×•×¨×™×: ×™×¦×™×¨×”, ×§×¨×™××”, ×¢×“×›×•×Ÿ, ×ž×—×™×§×”
#   - × ×™×”×•×œ ×—×‘×¨×™×: ×”×•×¡×¤×” ×•×”×¡×¨×” ×¢× ×¨×ž×ª ×’×™×©×”
#   - × ×™×”×•×œ ×¤×’×™×©×•×ª: ×©×™×•×š ×¤×’×™×©×” ×œ×ž×“×•×¨
#   - ×”×ž×¨×” ×œ×¤×•×¨×ž×˜ ×¤×œ×˜: _to_output ×ž×ž×™×¨ ORM ×œ-Pydantic
#
# Pattern: Service Layer
#   ×ž×ª×•×•×š ×‘×™×Ÿ ×”Router ×œ×‘×™×Ÿ ×”Repository.
#   ×ž×•×¡×™×£ ×‘×“×™×§×•×ª ×•×–×¨×™×§×ª HTTPException ×‘×ž×§×¨×” ×©×œ ×©×’×™××”.
# ============================================================================

from typing import Dict

from sqlalchemy import String

from app.models.user import User
from app.repository.groupRepo import GroupRepository
from app.schema.user import GroupInCreate, GroupOutput, UserInCreateNoRole, UserJWTData, UserOutput, UserInCreate, UserInLogin, UserToken, UserWithToken, MemberAccessOutput
from app.models.member_group_access import MemberGroupAccessLevel
from app.security.hashHelper import HashHelp
from app.security.auth import AuthHand
from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid


class GroupService:
    def __init__(self, session):
        self.__groupRepository = GroupRepository(session=session)  # ×ž×•×¤×¢ ×”×¨×¤×•×–×™×˜×•×¨×™
        self.session = session

    def _to_output(self, group) -> GroupOutput:
        """
        ×ž×ž×™×¨ ORM object ×©×œ ×ž×“×•×¨ ×œ-Pydantic GroupOutput.
        ×ž×ž×™×¨ ××ª ×”×—×‘×¨×™× ×•×”×¤×’×™×©×•×ª ×œ×¨×©×™×ž×•×ª UUID ×‘×œ×‘×“,
        ×•×’× ×ž×ž×™×¨ ××ª ×¨×ž×•×ª ×”×’×™×©×” ×œ×¤×•×¨×ž×˜ MemberAccessOutput.
        """
        return GroupOutput(
            UUID=group.UUID,
            name=group.name,
            members=[m.UUID for m in group.members],
            meetings=[m.UUID for m in group.meetings],
            member_access_levels=[
                MemberAccessOutput(user_id=row.member_uuid, access_level=row.access_level)
                for row in group.member_access_levels
            ],
        )

    def create_group(self, group_data: GroupInCreate) -> GroupOutput:
        return self._to_output(self.__groupRepository.create_group(group_data=group_data))
    
    def get_all_groups(self) -> list[GroupOutput]:
        return [self._to_output(m) for m in self.__groupRepository.get_all_groups()]

    def get_groups_by_user_uuid(self, user_uuid: str) -> list[GroupOutput]:
        """ ×ž×—×–×™×¨ ×¨×§ ××ª ×”×ž×“×•×¨×™× ×©×œ ×”×ž×©×ª×ž×© ×”×ž×—×•×‘×¨ """
        return [self._to_output(m) for m in self.__groupRepository.get_groups_by_user_uuid(user_uuid=user_uuid)]
    
    def get_group_by_uuid(self, group_uuid: str) -> GroupOutput:
        group = self.__groupRepository.get_group_by_uuid(group_uuid=group_uuid)
        if group:
            return self._to_output(group)
        raise HTTPException(status_code=400, detail="Group is not available")

    def delete_group(self, group_uuid: str) -> bool:
        if self.__groupRepository.delete_group(group_uuid=group_uuid):
            return True
        raise HTTPException(status_code=400, detail="Group is not available")
    
    def update_group(self, group_uuid: str, group_data: GroupInCreate) -> GroupOutput:
        group = self.__groupRepository.update_group(group_uuid=group_uuid, group_data=group_data)
        if group:
            return self._to_output(group)
        raise HTTPException(status_code=400, detail="Group is not available")

    def add_member_to_group(self, group_uuid: str, user_s_id: str, access_level: MemberGroupAccessLevel) -> GroupOutput:
        """
        ×ž×•×¡×™×£ ×—×‘×¨ ×œ×ž×“×•×¨ ×¢× ×¨×ž×ª ×’×™×©×”.
        ×ž×¢×‘×™×¨ ××ª access_level ×“×¨×š ×›×œ ×”×©×¨×©×¨×ª ×¢×“ ×”DB.
        """
        group = self.__groupRepository.add_member_to_group(
            group_uuid=group_uuid,
            user_s_id=user_s_id,
            access_level=access_level,
        )
        if group:
            return self._to_output(group)
        raise HTTPException(status_code=400, detail="Group or User is not available")
    
    def remove_member_from_group(self, group_uuid: str, user_s_id: str) -> GroupOutput:
        group = self.__groupRepository.remove_member_from_group(group_uuid=group_uuid, user_s_id=user_s_id)
        if group:
            return self._to_output(group)
        raise HTTPException(status_code=400, detail="Group or User is not available")

    def add_meeting_to_group(self, group_uuid: str, meeting_uuid: str) -> GroupOutput:
        group = self.__groupRepository.add_meeting_to_group_by_uuid(group_uuid=group_uuid, meeting_uuid=meeting_uuid)
        if group:
            return self._to_output(group)
        raise HTTPException(status_code=400, detail="Group or Meeting is not available")
