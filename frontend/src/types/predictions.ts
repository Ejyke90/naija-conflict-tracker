export interface RiskPrediction {
  lga: string;
  state: string;
  currentRisk: number;
  predicted7Day: number;
  predicted14Day: number;
  predicted30Day: number;
  confidence: number;
  trendDirection: 'increasing' | 'decreasing' | 'stable';
  lastUpdated: string;
}

export interface ContributingFactor {
  name: string;
  weight: number;
  category: 'historical' | 'current' | 'environmental' | 'social' | 'political';
}

export interface Alert {
  id: string;
  location: string;
  message: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  confidence: number;
  timestamp: string;
  type: 'escalation' | 'new_activity' | 'pattern' | 'anomaly';
}

export interface Recommendation {
  id: string;
  priority: number;
  action: string;
  rationale: string;
  affectedAreas: string[];
  timeframe: string;
}

export interface PredictionMetadata {
  modelVersion: string;
  trainingDataPeriod: string;
  lastValidated: string;
  accuracy: number;
  dataSourcesUsed: string[];
}

export interface AIPredictionsData {
  alerts: Alert[];
  predictions: RiskPrediction[];
  recommendations: Recommendation[];
  contributingFactors: ContributingFactor[];
  metadata: PredictionMetadata;
  generatedAt: string;
}
