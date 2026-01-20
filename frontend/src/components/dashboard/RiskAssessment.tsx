import React from 'react';
import { AlertTriangle, Shield, TrendingUp, MapPin } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface RiskLevel {
  level: 'low' | 'medium' | 'high' | 'critical';
  areas: number;
  color: string;
  bgColor: string;
  description: string;
}

interface RiskAssessmentProps {
  className?: string;
}

export const RiskAssessment: React.FC<RiskAssessmentProps> = ({ className }) => {
  const riskLevels: RiskLevel[] = [
    {
      level: 'critical',
      areas: 3,
      color: 'text-red-700',
      bgColor: 'bg-red-50 border-red-200',
      description: 'Immediate attention required'
    },
    {
      level: 'high',
      areas: 8,
      color: 'text-orange-700',
      bgColor: 'bg-orange-50 border-orange-200',
      description: 'Enhanced monitoring needed'
    },
    {
      level: 'medium',
      areas: 12,
      color: 'text-yellow-700',
      bgColor: 'bg-yellow-50 border-yellow-200',
      description: 'Standard monitoring'
    },
    {
      level: 'low',
      areas: 23,
      color: 'text-green-700',
      bgColor: 'bg-green-50 border-green-200',
      description: 'Stable conditions'
    }
  ];

  const totalAreas = riskLevels.reduce((sum, level) => sum + level.areas, 0);

  const highRiskAreas = [
    { name: 'Borno State', risk: 'critical', factors: ['Terrorism', 'Displacement', 'Food insecurity'] },
    { name: 'Kaduna State', risk: 'high', factors: ['Farmer-herder conflicts', 'Kidnapping'] },
    { name: 'Plateau State', risk: 'high', factors: ['Communal conflicts', 'Land disputes'] }
  ];

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'critical': return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case 'high': return <TrendingUp className="w-4 h-4 text-orange-600" />;
      case 'medium': return <Shield className="w-4 h-4 text-yellow-600" />;
      default: return <Shield className="w-4 h-4 text-green-600" />;
    }
  };

  const getRiskBadgeColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Risk Level Overview */}
      <div className="space-y-3">
        {riskLevels.map((risk) => (
          <div
            key={risk.level}
            className={`p-3 rounded-lg border ${risk.bgColor}`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {getRiskIcon(risk.level)}
                <div>
                  <p className={`font-medium capitalize ${risk.color}`}>
                    {risk.level} Risk
                  </p>
                  <p className="text-xs text-gray-600">
                    {risk.description}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className={`text-lg font-bold ${risk.color}`}>
                  {risk.areas}
                </p>
                <p className="text-xs text-gray-500">
                  {((risk.areas / totalAreas) * 100).toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* High Risk Areas Details */}
      <div className="border-t pt-4">
        <h4 className="font-medium text-gray-900 mb-3 flex items-center">
          <MapPin className="w-4 h-4 mr-2" />
          Priority Areas
        </h4>
        
        <div className="space-y-2">
          {highRiskAreas.map((area, index) => (
            <div
              key={index}
              className="p-3 bg-gray-50 rounded-lg border"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <p className="font-medium text-sm">{area.name}</p>
                    <Badge 
                      variant="outline"
                      className={getRiskBadgeColor(area.risk)}
                    >
                      {area.risk.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {area.factors.map((factor, idx) => (
                      <span
                        key={idx}
                        className="inline-block px-2 py-1 text-xs bg-white rounded border text-gray-600"
                      >
                        {factor}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary Stats */}
      <div className="border-t pt-4">
        <div className="grid grid-cols-2 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-red-600">
              {riskLevels.find(r => r.level === 'critical')?.areas || 0}
            </p>
            <p className="text-xs text-gray-600">Critical Areas</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-green-600">
              {riskLevels.find(r => r.level === 'low')?.areas || 0}
            </p>
            <p className="text-xs text-gray-600">Stable Areas</p>
          </div>
        </div>
      </div>

      <div className="text-center">
        <p className="text-xs text-gray-500">
          Risk assessment updated hourly
        </p>
      </div>
    </div>
  );
};

export default RiskAssessment;
