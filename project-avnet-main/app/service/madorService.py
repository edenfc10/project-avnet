from uuid import UUID
from app.repository.madorRepo import MadorRepository
from app.schema.user import MadorOutput, MadorBase, MadorMemberAccessOutput, MadorMemberAccessUpdate
from fastapi import HTTPException


class MadorService:
    def __init__(self, session):
        self.__madorRepository = MadorRepository(session=session)

    def _role_value(self, role) -> str:
        return getattr(role, "value", role)

    def _can_manage_group(self, current_user_role) -> bool:
        return current_user_role in ("admin", "super_admin")

    def create_mador(self, mador_data: MadorBase, creator_id: UUID) -> MadorOutput:
        mador = self.__madorRepository.create_mador(name=mador_data.name, creator_id=creator_id)
        return MadorOutput.model_validate(mador, from_attributes=True)

    def list_madors(self, current_user_id: UUID, current_user_role) -> list[MadorOutput]:
        role = self._role_value(current_user_role)
        if role == "agent":
            madors = self.__madorRepository.get_madors_by_member(user_id=current_user_id)
        else:
            madors = self.__madorRepository.get_madors()
        return [MadorOutput.model_validate(m, from_attributes=True) for m in madors]

    def add_user_to_mador(self, mador_id: UUID, user_id: UUID, current_user_id: UUID, current_user_role) -> MadorOutput:
        mador = self.__madorRepository.get_mador_by_uuid(mador_id)
        if not mador:
            raise HTTPException(status_code=404, detail="Mador not found")

        if not self._can_manage_group(current_user_role):
            raise HTTPException(status_code=403, detail="Only admin or super_admin can add members")
        
        mador = self.__madorRepository.add_user_to_mador(mador_id=mador_id, user_id=user_id)
        if not mador:
            raise HTTPException(status_code=404, detail="Mador or user not found")
        return MadorOutput.model_validate(mador, from_attributes=True)

    def remove_user_from_mador(self, mador_id: UUID, user_id: UUID, current_user_id: UUID, current_user_role) -> MadorOutput:
        mador = self.__madorRepository.get_mador_by_uuid(mador_id)
        if not mador:
            raise HTTPException(status_code=404, detail="Mador not found")

        if not self._can_manage_group(current_user_role):
            raise HTTPException(status_code=403, detail="Only admin or super_admin can remove members")
        
        mador = self.__madorRepository.remove_user_from_mador(mador_id=mador_id, user_id=user_id)
        if not mador:
            raise HTTPException(status_code=404, detail="Mador or user not found")
        return MadorOutput.model_validate(mador, from_attributes=True)

    def update_member_access_level(
        self,
        mador_id: UUID,
        user_id: UUID,
        access_data: MadorMemberAccessUpdate,
        current_user_id: UUID,
        current_user_role,
    ) -> MadorMemberAccessOutput:
        mador = self.__madorRepository.get_mador_by_uuid(mador_id)
        if not mador:
            raise HTTPException(status_code=404, detail="Mador not found")

        if not self._can_manage_group(current_user_role):
            raise HTTPException(status_code=403, detail="Only admin or super_admin can update access levels")

        access_row = self.__madorRepository.update_user_access_level(
            mador_id=mador_id,
            user_id=user_id,
            access_level=access_data.access_level,
        )
        if not access_row:
            raise HTTPException(status_code=404, detail="Mador member not found")

        return MadorMemberAccessOutput.model_validate(access_row, from_attributes=True)

    def delete_mador(self, mador_id: UUID, current_user_role) -> bool:
        if not self._can_manage_group(current_user_role):
            raise HTTPException(status_code=403, detail="Only admin or super_admin can delete groups")

        deleted = self.__madorRepository.delete_mador(mador_id=mador_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Mador not found")

        return True
