import api from './api';
import { Plant, PlantDetail, PlantListResponse, Category } from '../types/plant';

export const plantService = {
  /**
   * Get paginated list of plants
   */
  async getPlants(page: number = 1, pageSize: number = 30): Promise<PlantListResponse> {
    try {
      const response = await api.get<PlantListResponse>('/plants/', {
        params: { page, page_size: pageSize }
      });
      return response.data;
    } catch (error: any) {
      console.error('Get plants error:', error.response?.data);
      throw error.response?.data || { error: 'Failed to fetch plants' };
    }
  },

  /**
   * Get detailed information about a specific plant
   */
  async getPlantById(plantId: number): Promise<PlantDetail> {
    try {
      const response = await api.get<PlantDetail>(`/plants/${plantId}/`);
      return response.data;
    } catch (error: any) {
      console.error('Get plant detail error:', error.response?.data);
      throw error.response?.data || { error: 'Failed to fetch plant details' };
    }
  },

  /**
   * Search plants by name (English or Urdu)
   */
  async searchPlants(query: string, page: number = 1): Promise<PlantListResponse> {
    try {
      const response = await api.get<PlantListResponse>('/plants/search/', {
        params: { q: query, page }
      });
      return response.data;
    } catch (error: any) {
      console.error('Search plants error:', error.response?.data);
      throw error.response?.data || { error: 'Failed to search plants' };
    }
  },

  /**
   * Filter plants by category
   */
  async filterByCategory(category: string, page: number = 1): Promise<PlantListResponse> {
    try {
      const response = await api.get<PlantListResponse>('/plants/filter/', {
        params: { category, page }
      });
      return response.data;
    } catch (error: any) {
      console.error('Filter plants error:', error.response?.data);
      throw error.response?.data || { error: 'Failed to filter plants' };
    }
  },

  /**
   * Get all available categories with counts
   */
  async getCategories(): Promise<Category[]> {
    try {
      const response = await api.get<{ categories: Category[] }>('/plants/categories/');
      return response.data.categories;
    } catch (error: any) {
      console.error('Get categories error:', error.response?.data);
      throw error.response?.data || { error: 'Failed to fetch categories' };
    }
  },
};