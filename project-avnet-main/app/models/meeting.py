from enum import Enum
import uuid
from sqlalchemy import UUID, Column, String, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from app.core.database import Base


class MeetingType(str, Enum):
    audio = "audio"
    video = "video"
    blast_dial = "blast_dial"


class Meeting(Base):
    __tablename__ = "Meetings"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    password = Column(String(250), nullable=False)
    type = Column(SqlEnum(MeetingType), nullable=False)
    mador_id = Column(UUID(as_uuid=True), ForeignKey("Madors.UUID"), nullable=False)

    mador = relationship("Mador", back_populates="meetings")