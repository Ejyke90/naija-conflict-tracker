import React from 'react';

interface TrendsChartProps {
  title: string;
  type: 'line' | 'bar';
}

const TrendsChart: React.FC<TrendsChartProps> = ({ title, type }) => {
  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
        <select className="text-sm border border-gray-300 rounded px-2 py-1">
          <option>Last 30 days</option>
          <option>Last 90 days</option>
          <option>Last year</option>
        </select>
      </div>
      
      <div className="bg-gray-50 rounded-lg p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">
            {type === 'line' ? '📈' : '📊'}
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {type === 'line' ? 'Trend Chart' : 'Bar Chart'}
          </h3>
          <p className="text-gray-600">
            Interactive chart visualization with Recharts
          </p>
        </div>
      </div>
      
      <div className="mt-4 flex justify-between text-sm text-gray-600">
        <span>📊 Data updated hourly</span>
        <span>📥 Export available</span>
      </div>
    </div>
  );
};

export default TrendsChart;
