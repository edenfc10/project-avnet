// ============================================================================
// Video Meetings Page - דף ישיבות וידאו
// ============================================================================
// זהה ל-AudioMeetings אבל מסנן לפי סוג "video".
// מעביר את הנתונים ל-MeetingsPage הגנרי.
// ============================================================================

import { useEffect, useState } from "react";
import MeetingsPage from "../components/MeetingsPage";
import { madorAPI, meetingAPI } from "../services/api";

const inferTypeFromMeetingId = (meetingId) => {
  const text = String(meetingId || "");
  if (text.startsWith("89")) return "audio";
  if (text.startsWith("77")) return "video";
  if (text.startsWith("55")) return "blast_dial";
  return "unknown";
};

const inferTypeFromMeeting = (meeting) => {
  const accessLevel = String(meeting?.accessLevel || meeting?.type || "").toLowerCase();
  if (accessLevel === "audio" || accessLevel === "video" || accessLevel === "blast_dial") {
    return accessLevel;
  }
  return inferTypeFromMeetingId(meeting?.meetingId);
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

        const dbMeetings = (
          await Promise.all(
            madors.flatMap((mador) =>
              (mador.meetings || []).map(async (meetingRef) => {
                if (meetingRef && typeof meetingRef === "object" && meetingRef.UUID) {
                  return {
                    id: `db-${meetingRef.UUID}`,
                    dbId: meetingRef.UUID,
                    meetingId: String(meetingRef.m_number || ""),
                    accessLevel: meetingRef.accessLevel || "",
                    group: mador.name || "Unassigned",
                    status: "",
                  };
                }

                const meetingUuid = String(meetingRef || "").trim();
                if (!meetingUuid) {
                  return null;
                }

                try {
                  const meetingResponse = await meetingAPI.getMeeting(meetingUuid);
                  const meeting = meetingResponse.data;
                  return {
                    id: `db-${meeting.UUID}`,
                    dbId: meeting.UUID,
                    meetingId: String(meeting.m_number || ""),
                    accessLevel: meeting.accessLevel || "",
                    group: mador.name || "Unassigned",
                    status: "",
                  };
                } catch {
                  return null;
                }
              })
            )
          )
        ).filter(Boolean);

        setMeetings(dbMeetings.filter((meeting) => inferTypeFromMeeting(meeting) === "video"));
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
