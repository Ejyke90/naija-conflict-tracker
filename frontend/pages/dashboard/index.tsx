import React from 'react';
import dynamic from 'next/dynamic';
import ConflictChart from '../../components/dataviz_agent';
const ConflictMap = dynamic(() => import('../../components/cartography_agent'), { ssr: false });

const Dashboard = () => {
  const chartData = [{ date: '2023-01-01', incidents: 5 }, { date: '2023-02-01', incidents: 3 }];  // Example data, replace with API fetch
  const mapPositions = [{ lat: 6.5244, lon: 3.3792, location: 'Lagos' }];  // Example positions
  return (
    <div>
      <h1>Conflict Dashboard</h1>
      <ConflictChart data={chartData} />
      <ConflictMap positions={mapPositions} />
    </div>
  );
};

export default Dashboard;
