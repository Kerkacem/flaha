import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const TOKEN_KEY = 'flaha_auth_token';
const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://10.0.2.2:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      AsyncStorage.removeItem(TOKEN_KEY);
    }
    return Promise.reject(err);
  },
);

export { TOKEN_KEY, API_BASE };
export default api;
