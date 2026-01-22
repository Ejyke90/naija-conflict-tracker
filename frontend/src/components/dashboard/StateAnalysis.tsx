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

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top States by Incidents */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">States by Incident Count</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stateData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="state" type="category" width={80} />
              <Tooltip />
              <Bar dataKey="incidents" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top States by Fatalities */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">States by Fatalities</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stateData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="state" type="category" width={80} />
              <Tooltip />
              <Bar dataKey="fatalities" fill="#dc2626" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* State Statistics Table */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">State Statistics Overview</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium">State</th>
                <th className="text-right py-3 px-4 font-medium">Incidents</th>
                <th className="text-right py-3 px-4 font-medium">Fatalities</th>
                <th className="text-right py-3 px-4 font-medium">Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {stateData.map((state, index) => (
                <tr key={state.state} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium">{state.state}</td>
                  <td className="text-right py-3 px-4">{state.incidents}</td>
                  <td className="text-right py-3 px-4 text-red-600">{state.fatalities}</td>
                  <td className="text-right py-3 px-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      index < 2 ? 'bg-red-100 text-red-800' :
                      index < 4 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {index < 2 ? 'High' : index < 4 ? 'Medium' : 'Low'}
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
