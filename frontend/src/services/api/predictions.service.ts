import { AIPredictionsData, RiskPrediction } from '@/types/predictions';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class PredictionsService {
  private static instance: PredictionsService;

  private constructor() {}

  public static getInstance(): PredictionsService {
    if (!PredictionsService.instance) {
      PredictionsService.instance = new PredictionsService();
    }
    return PredictionsService.instance;
  }

  /**
   * Fetch AI-powered predictions for all monitored areas
   */
  async getAllPredictions(): Promise<AIPredictionsData> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/predictions/all`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        cache: 'no-store', // Always get fresh predictions
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch predictions:', error);
      throw error;
    }
  }

  /**
   * Fetch prediction for specific location
   */
  async getPredictionByLocation(
    state: string,
    lga?: string
  ): Promise<RiskPrediction> {
    try {
      const params = new URLSearchParams({ state });
      if (lga) params.append('lga', lga);

      const response = await fetch(
        `${API_BASE_URL}/api/predictions/location?${params}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch location prediction:', error);
      throw error;
    }
  }

  /**
   * Get explainability data for a prediction
   */
  async getExplainability(predictionId: string): Promise<{
    contributingFactors: Array<{ factor: string; weight: number }>;
    similarHistoricalEvents: Array<{ date: string; outcome: string; similarity: number }>;
    modelDetails: {
      algorithm: string;
      features: string[];
      accuracy: number;
    };
  }> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/predictions/${predictionId}/explain`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch explainability:', error);
      throw error;
    }
  }

  /**
   * Run scenario simulation
   */
  async runScenario(scenarioParams: {
    location: string;
    variables: Record<string, number>;
  }): Promise<{
    predictedRisk: number;
    confidence: number;
    impactAnalysis: string;
  }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/predictions/scenario`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(scenarioParams),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to run scenario:', error);
      throw error;
    }
  }
}

export const predictionsService = PredictionsService.getInstance();
