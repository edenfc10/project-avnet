import uuid

from sqlalchemy import UUID, Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

user_mador_association = Table(
    "user_mador_association",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("Users.UUID"), primary_key=True),
    Column("mador_id", UUID(as_uuid=True), ForeignKey("Madors.UUID"), primary_key=True),
)


class Mador(Base):
    __tablename__ = "Madors"

    UUID = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), unique=True, nullable=False)
    creator_id = Column(PostgresUUID(as_uuid=True), ForeignKey("Users.UUID"), nullable=False)

    creator = relationship(
        "User",
        foreign_keys=[creator_id],
        back_populates="created_madors",
        lazy="selectin",
    )

    members = relationship(
        "User",
        secondary=user_mador_association,
        back_populates="madors",
        lazy="selectin",
    )

    member_access_levels = relationship(
        "MadorMemberAccess",
        back_populates="mador",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    meetings = relationship(
        "Meeting",
        back_populates="mador",
        lazy="selectin",
    )


class MadorMemberAccess(Base):
    __tablename__ = "MadorMemberAccess"

    user_id = Column(PostgresUUID(as_uuid=True), ForeignKey("Users.UUID"), primary_key=True)
    mador_id = Column(PostgresUUID(as_uuid=True), ForeignKey("Madors.UUID"), primary_key=True)
    access_level = Column(String(20), nullable=False, default="standard")

    user = relationship("User", back_populates="mador_access_levels", lazy="selectin")
    mador = relationship("Mador", back_populates="member_access_levels", lazy="selectin")
