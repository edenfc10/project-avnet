import uuid
from sqlalchemy import delete

from .base import BaseRepository
from app.models.mador import Mador, MadorMemberAccess, user_mador_association
from app.models.meeting import Meeting
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

    def get_madors_by_member(self, user_id: uuid.UUID) -> list[Mador]:
        return (
            self.session.query(Mador)
            .join(Mador.members)
            .filter(User.UUID == user_id)
            .all()
        )

    def add_user_to_mador(self, mador_id: uuid.UUID, user_id: uuid.UUID) -> Mador | None:
        mador = self.get_mador_by_uuid(mador_id)
        if not mador:
            return None

        user = self.session.query(User).filter_by(UUID=user_id).first()
        if not user:
            return None

        if user not in mador.members:
            mador.members.append(user)

        access = self.session.query(MadorMemberAccess).filter_by(mador_id=mador_id, user_id=user_id).first()
        if not access:
            self.session.add(MadorMemberAccess(mador_id=mador_id, user_id=user_id, access_level="audio"))

        self.session.commit()
        self.session.refresh(mador)

        return mador

    def remove_user_from_mador(self, mador_id: uuid.UUID, user_id: uuid.UUID) -> Mador | None:
        mador = self.get_mador_by_uuid(mador_id)
        if not mador:
            return None

        user = self.session.query(User).filter_by(UUID=user_id).first()
        if not user:
            return None

        if user in mador.members:
            mador.members.remove(user)
            self.session.query(MadorMemberAccess).filter_by(mador_id=mador_id, user_id=user_id).delete()
            self.session.commit()
            self.session.refresh(mador)

        return mador

    def update_user_access_level(self, mador_id: uuid.UUID, user_id: uuid.UUID, access_level: str) -> MadorMemberAccess | None:
        mador = self.get_mador_by_uuid(mador_id)
        if not mador:
            return None

        user = self.session.query(User).filter_by(UUID=user_id).first()
        if not user:
            return None

        if user not in mador.members:
            return None

        row = self.session.query(MadorMemberAccess).filter_by(mador_id=mador_id, user_id=user_id).first()
        if not row:
            row = MadorMemberAccess(mador_id=mador_id, user_id=user_id, access_level=access_level)
            self.session.add(row)
        else:
            row.access_level = access_level

        self.session.commit()
        self.session.refresh(row)
        return row

    def delete_mador(self, mador_id: uuid.UUID) -> bool:
        mador = self.get_mador_by_uuid(mador_id)
        if not mador:
            return False

        self.session.query(Meeting).filter_by(mador_id=mador_id).delete(synchronize_session=False)
        self.session.query(MadorMemberAccess).filter_by(mador_id=mador_id).delete(synchronize_session=False)
        self.session.execute(
            delete(user_mador_association).where(user_mador_association.c.mador_id == mador_id)
        )
        self.session.delete(mador)
        self.session.commit()
        return True
