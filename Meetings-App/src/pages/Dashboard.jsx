// ============================================================================
// Dashboard Page - דף ראשי / לוח בקרה
// ============================================================================
// דף פשוט שמוצג למשתמש אחרי התחברות.
// כולל סקציות סטטיות (placeholder לפיתוח עתידי).
// ============================================================================

import './Dashboard.css';

export default function Dashboard() {
  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Welcome to Your Dashboard</h1>
        <p>Manage your meetings and settings with ease.</p>
      </header>

      <main className="dashboard-main">
        <section className="dashboard-section">
          <h2>Overview</h2>
          <p>Here you can find a quick summary of your activities.</p>
        </section>

        <section className="dashboard-section">
          <h2>Upcoming Meetings</h2>
          <p>Stay on top of your schedule with upcoming meetings.</p>
        </section>

        <section className="dashboard-section">
          <h2>Quick Actions</h2>
          <ul className="quick-actions">
            <li><button>Start a Meeting</button></li>
            <li><button>View Reports</button></li>
            <li><button>Manage Settings</button></li>
          </ul>
        </section>
      </main>
    </div>
  );
}
