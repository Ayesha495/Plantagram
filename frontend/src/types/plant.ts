// Plant data structure matching our Django API

export interface Plant {
  id: number;
  name: string;
  name_urdu: string;
  scientific_name: string;
  category: string;
  care_level: 'Easy' | 'Medium' | 'Hard';
  image_url: string;
  is_beginner_friendly: boolean;
  is_popular: boolean;
}

export interface PlantDetail extends Plant {
  trefle_id: number | null;
  common_names: string | null;
  description: string;
  description_urdu: string;
  water_frequency_days: number;
  sunlight: string;
  temperature_min: number;
  temperature_max: number;
  humidity_level: string;
  care_tips: string;
  created_at: string;
  updated_at: string;
}

export interface PlantListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Plant[];
}

export interface Category {
  category: string;
  count: number;
}