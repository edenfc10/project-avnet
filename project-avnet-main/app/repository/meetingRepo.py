import uuid
from .base import BaseRepository
from app.models.meeting import Meeting, MeetingType


class MeetingRepository(BaseRepository):
    def create_meeting(self, name: str, password: str, type: MeetingType, mador_id) -> Meeting:
        meeting = Meeting(name=name, password=password, type=type, mador_id=mador_id)
        self.session.add(meeting)
        self.session.commit()
        self.session.refresh(meeting)
        return meeting

    def get_meeting_by_id(self, meeting_id) -> Meeting | None:
        return self.session.query(Meeting).filter_by(id=meeting_id).first()

    def get_meetings_by_mador(self, mador_id) -> list[Meeting]:
        return self.session.query(Meeting).filter_by(mador_id=mador_id).all()