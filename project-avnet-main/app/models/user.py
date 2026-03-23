from enum import Enum
import uuid
from sqlalchemy import Column, Integer, String, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.mador import user_mador_association
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

class UserRole(str, Enum):
    super_admin = "super_admin"
    admin = "admin"
    agent = "agent"


class User(Base):
    __tablename__ = "Users"

    UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    s_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(50), nullable=False)
    password = Column(String(250), nullable=False)
    role = Column(SqlEnum(UserRole), nullable=False, default=UserRole.admin)

    created_madors = relationship(
        "Mador",
        foreign_keys="Mador.creator_id",
        back_populates="creator",
        lazy="selectin",
    )

    madors = relationship(
        "Mador",
        secondary=user_mador_association,
        back_populates="members",
        lazy="selectin",
    )

    mador_access_levels = relationship(
        "MadorMemberAccess",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )



