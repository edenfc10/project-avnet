from app.repository.meetingRepo import MeetingRepository
from app.schema.user import MeetingOutput, MeetingBase
from fastapi import HTTPException


class MeetingService:
    def __init__(self, session):
        self.__meetingRepository = MeetingRepository(session=session)

    def create_meeting(self, meeting_data: MeetingBase, mador_id: int) -> MeetingOutput:
        meeting = self.__meetingRepository.create_meeting(
            name=meeting_data.name, password=meeting_data.password, type=meeting_data.type.value, mador_id=mador_id
        )
        return MeetingOutput.model_validate(meeting, from_attributes=True)

    def get_meetings_by_mador(self, mador_id: int) -> list[MeetingOutput]:
        meetings = self.__meetingRepository.get_meetings_by_mador(mador_id=mador_id)
        return [MeetingOutput.model_validate(m, from_attributes=True) for m in meetings]