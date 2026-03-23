import { useEffect, useState } from "react";
import MeetingsPage from "../components/MeetingsPage";
import { madorAPI } from "../services/api";

const inferTypeFromMeetingId = (meetingId) => {
  const text = String(meetingId || "");
  if (text.startsWith("89")) return "audio";
  if (text.startsWith("77")) return "video";
  if (text.startsWith("55")) return "blast_dial";
  return "unknown";
};

export default function VideoMeetings() {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadMeetings = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await madorAPI.listMadors();
        const madors = response.data || [];

        const dbMeetings = madors.flatMap((mador) =>
          (mador.meetings || []).map((meeting) => ({
            id: `db-${meeting.id}`,
            dbId: meeting.id,
            meetingId: String(meeting.meeting_id),
            group: mador.name || "Unassigned",
            mador_id: meeting.mador_id,
            mador_owner_id: meeting.mador_owner_id,
            status: "",
          }))
        );

        setMeetings(dbMeetings.filter((meeting) => inferTypeFromMeetingId(meeting.meetingId) === "video"));
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load database video meetings.");
        setMeetings([]);
      } finally {
        setLoading(false);
      }
    };

    loadMeetings();
  }, []);

  return (
    <MeetingsPage
      title="Video Meetings"
      data={meetings}
      loading={loading}
      error={error}
    />
  );
}
