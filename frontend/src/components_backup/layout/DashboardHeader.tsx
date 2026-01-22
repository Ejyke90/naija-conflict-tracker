import React from 'react';
import Link from 'next/link';

interface DashboardHeaderProps {
  className?: string;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({ className = '' }) => {
  return (
    <div className={`bg-gradient-to-r from-blue-600 to-blue-800 text-white py-16 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-4">
            Nextier Conflict Tracker
          </h1>
          <p className="text-xl md:text-2xl text-blue-100 max-w-3xl mx-auto mb-6">
            Real-time conflict monitoring and predictive analysis for Nigeria
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link 
              href="/dashboard"
              className="px-6 py-2 bg-white text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors"
            >
              Dashboard
            </Link>
            <Link 
              href="/conflict-index"
              className="px-6 py-2 bg-blue-500 border-2 border-white text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
            >
              Conflict Index
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
