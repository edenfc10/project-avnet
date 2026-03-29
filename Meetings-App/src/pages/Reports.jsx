// ============================================================================
// Reports Page - ×“×£ ×“×•×—×•×ª / KPI
// ============================================================================
// ×ž×¦×™×’ ×¡×˜×˜×™×¡×˜×™×§×•×ª ×ž×”×™×¨×•×ª:
//   - ×ž×¡×¤×¨ ×ž×©×ª×ž×©×™×, ×ž×“×•×¨×™×, ×™×©×™×‘×•×ª, ×—×‘×¨×•×™×•×ª
//   - ×¡×§×™×¨×ª ×¤×¢×™×œ×•×ª ×œ×›×œ ×ž×“×•×¨
// ×˜×•×¢×Ÿ ××ª ×”× ×ª×•× ×™× ×ž-userAPI ×•-groupAPI ×‘×ž×§×‘×™×œ.
// ============================================================================

import { useEffect, useMemo, useState } from "react";
import { groupAPI, userAPI } from "../services/api";

export default function Reports() {
  const [users, setUsers] = useState([]);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadReportData = async () => {
      try {
        setLoading(true);
        setError("");

        const [usersResponse, groupsResponse] = await Promise.all([
          userAPI.getAllUsers(),
          groupAPI.listGroups(),
        ]);

        setUsers(usersResponse.data || []);
        setGroups(groupsResponse.data || []);
      } catch (err) {
        const message = err.response?.data?.detail || "Failed to load report data.";
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    loadReportData();
  }, []);

  const totalMeetings = useMemo(
    () => groups.reduce((sum, group) => sum + (group.meetings?.length || 0), 0),
    [groups]
  );

  const totalMembers = useMemo(
    () => groups.reduce((sum, group) => sum + (group.members?.length || 0), 0),
    [groups]
  );

  return (
    <div className="page">
      <h2 className="page-header">Reports</h2>

      {loading ? <div className="card"><div className="empty-state">Loading report data...</div></div> : null}
      {error ? <div className="error-banner">{error}</div> : null}

      {!loading && !error ? (
        <>
          <div className="kpi-grid">
            <div className="kpi-card">
              <div className="kpi-label">Users</div>
              <div className="kpi-value">{users.length}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Groups</div>
              <div className="kpi-value">{groups.length}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Meetings</div>
              <div className="kpi-value">{totalMeetings}</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">Group Memberships</div>
              <div className="kpi-value">{totalMembers}</div>
            </div>
          </div>

          <div className="card fill">
            <h3 className="card-title">Group Activity Snapshot</h3>
            <div className="meetings-list">
              {groups.length === 0 ? (
                <div className="empty-state">No groups found.</div>
              ) : (
                groups.map((group) => (
                  <div key={group.id} className="meeting-row">
                    <div>
                      <div className="meeting-title">{group.name}</div>
                      <div className="meeting-meta">
                        Members: {group.members?.length || 0} â€¢ Meetings: {group.meetings?.length || 0}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}

