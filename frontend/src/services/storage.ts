import AsyncStorage from '@react-native-async-storage/async-storage';

export const storage = {
  // Save tokens
  async saveTokens(accessToken: string, refreshToken: string) {
    try {
      await AsyncStorage.setItem('access_token', accessToken);
      await AsyncStorage.setItem('refresh_token', refreshToken);
    } catch (error) {
      console.error('Error saving tokens:', error);
      throw error;
    }
  },

  // Get access token
  async getAccessToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('access_token');
    } catch (error) {
      console.error('Error getting access token:', error);
      return null;
    }
  },

  // Get refresh token
  async getRefreshToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem('refresh_token');
    } catch (error) {
      console.error('Error getting refresh token:', error);
      return null;
    }
  },

  // Clear all tokens (logout)
  async clearTokens() {
    try {
      await AsyncStorage.removeItem('access_token');
      await AsyncStorage.removeItem('refresh_token');
    } catch (error) {
      console.error('Error clearing tokens:', error);
      throw error;
    }
  },

  // Save user data
  async saveUser(user: any) {
    try {
      await AsyncStorage.setItem('user', JSON.stringify(user));
    } catch (error) {
      console.error('Error saving user:', error);
      throw error;
    }
  },

  // Get user data
  async getUser(): Promise<any | null> {
    try {
      const userData = await AsyncStorage.getItem('user');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error getting user:', error);
      return null;
    }
  },

  // Clear user data
  async clearUser() {
    try {
      await AsyncStorage.removeItem('user');
    } catch (error) {
      console.error('Error clearing user:', error);
      throw error;
    }
  },
};