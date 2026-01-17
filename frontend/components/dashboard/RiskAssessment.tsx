import React from 'react';

const RiskAssessment: React.FC = () => {
  const riskLevels = [
    { level: 'Very High', count: 3, color: 'bg-red-900 text-white' },
    { level: 'High', count: 8, color: 'bg-danger-100 text-danger-800' },
    { level: 'Medium', count: 12, color: 'bg-warning-100 text-warning-800' },
    { level: 'Low', count: 23, color: 'bg-success-100 text-success-800' }
  ];

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Risk Assessment</h2>
        <button className="btn btn-secondary text-sm">Details</button>
      </div>
      
      <div className="space-y-3">
        {riskLevels.map((risk) => (
          <div key={risk.level} className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${
                risk.level === 'Very High' ? 'bg-red-900' :
                risk.level === 'High' ? 'bg-danger-600' :
                risk.level === 'Medium' ? 'bg-warning-600' :
                'bg-success-600'
              }`}></div>
              <span className="text-sm font-medium text-gray-900">{risk.level}</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-semibold text-gray-900">{risk.count}</span>
              <span className="text-sm text-gray-600">LGAs</span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Total monitored areas</span>
          <span className="text-sm font-semibold text-gray-900">46 LGAs</span>
        </div>
      </div>
      
      <div className="mt-4">
        <div className="bg-warning-50 border border-warning-200 rounded-lg p-3">
          <p className="text-sm text-warning-800">
            ⚠️ 3 areas at very high risk - immediate attention required
          </p>
        </div>
      </div>
    </div>
  );
};

export default RiskAssessment;
