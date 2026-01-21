import React from 'react';
import { 
  BarChart3, 
  Map, 
  AlertTriangle, 
  FileText, 
  Settings, 
  Users, 
  Database,
  Bell,
  TrendingUp
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface MenuItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeView, onViewChange, isOpen = true, onClose }) => {
  const menuItems: MenuItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'map', label: 'Map View', icon: Map },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp },
    { id: 'reports', label: 'Reports', icon: FileText },
    { id: 'alerts', label: 'Alerts', icon: Bell, badge: 3 },
    { id: 'data-sources', label: 'Data Sources', icon: Database },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];
  return (
    <>
      {/* Mobile Sidebar */}
      {isOpen && (
        <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 lg:hidden">
          <div className="flex flex-col h-full">
            {/* Mobile Close Button */}
            <div className="flex justify-end p-4">
              <button
                onClick={onClose}
                className="p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
              >
                <span className="sr-only">Close sidebar</span>
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            {/* Sidebar Content */}
            <div className="flex-1 overflow-y-auto">
              {/* Header */}
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                    <BarChart3 className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h1 className="text-lg font-semibold text-gray-900">NextierConflictTracker</h1>
                    <p className="text-sm text-gray-500">Nigeria Conflict Monitoring</p>
                  </div>
                </div>
                <div className="mt-4 flex items-center space-x-2">
                  <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">
                    <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                    Live
                  </Badge>
                </div>
              </div>

              {/* Navigation */}
              <div className="flex-1 p-4">
                <nav className="space-y-1">
                  <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
                    Navigation
                  </div>
                  {menuItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeView === item.id;
                    
                    return (
                      <button
                        key={item.id}
                        onClick={() => {
                          onViewChange(item.id);
                          if (onClose) onClose();
                        }}
                        className={`w-full flex items-center justify-between px-3 py-2 text-sm rounded-lg transition-colors ${
                          isActive 
                            ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600' 
                            : 'text-gray-700 hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-center space-x-3">
                          <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-gray-500'}`} />
                          <span className="font-medium">{item.label}</span>
                        </div>
                        {item.badge && (
                          <Badge variant="secondary" className="bg-red-100 text-red-600 text-xs">
                            {item.badge}
                          </Badge>
                        )}
                      </button>
                    );
                  })}
                </nav>
              </div>

              {/* Quick Stats */}
              <div className="p-4 border-t border-gray-200">
                <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
                  Quick Stats
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Active Incidents</span>
                    <span className="text-sm font-semibold text-gray-900">23</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">States Monitored</span>
                    <span className="text-sm font-semibold text-gray-900">36</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Data Sources</span>
                    <span className="text-sm font-semibold text-gray-900">12</span>
                  </div>
                </div>

                {/* Current Risk Level */}
                <div className="mt-4 p-3 bg-orange-50 rounded-lg border border-orange-200">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 text-orange-600" />
                    <span className="text-sm font-medium text-orange-800">Current Risk Level</span>
                  </div>
                  <div className="mt-1">
                    <span className="text-lg font-bold text-orange-900">HIGH</span>
                    <p className="text-xs text-orange-700">Enhanced monitoring active</p>
                  </div>
                </div>

                {/* Last Updated */}
                <div className="mt-4 text-xs text-gray-500">
                  Last updated: 2 min ago
                  <br />
                  Data sources: 8 active
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <div className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200 overflow-y-auto">
          {/* Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">NextierConflictTracker</h1>
                <p className="text-sm text-gray-500">Nigeria Conflict Monitoring</p>
              </div>
            </div>
            <div className="mt-4 flex items-center space-x-2">
              <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
                Live
              </Badge>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex-1 p-4">
            <nav className="space-y-1">
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
                Navigation
              </div>
              {menuItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeView === item.id;
                
                return (
                  <button
                    key={item.id}
                    onClick={() => onViewChange(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 text-sm rounded-lg transition-colors ${
                      isActive 
                        ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600' 
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-gray-500'}`} />
                      <span className="font-medium">{item.label}</span>
                    </div>
                    {item.badge && (
                      <Badge variant="secondary" className="bg-red-100 text-red-600 text-xs">
                        {item.badge}
                      </Badge>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Quick Stats */}
          <div className="p-4 border-t border-gray-200">
            <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
              Quick Stats
            </div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Active Incidents</span>
                <span className="text-sm font-semibold text-gray-900">23</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">States Monitored</span>
                <span className="text-sm font-semibold text-gray-900">36</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Data Sources</span>
                <span className="text-sm font-semibold text-gray-900">12</span>
              </div>
            </div>

            {/* Current Risk Level */}
            <div className="mt-4 p-3 bg-orange-50 rounded-lg border border-orange-200">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-orange-600" />
                <span className="text-sm font-medium text-orange-800">Current Risk Level</span>
              </div>
              <div className="mt-1">
                <span className="text-lg font-bold text-orange-900">HIGH</span>
                <p className="text-xs text-orange-700">Enhanced monitoring active</p>
              </div>
            </div>

            {/* Last Updated */}
            <div className="mt-4 text-xs text-gray-500">
              Last updated: 2 min ago
              <br />
              Data sources: 8 active
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
