from uuid import UUID
from app.repository.madorRepo import MadorRepository
from app.schema.user import MadorOutput, MadorBase
from fastapi import HTTPException


class MadorService:
    def __init__(self, session):
        self.__madorRepository = MadorRepository(session=session)

    def create_mador(self, mador_data: MadorBase, creator_id: UUID) -> MadorOutput:
        mador = self.__madorRepository.create_mador(name=mador_data.name, creator_id=creator_id)
        return MadorOutput.model_validate(mador, from_attributes=True)

    def list_madors(self) -> list[MadorOutput]:
        madors = self.__madorRepository.get_madors()
        return [MadorOutput.model_validate(m, from_attributes=True) for m in madors]

    def add_user_to_mador(self, mador_id: UUID, user_id: str, current_user_id: UUID) -> MadorOutput:
        mador = self.__madorRepository.get_mador_by_uuid(mador_id)
        if not mador:
            raise HTTPException(status_code=404, detail="Mador not found")
        
        if mador.creator_id != current_user_id:
            raise HTTPException(status_code=403, detail="Only mador creator can add members")
        
        mador = self.__madorRepository.add_user_to_mador(mador_id=mador_id, user_id=user_id)
        if not mador:
            raise HTTPException(status_code=404, detail="Mador or user not found")
        return MadorOutput.model_validate(mador, from_attributes=True)

    def remove_user_from_mador(self, mador_id: UUID, user_id: str, current_user_id: UUID) -> MadorOutput:
        mador = self.__madorRepository.get_mador_by_uuid(mador_id)
        if not mador:
            raise HTTPException(status_code=404, detail="Mador not found")
        
        if mador.creator_id != current_user_id:
            raise HTTPException(status_code=403, detail="Only mador creator can remove members")
        
        mador = self.__madorRepository.remove_user_from_mador(mador_id=mador_id, user_id=user_id)
        if not mador:
            raise HTTPException(status_code=404, detail="Mador or user not found")
        return MadorOutput.model_validate(mador, from_attributes=True)
