import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api, { TOKEN_KEY } from '../api/client';
import { Farmer, LoginResponse } from '../types';

interface AuthState {
  loading: boolean;
  farmer: Farmer | null;
  token: string | null;
}

interface AuthContextType extends AuthState {
  login: (phone: string, otp: string) => Promise<LoginResponse>;
  register: (phone: string, name: string, wilaya: string) => Promise<LoginResponse>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({ loading: true, farmer: null, token: null });

  useEffect(() => {
    (async () => {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      if (token) {
        setState((s) => ({ ...s, token }));
        try {
          const { data } = await api.get<Farmer>('/api/v1/auth/me');
          setState({ loading: false, farmer: data, token });
        } catch {
          await AsyncStorage.removeItem(TOKEN_KEY);
          setState({ loading: false, farmer: null, token: null });
        }
      } else {
        setState({ loading: false, farmer: null, token: null });
      }
    })();
  }, []);

  const login = useCallback(async (phone: string, otp: string) => {
    const { data } = await api.post<LoginResponse>('/api/v1/auth/login', { phone, otp });
    if (data.access_token) {
      await AsyncStorage.setItem(TOKEN_KEY, data.access_token);
      try {
        const { data: farmer } = await api.get<Farmer>('/api/v1/auth/me');
        setState({ loading: false, farmer, token: data.access_token });
      } catch {
        setState({ loading: false, farmer: null, token: data.access_token });
      }
    } else {
      setState((s) => ({ ...s, loading: false }));
    }
    return data;
  }, []);

  const register = useCallback(async (phone: string, name: string, wilaya: string) => {
    const { data } = await api.post<LoginResponse>('/api/v1/auth/register', { phone, name, wilaya });
    if (data.access_token) {
      await AsyncStorage.setItem(TOKEN_KEY, data.access_token);
      try {
        const { data: farmer } = await api.get<Farmer>('/api/v1/auth/me');
        setState({ loading: false, farmer, token: data.access_token });
      } catch {
        setState({ loading: false, farmer: null, token: data.access_token });
      }
    }
    return data;
  }, []);

  const logout = useCallback(async () => {
    await AsyncStorage.removeItem(TOKEN_KEY);
    setState({ loading: false, farmer: null, token: null });
  }, []);

  const refreshProfile = useCallback(async () => {
    try {
      const { data } = await api.get<Farmer>('/api/v1/auth/me');
      setState((s) => ({ ...s, farmer: data }));
    } catch {}
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
