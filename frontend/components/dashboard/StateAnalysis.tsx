import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const StateAnalysis: React.FC = () => {
  // Sample state data
  const stateData = [
    { state: 'Kaduna', incidents: 145, fatalities: 23 },
    { state: 'Borno', incidents: 98, fatalities: 67 },
    { state: 'Zamfara', incidents: 87, fatalities: 12 },
    { state: 'Rivers', incidents: 76, fatalities: 8 },
    { state: 'Niger', incidents: 65, fatalities: 5 },
    { state: 'Benue', incidents: 54, fatalities: 9 },
    { state: 'Plateau', incidents: 43, fatalities: 15 },
    { state: 'Kano', incidents: 32, fatalities: 4 }
  ];

  const getRiskLevel = (index: number) => {
    if (index < 2) return 'High';
    if (index < 4) return 'Medium';
    return 'Low';
  };

  const getRiskSignalColor = (index: number) => {
    if (index < 2) return 'signal_critical';
    if (index < 4) return 'signal_medium';
    return 'signal_low';
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top States by Incidents */}
        <div className="glass-card p-6">
          <h3 className="typography-heading text-lg text-tactical-e-ink mb-4">States by Incident Count</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stateData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis type="number" stroke="rgba(255,255,255,0.5)" />
              <YAxis dataKey="state" type="category" width={80} stroke="rgba(255,255,255,0.5)" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(26, 31, 46, 0.9)', 
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '0.5rem'
                }}
                labelStyle={{ color: '#F8F9FA' }}
                itemStyle={{ color: '#F8F9FA' }}
              />
              <Bar dataKey="incidents" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top States by Fatalities */}
        <div className="glass-card p-6">
          <h3 className="typography-heading text-lg text-tactical-e-ink mb-4">States by Fatalities</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stateData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis type="number" stroke="rgba(255,255,255,0.5)" />
              <YAxis dataKey="state" type="category" width={80} stroke="rgba(255,255,255,0.5)" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(26, 31, 46, 0.9)', 
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '0.5rem'
                }}
                labelStyle={{ color: '#F8F9FA' }}
                itemStyle={{ color: '#F8F9FA' }}
              />
              <Bar dataKey="fatalities" fill="#DC2626" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* State Statistics Table */}
      <div className="glass-card p-6">
        <h3 className="typography-heading text-lg text-tactical-e-ink mb-4">State Statistics Overview</h3>
        <div className="overflow-x-auto">
          <table className="w-full typography-body text-sm">
            <thead>
              <tr className="border-b border-tactical-slate-light/30">
                <th className="text-left py-3 px-4 typography-label font-medium text-tactical-e-ink">State</th>
                <th className="text-right py-3 px-4 typography-label font-medium text-tactical-e-ink">Incidents</th>
                <th className="text-right py-3 px-4 typography-label font-medium text-tactical-e-ink">Fatalities</th>
                <th className="text-right py-3 px-4 typography-label font-medium text-tactical-e-ink">Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {stateData.map((state, index) => (
                <tr key={state.state} className="border-b border-tactical-slate-light/20 hover:bg-tactical-slate-medium/10">
                  <td className="py-3 px-4 typography-mono font-medium text-tactical-e-ink">{state.state}</td>
                  <td className="text-right py-3 px-4 typography-mono text-tactical-e-ink">{state.incidents}</td>
                  <td className="text-right py-3 px-4 typography-mono text-red-400">{state.fatalities}</td>
                  <td className="text-right py-3 px-4">
                    <span className={`px-2 py-1 text-xs rounded-full typography-label ${getRiskSignalColor(index)}`}>
                      {getRiskLevel(index)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default StateAnalysis;
