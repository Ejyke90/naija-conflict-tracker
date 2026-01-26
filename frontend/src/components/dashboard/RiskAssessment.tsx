import React, { useEffect, useState } from 'react';
import { AlertTriangle, Shield, TrendingUp } from 'lucide-react';
import { getAccessToken } from '../../../contexts/AuthContext';

interface RegionalData {
  region: string;
  incidents: number;
  fatalities: number;
  risk_level: string;
}

const RiskAssessment: React.FC = () => {
  const [regions, setRegions] = useState<RegionalData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        const token = getAccessToken();
        const headers: HeadersInit = {};
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${apiUrl}/api/dashboard/report/analysis`, {
          headers
        });
        if (response.ok) {
          const result = await response.json();
          setRegions(result.regional_distribution || []);
        }
      } catch (err) {
        console.error("Error fetching risk data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Compute stats
  const highRisk = regions.filter(r => r.risk_level === 'High' || r.risk_level === 'Critical').length;
  const mediumRisk = regions.filter(r => r.risk_level === 'Medium').length;
  const lowRisk = regions.filter(r => r.risk_level === 'Low').length;
  const totalStates = regions.length || 1; // Avoid division by zero

  const topRiskyStates = regions
    .filter(r => r.risk_level === 'Critical' || r.risk_level === 'High')
    .slice(0, 3);

  if (loading) return (
    <div className="card h-full flex items-center justify-center p-6 text-gray-500">
      Loading assessment...
    </div>
  );

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-full flex flex-col">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Risk Assessment</h2>

      <div className="space-y-4 flex-1">
        <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg border border-red-100">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-600 mr-3" />
            <div>
              <p className="font-medium text-red-900">High Risk Zones</p>
              <p className="text-sm text-red-700">{highRisk} States identified</p>
            </div>
          </div>
          <span className="text-red-700 font-bold">{Math.round((highRisk / totalStates) * 100)}%</span>
        </div>

        <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg border border-yellow-100">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-yellow-600 mr-3" />
            <div>
              <p className="font-medium text-yellow-900">Medium Risk Zones</p>
              <p className="text-sm text-yellow-700">{mediumRisk} States identified</p>
            </div>
          </div>
          <span className="text-yellow-700 font-bold">{Math.round((mediumRisk / totalStates) * 100)}%</span>
        </div>

        <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-100">
          <div className="flex items-center">
            <Shield className="h-5 w-5 text-green-600 mr-3" />
            <div>
              <p className="font-medium text-green-900">Low Risk Zones</p>
              <p className="text-sm text-green-700">{lowRisk} States identified</p>
            </div>
          </div>
          <span className="text-green-700 font-bold">{Math.round((lowRisk / totalStates) * 100)}%</span>
        </div>
      </div>

      {topRiskyStates.length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-100">
          <h4 className="text-xs font-semibold text-gray-500 mb-3 uppercase tracking-wider">Critical Hotspots</h4>
          <div className="space-y-2">
            {topRiskyStates.map((state) => (
              <div key={state.region} className="flex items-center justify-between text-sm p-2 bg-gray-50 rounded-md">
                <span className="font-medium text-gray-700">{state.region}</span>
                <span className="text-red-600 font-medium">{state.incidents} Incidents</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-xs text-blue-800">
          Risk levels calculated based on incident frequency and fatality counts over the selected period.
        </p>
      </div>
    </div>
  );
};

export default RiskAssessment;
