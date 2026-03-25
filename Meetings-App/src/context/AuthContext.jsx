// ============================================================================
// AuthContext - ניהול מצב ההתחברות של המשתמש
// ============================================================================
// Context גלובלי שמנהל:
//   - isAuthenticated: האם המשתמש מחובר
//   - userRole: תפקיד המשתמש (super_admin / admin / agent)
//   - currentUser: אובייקט המשתמש המלא מהשרת
//   - loading: האם טוען מצב התחברות
//   - login(token): שומר טוקן ומביא פרטי משתמש
//   - logout(): מנקה טוקן ומאפס מצב
//
// זרימת עבודה:
//   1. בטעינה - בודק אם יש token ב-localStorage
//   2. אם כן - שולח בקשה ל-/protected/me לאימות
//   3. אם תקין - שומר תפקיד ופרטי משתמש
//   4. אם לא תקין - מבצע logout
// ============================================================================

import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // בטעינה ראשונה - בודק אם יש token קיים ואם הוא תקין
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const resp = await authAPI.protected();
        const roleFromServer = resp.data?.user?.role || null;

        if (resp.status === 200 && roleFromServer) {
          setIsAuthenticated(true);
          setCurrentUser(resp.data?.user || null);
          setUserRole(roleFromServer);
        } else {
          logout();
        }
      } catch {
        logout();
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // פונקציית התחברות - שומרת token ומביאה פרטי משתמש מהשרת
  const login = async (token) => {
    localStorage.setItem('token', token);

    try {
      const resp = await authAPI.protected();
      const roleFromServer = resp.data?.user?.role || null;

      if (resp.status === 200 && roleFromServer) {
        setIsAuthenticated(true);
        setUserRole(roleFromServer);
        setCurrentUser(resp.data?.user || null);
      } else {
        logout();
      }
    } catch {
      logout();
    }
  };

  // פונקציית התנתקות - מנקה הכל
  const logout = () => {
    console.log('Logging out user');
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setUserRole(null);
    setCurrentUser(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, userRole, currentUser, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook נוח לשימוש ב-context - חייב להיות בתוך AuthProvider
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
  