import React from 'react';

const RecentIncidents: React.FC = () => {
  const incidents = [
    {
      id: 1,
      date: '2024-01-17',
      location: 'Borno State',
      type: 'Armed Attack',
      casualties: 5,
      status: 'verified'
    },
    {
      id: 2,
      date: '2024-01-17',
      location: 'Kaduna State',
      type: 'Kidnapping',
      casualties: 3,
      status: 'reported'
    },
    {
      id: 3,
      date: '2024-01-16',
      location: 'Rivers State',
      type: 'Communal Conflict',
      casualties: 2,
      status: 'verified'
    },
    {
      id: 4,
      date: '2024-01-16',
      location: 'Niger State',
      type: 'Banditry',
      casualties: 8,
      status: 'reported'
    }
  ];

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
