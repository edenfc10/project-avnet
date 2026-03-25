// ============================================================================
// ProtectedRoute - שמירה על נתיבים מוגנים
// ============================================================================
// קומפוננטת עטיפה (wrapper) שמגינה על נתיבים שדורשים התחברות.
// אם המשתמש לא מחובר - מפנה אותו לדף ההתחברות (/login).
// אם המשתמש מחובר - מציג את התוכן של הדף המבוקש.
// משתמש ב-AuthContext כדי לבדוק מצב התחברות.
// ============================================================================

import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  // מציג loading בזמן שבודקים מצב התחברות
  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  // אם לא מחובר - מפנה לדף התחברות
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // מחובר - מציג את התוכן
  return children;
}
