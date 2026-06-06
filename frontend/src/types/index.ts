export interface Farmer {
  id: string;
  name: string;
  phone: string;
  role: string;
  wilaya: string;
  commune?: string;
  rating_avg: number;
  total_transactions: number;
  is_verified: boolean;
  credit_score?: number;
  land_hectares?: number;
  crops?: string;
}

export interface Product {
  id: string;
  farmer_id: string;
  farmer_name: string;
  farmer_phone: string;
  farmer_rating: number;
  name: string;
  category: string;
  description?: string;
  quantity: number;
  unit: string;
  price: number;
  wilaya: string;
  status: string;
  is_organic: boolean;
  created_at: string;
}

export interface Transaction {
  id: string;
  product_name: string;
  seller_name: string;
  seller_phone: string;
  buyer_name: string;
  buyer_phone: string;
  quantity: number;
  total_price: number;
  commission: number;
  delivery_status: string;
  payment_status: string;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  farmer_id: string;
  name: string;
  is_new: boolean;
}

export interface AdvisoryResponse {
  query_id: string;
  response: string;
  confidence?: number;
  disease?: string;
  products?: string[];
}

export interface WeatherData {
  temperature: number;
  humidity: number;
  wind_speed: number;
  description: string;
  icon: string;
}

export interface GovProgram {
  code: string;
  name: string;
  description: string;
  type: string;
  eligibility: string;
  benefits: string;
}
