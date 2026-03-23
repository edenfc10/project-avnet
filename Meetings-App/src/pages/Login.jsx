import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './Login.css';

export default function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    s_id: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      navigate('/dashboard', { replace: true });
    }
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const { login} = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log('Attempting login with:', formData);
      console.log('API URL:', import.meta.env.VITE_API_URL || 'http://localhost:8000');
      
      const response = await authAPI.login(formData);
      
      console.log('Login successful:', response);
      
      await login(response.data.token);
      
      // Redirect to dashboard
      navigate('/dashboard', { replace: true });
    } catch (err) {
      console.error('Full error:', err);
      console.error('Error response:', err.response);
      
      const errorMessage = err.response?.data?.detail || 
                          err.message || 
                          'Login failed. Please check your connection and credentials.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Meet Manager</h1>
        <p className="login-subtitle">Sign in to your account</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="s_id">S_ID</label>
            <input
              type="text"
              id="s_id"
              name="s_id"
              value={formData.s_id}
              onChange={handleChange}
              placeholder="Enter your S_ID"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
            />
          </div>

          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="login-help">
          Need help? Contact your administrator.
        </p>
      </div>
    </div>
  );
}
