import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface TrendData {
  month: string;
  incidents: number;
  fatalities: number;
}

const TrendChart: React.FC = () => {
  const [data, setData] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/dashboard/report/analysis`);
        if (!response.ok) {
          throw new Error('Failed to fetch trend data');
        }
        const result = await response.json();
        // Result.temporal_trends is the array we want
        setData(result.temporal_trends || []);
      } catch (err) {
        console.error("Error fetching trend data:", err);
        setError('Failed to load trend data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div className="h-[300px] flex items-center justify-center text-gray-500">Loading trends...</div>;
  if (error) return <div className="h-[300px] flex items-center justify-center text-red-500 text-sm">{error}</div>;

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Conflict Trend Analysis</h2>
      {data.length === 0 ? (
        <div className="h-[300px] flex items-center justify-center text-gray-400">No trend data available</div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="month" stroke="#6b7280" tick={{fontSize: 12}} />
            <YAxis yAxisId="left" stroke="#6b7280" tick={{fontSize: 12}} label={{ value: 'Incidents', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }} />
            <YAxis yAxisId="right" orientation="right" stroke="#ef4444" tick={{fontSize: 12}} label={{ value: 'Fatalities', angle: 90, position: 'insideRight' }} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
            />
            <Legend wrapperStyle={{paddingTop: '10px'}} />
            <Line yAxisId="left" type="monotone" dataKey="incidents" name="Incidents" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
            <Line yAxisId="right" type="monotone" dataKey="fatalities" name="Fatalities" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default TrendChart;
