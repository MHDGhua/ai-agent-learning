import React, { createContext, useContext, useState, useCallback } from 'react';
import type { UserInfo } from '@/types';

interface AuthState {
  user: UserInfo | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: UserInfo, token: string) => void;
  logout: () => void;
  updateUser: (updates: Partial<UserInfo>) => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserInfo | null>(() => {
    const stored = localStorage.getItem('lerap_user');
    return stored ? JSON.parse(stored) : null;
  });
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('lerap_token');
  });

  const login = useCallback((userInfo: UserInfo, authToken: string) => {
    setUser(userInfo);
    setToken(authToken);
    localStorage.setItem('lerap_user', JSON.stringify(userInfo));
    localStorage.setItem('lerap_token', authToken);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('lerap_user');
    localStorage.removeItem('lerap_token');
  }, []);

  const updateUser = useCallback((updates: Partial<UserInfo>) => {
    setUser(prev => {
      if (!prev) return prev;
      const updated = { ...prev, ...updates };
      localStorage.setItem('lerap_user', JSON.stringify(updated));
      return updated;
    });
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!user, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthState => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
