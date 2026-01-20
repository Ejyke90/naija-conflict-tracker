import React from 'react';
import { 
  BarChart3, 
  Map, 
  TrendingUp, 
  AlertTriangle, 
  Settings, 
  Users,
  FileText,
  Bell,
  Database,
  X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavigationItem {
  name: string;
  icon: React.ComponentType<any>;
  href: string;
  badge?: string;
  active?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const navigation: NavigationItem[] = [
    { name: 'Dashboard', icon: BarChart3, href: '/', active: true },
    { name: 'Map View', icon: Map, href: '/' },
    { name: 'Analytics', icon: TrendingUp, href: '/' },
    { name: 'Reports', icon: FileText, href: '/' },
    { name: 'Alerts', icon: Bell, href: '/', badge: '3' },
    { name: 'Data Sources', icon: Database, href: '/' },
    { name: 'Users', icon: Users, href: '/' },
    { name: 'Settings', icon: Settings, href: '/' }
  ];

  const quickStats = [
    { label: 'Active Incidents', value: '23', color: 'text-red-600' },
    { label: 'States Monitored', value: '36', color: 'text-blue-600' },
    { label: 'Data Sources', value: '12', color: 'text-green-600' }
  ];

  return (
    <>
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <div className="flex flex-col w-64">
          <div className="flex flex-col h-0 flex-1 bg-white border-r border-gray-200">
            {/* Sidebar Header */}
            <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
              <div className="flex items-center flex-shrink-0 px-4 mb-6">
                <h2 className="text-lg font-semibold text-gray-900">Navigation</h2>
              </div>

              {/* Navigation Links */}
              <nav className="mt-5 flex-1 px-2 space-y-1">
                {navigation.map((item) => {
                  const Icon = item.icon;
                  return (
                    <a
                      key={item.name}
                      href={item.href}
                      className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                        item.active
                          ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                    >
                      <Icon
                        className={`mr-3 flex-shrink-0 h-5 w-5 ${
                          item.active ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                        }`}
                      />
                      {item.name}
                      {item.badge && (
                        <Badge className="ml-auto bg-red-100 text-red-800 border-red-200">
                          {item.badge}
                        </Badge>
                      )}
                    </a>
                  );
                })}
              </nav>

              {/* Quick Stats */}
              <div className="mt-8 px-4">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
                  Quick Stats
                </h3>
                <div className="space-y-3">
                  {quickStats.map((stat, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">{stat.label}</span>
                      <span className={`text-sm font-semibold ${stat.color}`}>
                        {stat.value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Risk Level Indicator */}
              <div className="mt-6 mx-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="flex items-center">
                  <AlertTriangle className="w-5 h-5 text-orange-600 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-orange-800">Current Risk Level</p>
                    <p className="text-xs text-orange-600">HIGH - Enhanced monitoring active</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Sidebar Footer */}
            <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
              <div className="text-xs text-gray-500">
                <p>Last updated: 2 min ago</p>
                <p>Data sources: 8 active</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Sidebar */}
      <div className={`lg:hidden fixed inset-y-0 left-0 z-50 w-64 bg-white transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex flex-col h-full">
          {/* Mobile Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Menu</h2>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>

          {/* Mobile Navigation */}
          <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.name}
                  href={item.href}
                  onClick={onClose}
                  className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                    item.active
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon
                    className={`mr-3 flex-shrink-0 h-5 w-5 ${
                      item.active ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                  />
                  {item.name}
                  {item.badge && (
                    <Badge className="ml-auto bg-red-100 text-red-800 border-red-200">
                      {item.badge}
                    </Badge>
                  )}
                </a>
              );
            })}
          </nav>

          {/* Mobile Footer */}
          <div className="border-t border-gray-200 p-4">
            <div className="text-xs text-gray-500">
              <p>Nextier Nigeria Conflict Tracker</p>
              <p>Real-time monitoring system</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
