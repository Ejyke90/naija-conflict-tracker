import React from 'react';
import { AlertTriangle, Shield, TrendingUp } from 'lucide-react';

const RiskAssessment: React.FC = () => {
  return (
    <div className="card">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Risk Assessment</h2>

      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-500 mr-3" />
            <div>
              <p className="font-medium text-red-800">High Risk Zone</p>
              <p className="text-sm text-red-600">North Central Region</p>
            </div>
          </div>
          <span className="text-red-600 font-semibold">85%</span>
        </div>

        <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-yellow-500 mr-3" />
            <div>
              <p className="font-medium text-yellow-800">Medium Risk Zone</p>
              <p className="text-sm text-yellow-600">South West Region</p>
            </div>
          </div>
          <span className="text-yellow-600 font-semibold">62%</span>
        </div>

        <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
          <div className="flex items-center">
            <Shield className="h-5 w-5 text-green-500 mr-3" />
            <div>
              <p className="font-medium text-green-800">Low Risk Zone</p>
              <p className="text-sm text-green-600">South East Region</p>
            </div>
          </div>
          <span className="text-green-600 font-semibold">23%</span>
        </div>
      </div>

      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-800">
          Risk assessment based on historical data, current trends, and geopolitical factors.
        </p>
      </div>
    </div>
  );
};

export default RiskAssessment;
