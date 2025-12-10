import axios from 'axios';
import { Crop } from '../constants/crops';

const API_BASE_URL = 'https://tu-backend.com/api';

export interface RecommendationRequest {
  farmerId: string;
  crop: Crop;
  latitude: number;
  longitude: number;
  temperature: number;
  humidity: number;
  rainfall: number;
  ph: number;
}

export interface RecommendationResponse {
  recommendation: string;
  success: boolean;
}

export const getRecommendation = async (
  data: RecommendationRequest
): Promise<RecommendationResponse> => {
  try {
    const response = await axios.post<RecommendationResponse>(
      `${API_BASE_URL}/recommendation`,
      data,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.message || 
        'Error al obtener recomendación. Verifica tu conexión a internet.'
      );
    }
    throw new Error('Error al conectar con el servidor');
  }
};
