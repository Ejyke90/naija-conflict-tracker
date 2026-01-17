import React from 'react';

const StatsOverview: React.FC = () => {
  return (
    <div className="dashboard-grid">
      <div className="stat-card">
        <h3 className="text-lg font-semibold text-gray-900">Total Incidents</h3>
        <p className="text-3xl font-bold text-primary-600">1,234</p>
        <p className="text-sm text-gray-600">Last 30 days</p>
      </div>
      
      <div className="stat-card">
        <h3 className="text-lg font-semibold text-gray-900">Fatalities</h3>
        <p className="text-3xl font-bold text-danger-600">567</p>
        <p className="text-sm text-gray-600">Last 30 days</p>
      </div>
      
      <div className="stat-card">
        <h3 className="text-lg font-semibold text-gray-900">Active Hotspots</h3>
        <p className="text-3xl font-bold text-warning-600">23</p>
        <p className="text-sm text-gray-600">High risk areas</p>
      </div>
      
      <div className="stat-card">
        <h3 className="text-lg font-semibold text-gray-900">States Affected</h3>
        <p className="text-3xl font-bold text-gray-600">18</p>
        <p className="text-sm text-gray-600">Out of 36 states</p>
      </div>
    </div>
  );
};

export default StatsOverview;
