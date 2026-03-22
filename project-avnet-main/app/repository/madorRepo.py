import uuid

from .base import BaseRepository
from app.models.mador import Mador
from app.models.user import User


class MadorRepository(BaseRepository):
    def create_mador(self, name: str, creator_id: uuid.UUID) -> Mador:
        mador = Mador(name=name, creator_id=creator_id)
        self.session.add(mador)
        self.session.commit()
        self.session.refresh(mador)
        return mador

    def get_mador_by_uuid(self, mador_id: uuid.UUID) -> Mador | None:
        return self.session.query(Mador).filter_by(UUID=mador_id).first()

    def get_madors(self) -> list[Mador]:
        return self.session.query(Mador).all()

    def add_user_to_mador(self, mador_id: uuid.UUID, user_id: str) -> Mador | None:
        mador = self.get_mador_by_uuid(mador_id)
        if not mador:
            return None

        user = self.session.query(User).filter_by(s_id=user_id).first()
        if not user:
            return None

        if user not in mador.members:
            mador.members.append(user)
            self.session.commit()
            self.session.refresh(mador)

        return mador

    def remove_user_from_mador(self, mador_id: uuid.UUID, user_id: str) -> Mador | None:
        mador = self.get_mador_by_uuid(mador_id)
        if not mador:
            return None

        user = self.session.query(User).filter_by(s_id=user_id).first()
        if not user:
            return None

        if user in mador.members:
            mador.members.remove(user)
            self.session.commit()
            self.session.refresh(mador)

        return mador
