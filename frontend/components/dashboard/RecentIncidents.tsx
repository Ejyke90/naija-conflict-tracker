import React, { useState, useEffect } from 'react';

interface Incident {
  id: number;
  date: string;
  location: string;
  type: string;
  casualties: number;
  status: string;
}

const RecentIncidents: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL;
        if (!apiUrl) {
          throw new Error('API URL not configured');
        }

        const response = await fetch(`${apiUrl}/api/dashboard/recent-incidents?limit=10&days=7`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setIncidents(data.incidents || []);
      } catch (err) {
        console.error('Error fetching recent incidents:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch incidents');
        // Fallback to placeholder data
        setIncidents([
          {
            id: 1,
            date: '2024-01-17',
            location: 'No data available',
            type: 'Check API connection',
            casualties: 0,
            status: 'error'
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchIncidents();
  }, []);

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Recent Incidents</h2>
        <button className="btn btn-secondary text-sm">View All</button>
      </div>
      
      <div className="space-y-3">
        {incidents.map((incident) => (
          <div key={incident.id} className="border-b border-gray-200 pb-3 last:border-0">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h3 className="font-medium text-gray-900">{incident.type}</h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    incident.status === 'verified' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {incident.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{incident.location}</p>
                <p className="text-xs text-gray-500 mt-1">{incident.date}</p>
              </div>
              <div className="text-right">
                <p className="text-lg font-semibold text-danger-600">{incident.casualties}</p>
                <p className="text-xs text-gray-500">casualties</p>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-center">
        <button className="btn btn-primary text-sm">Load More Incidents</button>
      </div>
    </div>
  );
};

export default RecentIncidents;
