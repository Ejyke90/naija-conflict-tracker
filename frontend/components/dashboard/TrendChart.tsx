import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const TrendChart: React.FC = () => {
  // Sample data - replace with real conflict trend data
  const data = [
    { month: 'Jan', incidents: 45 },
    { month: 'Feb', incidents: 52 },
    { month: 'Mar', incidents: 38 },
    { month: 'Apr', incidents: 61 },
    { month: 'May', incidents: 55 },
    { month: 'Jun', incidents: 67 },
  ];

  return (
    <div className="card">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Conflict Trends</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="incidents" stroke="#8884d8" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TrendChart;
