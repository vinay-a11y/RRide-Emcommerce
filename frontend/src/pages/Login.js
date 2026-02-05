import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

export default function Login() {
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    mobile: '',
    password: '',
    name: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        await login(formData.mobile, formData.password);
        toast.success('Login successful!');
      } else {
        await register(formData.mobile, formData.password, formData.name);
        toast.success('Registration successful!');
      }
      navigate('/');
    } catch (error) {
      console.error('Auth error:', error);
      toast.error(error.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4 py-24" data-testid="login-page">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-md"
      >
        <div className="backdrop-blur-xl bg-zinc-900/80 border border-zinc-800 rounded-lg p-8">
          <div className="text-center mb-8">
            <h1
              className="text-4xl font-bold text-white uppercase mb-2"
              style={{ fontFamily: 'Teko, sans-serif' }}
              data-testid="auth-title"
            >
              <span className="text-white">RRIDE</span>
              <span className="text-primary ml-1">GARAGE</span>
            </h1>
            <p className="text-zinc-400">{isLogin ? 'Welcome back!' : 'Create your account'}</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-white font-semibold mb-2">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 text-white rounded-sm focus:outline-none focus:border-primary transition-colors"
                  placeholder="Enter your name"
                  required={!isLogin}
                  data-testid="name-input"
                />
              </div>
            )}

            <div>
              <label className="block text-white font-semibold mb-2">Mobile Number</label>
              <input
                type="tel"
                value={formData.mobile}
                onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
                className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 text-white rounded-sm focus:outline-none focus:border-primary transition-colors"
                placeholder="Enter your mobile number"
                required
                data-testid="mobile-input"
              />
            </div>

            <div>
              <label className="block text-white font-semibold mb-2">Password</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 text-white rounded-sm focus:outline-none focus:border-primary transition-colors"
                placeholder="Enter your password"
                required
                data-testid="password-input"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-4 bg-primary text-black font-bold uppercase tracking-wider hover:bg-orange-400 transition-all skew-button disabled:opacity-50"
              data-testid="auth-submit-btn"
            >
              <span>{loading ? 'Processing...' : isLogin ? 'Login' : 'Register'}</span>
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-zinc-400 hover:text-primary transition-colors"
              data-testid="toggle-auth-mode-btn"
            >
              {isLogin ? "Don't have an account? Register" : 'Already have an account? Login'}
            </button>
          </div>

          <div className="mt-6 text-center">
            <button
              onClick={() => navigate('/')}
              className="text-zinc-400 hover:text-primary transition-colors text-sm"
              data-testid="continue-guest-btn"
            >
              Continue as Guest
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
