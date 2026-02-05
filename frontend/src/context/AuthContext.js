'use client'

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useRef,
} from "react";
import axios from "axios";

/* ================================
   CONFIG
================================ */
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

console.log("[v0] Backend URL:", API);

/* ================================
   AXIOS INSTANCE
================================ */
export const api = axios.create({
  baseURL: API,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  }
});

// ✅ FIXED: Interceptor NOW ADDS TOKEN TO EVERY REQUEST
api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem("token") : null;
  console.log("[v0] Axios Request - Token found:", !!token, "URL:", config.url);
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log("[v0] Added Authorization header");
  } else {
    console.log("[v0] No token - request will fail if endpoint needs auth");
  }
  return config;
});

// ✅ Response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log("[v0] Response success:", response.status, response.config.url);
    return response;
  },
  (error) => {
    console.log("[v0] Response error:", error.response?.status, error.response?.statusText, error.config?.url);
    return Promise.reject(error);
  }
);

/* ================================
   CONTEXT
================================ */
const AuthContext = createContext(undefined);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};

/* ================================
   PROVIDER
================================ */
export const AuthProvider = ({ children }) => {
  // ✅ Initialize token immediately from localStorage
  const [token, setToken] = useState(() => {
    if (typeof window !== "undefined") {
      try {
        return localStorage.getItem("token") || null;
      } catch {
        return null;
      }
    }
    return null;
  });
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  const hasFetched = useRef(false);

  /* 🔑 Restore session on reload */
  useEffect(() => {
    const initAuth = async () => {
      console.log("[v0] Auth initializing - token from localStorage:", !!token);
      
      if (!token) {
        setLoading(false);
        return;
      }

      // Verify token is still valid on first mount
      if (hasFetched.current) {
        setLoading(false);
        return;
      }
      
      hasFetched.current = true;
      setLoading(true);
      
      try {
        console.log("[v0] Verifying token with backend...");
        const res = await api.get("/auth/me");
        console.log("[v0] Token valid, user:", res.data);
        setUser(res.data);
      } catch (err) {
        console.warn("[v0] Token invalid:", err.response?.status, err.message);
        // Clear invalid token
        if (err.response?.status === 401) {
          if (typeof window !== "undefined") {
            localStorage.removeItem("token");
          }
          setToken(null);
          setUser(null);
        }
      } finally {
        setLoading(false);
      }
    };

    initAuth();
    // eslint-disable-next-line
  }, []);

  /* ================================
     LOGIN
  ================================ */
  const login = async (mobile, password) => {
    try {
      console.log("[v0] Starting login...");
      const res = await api.post("/auth/login", { mobile, password });
      
      const token = res.data.token;
      console.log("[v0] Login successful, token received");
      
      // ✅ Store immediately to localStorage BEFORE state updates
      if (typeof window !== "undefined") {
        localStorage.setItem("token", token);
        console.log("[v0] Token stored in localStorage");
      }
      
      setToken(token);
      setUser(res.data.user);
      hasFetched.current = true;
      
      return res.data.user;
    } catch (error) {
      console.error("[v0] Login failed:", error);
      throw error;
    }
  };

  /* ================================
     REGISTER
  ================================ */
  const register = async (mobile, password, name) => {
    const res = await api.post("/auth/register", {
      mobile,
      password,
      name,
    });
    const token = res.data.token;
    
    // ✅ Store immediately to localStorage BEFORE state updates
    if (typeof window !== "undefined") {
      localStorage.setItem("token", token);
      console.log("[v0] Token stored in localStorage after registration");
    }
    
    setToken(token);
    setUser(res.data.user);
    hasFetched.current = true;
    return res.data.user;
  };

  /* ================================
     LOGOUT
  ================================ */
  const logout = () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
    }
    setToken(null);
    setUser(null);
    hasFetched.current = false;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!token,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

