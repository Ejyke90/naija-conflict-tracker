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
    <div className="glass-card p-6">
      <h2 className="typography-heading text-xl text-tactical-e-ink mb-6">Conflict Trends</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis dataKey="month" stroke="rgba(255,255,255,0.5)" />
          <YAxis stroke="rgba(255,255,255,0.5)" />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'rgba(26, 31, 46, 0.9)', 
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '0.5rem'
            }}
            labelStyle={{ color: '#F8F9FA' }}
            itemStyle={{ color: '#F8F9FA' }}
          />
          <Line type="monotone" dataKey="incidents" stroke="#3B82F6" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TrendChart;
