// ============================================================================
// Blastdial Meetings Page - ×“×£ ×™×©×™×‘×•×ª ×‘×œ××¡×˜×“×™×™×œ
// ============================================================================
// ×–×”×” ×œ-AudioMeetings ××‘×œ ×ž×¡× ×Ÿ ×œ×¤×™ ×¡×•×’ "blast_dial".
// ×ž×¢×‘×™×¨ ××ª ×”× ×ª×•× ×™× ×œ-MeetingsPage ×”×’× ×¨×™.
// ============================================================================

import { useEffect, useState } from "react";
import MeetingsPage from "../components/MeetingsPage";
import { groupAPI, meetingAPI } from "../services/api";

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

export default function BlastdialMeetings() {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadMeetings = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await groupAPI.listGroups();
        const groups = response.data || [];

        const dbMeetings = (
          await Promise.all(
            groups.flatMap((group) =>
              (group.meetings || []).map(async (meetingRef) => {
                if (meetingRef && typeof meetingRef === "object" && meetingRef.UUID) {
                  return {
                    id: `db-${meetingRef.UUID}`,
                    dbId: meetingRef.UUID,
                    meetingId: String(meetingRef.m_number || ""),
                    accessLevel: meetingRef.accessLevel || "",
                    password: meetingRef.password || "",
                    group: group.name || "Unassigned",
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
                    password: meeting.password || "",
                    group: group.name || "Unassigned",
                    status: "",
                  };
                } catch {
                  return null;
                }
              })
            )
          )
        ).filter(Boolean);

        setMeetings(dbMeetings.filter((meeting) => inferTypeFromMeeting(meeting) === "blast_dial"));
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load database blast dial meetings.");
        setMeetings([]);
      } finally {
        setLoading(false);
      }
    };

    loadMeetings();
  }, []);

  return (
    <MeetingsPage
      title="Blastdial Meetings"
      data={meetings}
      loading={loading}
      error={error}
    />
  );
}
