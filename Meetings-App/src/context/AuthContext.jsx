import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

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

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
  