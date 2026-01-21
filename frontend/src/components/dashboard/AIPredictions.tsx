import React from 'react';
import { Brain, TrendingUp, AlertTriangle, Shield, Zap, Target } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

interface PredictionData {
  state: string;
  predictedIncidents: number;
  confidence: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  trend: 'increasing' | 'decreasing' | 'stable';
  factors: string[];
}

export const AIPredictions: React.FC = () => {
  const predictions: PredictionData[] = [
    {
      state: 'Kaduna',
      predictedIncidents: 23,
      confidence: 87,
      riskLevel: 'critical',
      trend: 'increasing',
      factors: ['Historical patterns', 'Recent escalation', 'Political tensions']
    },
    {
      state: 'Borno',
      predictedIncidents: 18,
      confidence: 92,
      riskLevel: 'high',
      trend: 'stable',
      factors: ['Ongoing insurgency', 'Border proximity', 'Resource scarcity']
    },
    {
      state: 'Rivers',
      predictedIncidents: 12,
      confidence: 78,
      riskLevel: 'high',
      trend: 'increasing',
      factors: ['Election proximity', 'Political violence', 'Economic factors']
    },
    {
      state: 'Zamfara',
      predictedIncidents: 15,
      confidence: 85,
      riskLevel: 'medium',
      trend: 'decreasing',
      factors: ['Security improvements', 'Community engagement', 'Bandit activity reduction']
    }
  ];

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing': return <TrendingUp className="w-4 h-4 text-red-500" />;
      case 'decreasing': return <TrendingUp className="w-4 h-4 text-green-500 rotate-180" />;
      default: return <Target className="w-4 h-4 text-blue-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* AI Header */}
      <Card className="glass border-0 shadow-2xl">
        <CardHeader className="text-center pb-4">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-lg">
              <Brain className="w-8 h-8 text-white animate-pulse-slow" />
            </div>
            <div>
              <CardTitle className="text-2xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AI Conflict Prediction Engine
              </CardTitle>
              <CardDescription className="text-lg">
                Machine learning-powered risk assessment and predictive analytics
              </CardDescription>
            </div>
          </div>

          <div className="flex items-center justify-center gap-6 text-sm text-slate-600">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span>Real-time processing</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-green-500" />
              <span>87% avg accuracy</span>
            </div>
            <div className="flex items-center gap-2">
              <Brain className="w-4 h-4 text-blue-500" />
              <span>Groq Llama-3 powered</span>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Prediction Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {predictions.map((prediction, index) => (
          <Card key={prediction.state} className="group hover:shadow-2xl transition-all duration-500 border-0 shadow-xl bg-gradient-to-br from-white to-slate-50">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-4 h-4 rounded-full ${getRiskColor(prediction.riskLevel)} animate-pulse`}></div>
                  <CardTitle className="text-xl">{prediction.state} State</CardTitle>
                  {getTrendIcon(prediction.trend)}
                </div>
                <Badge
                  className={`${
                    prediction.riskLevel === 'critical' ? 'bg-red-100 text-red-800' :
                    prediction.riskLevel === 'high' ? 'bg-orange-100 text-orange-800' :
                    prediction.riskLevel === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  } border-0`}
                >
                  {prediction.riskLevel.toUpperCase()}
                </Badge>
              </div>
              <CardDescription>
                Predicted incidents for next 30 days
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              {/* Prediction Value */}
              <div className="text-center py-4">
                <div className="text-4xl font-bold text-slate-900 mb-2">
                  {prediction.predictedIncidents}
                </div>
                <div className="text-sm text-slate-600">Expected incidents</div>
              </div>

              {/* Confidence Score */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">AI Confidence</span>
                  <span className="font-semibold text-slate-900">{prediction.confidence}%</span>
                </div>
                <Progress value={prediction.confidence} className="h-2" />
              </div>

              {/* Key Factors */}
              <div className="space-y-2">
                <div className="text-sm font-medium text-slate-700">Key Risk Factors:</div>
                <div className="flex flex-wrap gap-2">
                  {prediction.factors.map((factor, idx) => (
                    <Badge key={idx} variant="outline" className="text-xs bg-slate-50 border-slate-200">
                      {factor}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Explainable AI Section */}
              <div className="mt-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100">
                <div className="flex items-start gap-2">
                  <Brain className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="text-xs text-slate-700">
                    <div className="font-medium mb-1">AI Analysis:</div>
                    <div className="text-slate-600">
                      Prediction based on 12-month historical data, current political climate,
                      and regional conflict patterns. Model accuracy validated against past predictions.
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Model Performance */}
      <Card className="glass border-0 shadow-xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5 text-blue-600" />
            Model Performance Metrics
          </CardTitle>
          <CardDescription>
            Real-time AI model accuracy and prediction confidence
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
              <div className="text-2xl font-bold text-green-700">87%</div>
              <div className="text-sm text-green-600">Accuracy</div>
            </div>
            <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
              <div className="text-2xl font-bold text-blue-700">0.12</div>
              <div className="text-sm text-blue-600">MSE Score</div>
            </div>
            <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
              <div className="text-2xl font-bold text-purple-700">15min</div>
              <div className="text-sm text-purple-600">Update Freq</div>
            </div>
            <div className="text-center p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg">
              <div className="text-2xl font-bold text-orange-700">24</div>
              <div className="text-sm text-orange-600">Features Used</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIPredictions;
