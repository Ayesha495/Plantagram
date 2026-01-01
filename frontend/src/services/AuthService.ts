import api from './api';
import { storage } from './storage';

// Type definitions
export interface SignupData {
  username: string;
  email: string;
  password: string;
  password2: string;
  location?: string;
  language_preference?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  tokens: {
    access: string;
    refresh: string;
  };
}

export interface User {
  id: number;
  username: string;
  email: string;
  profile_picture: string | null;
  location: string | null;
  language_preference: string;
  streak_count: number;
  total_petal_points: number;
  league: string;
  created_at: string;
}

export const authService = {
  // Signup
  async signup(data: SignupData): Promise<AuthResponse> {
    try {
      const response = await api.post<AuthResponse>('/auth/signup/', data);
      
      // Save tokens and user data
      await storage.saveTokens(
        response.data.tokens.access,
        response.data.tokens.refresh
      );
      await storage.saveUser(response.data.user);
      
      return response.data;
    } catch (error: any) {
      console.error('Signup error:', error.response?.data);
      throw error.response?.data || { error: 'Signup failed' };
    }
  },

  // Login
  async login(data: LoginData): Promise<AuthResponse> {
    try {
      const response = await api.post<AuthResponse>('/auth/login/', data);
      
      // Save tokens and user data
      await storage.saveTokens(
        response.data.tokens.access,
        response.data.tokens.refresh
      );
      await storage.saveUser(response.data.user);
      
      return response.data;
    } catch (error: any) {
      console.error('Login error:', error.response?.data);
      throw error.response?.data || { error: 'Login failed' };
    }
  },

  // Get current user profile
  async getProfile(): Promise<User> {
    try {
      const response = await api.get<User>('/auth/profile/');
      await storage.saveUser(response.data);
      return response.data;
    } catch (error: any) {
      console.error('Get profile error:', error.response?.data);
      throw error.response?.data || { error: 'Failed to get profile' };
    }
  },

  // Logout
  async logout() {
    try {
      await storage.clearTokens();
      await storage.clearUser();
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },

  // Check if user is logged in
  async isAuthenticated(): Promise<boolean> {
    const token = await storage.getAccessToken();
    return !!token;
  },
};