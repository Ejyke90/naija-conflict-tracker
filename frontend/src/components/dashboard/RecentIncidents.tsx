import React, { useState, useEffect } from 'react';
import { Calendar, MapPin, Users, AlertCircle, ExternalLink } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface Incident {
  id: string;
  type: string;
  location: string;
  state: string;
  date: string;
  fatalities: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'verified' | 'reported' | 'investigating';
  description: string;
}

interface RecentIncidentsProps {
  limit?: number;
  showViewAll?: boolean;
}

export const RecentIncidents: React.FC<RecentIncidentsProps> = ({ 
  limit = 5, 
  showViewAll = true 
}) => {
  // Mock data - replace with real API data
  const incidents: Incident[] = [
    {
      id: '1',
      type: 'Armed Attack',
      location: 'Kaduna',
      state: 'Kaduna State',
      date: '2024-01-17',
      fatalities: 5,
      severity: 'high',
      status: 'verified',
      description: 'Armed attack on farming community in rural Kaduna'
    },
    {
      id: '2',
      type: 'Kidnapping',
      location: 'Abuja',
      state: 'FCT',
      date: '2024-01-16',
      fatalities: 0,
      severity: 'medium',
      status: 'reported',
      description: 'Kidnapping incident reported along Abuja-Kaduna highway'
    },
    {
      id: '3',
      type: 'Communal Conflict',
      location: 'Jos',
      state: 'Plateau State',
      date: '2024-01-16',
      fatalities: 2,
      severity: 'medium',
      status: 'verified',
      description: 'Farmer-herder conflict in Jos North LGA'
    },
    {
      id: '4',
      type: 'Banditry',
      location: 'Katsina',
      state: 'Katsina State',
      date: '2024-01-15',
      fatalities: 8,
      severity: 'high',
      status: 'verified',
      description: 'Bandit attack on village market'
    },
    {
      id: '5',
      type: 'Terrorism',
      location: 'Maiduguri',
      state: 'Borno State',
      date: '2024-01-14',
      fatalities: 12,
      severity: 'critical',
      status: 'investigating',
      description: 'Suspected terrorist attack on civilian targets'
    }
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified': return 'bg-green-100 text-green-800 border-green-200';
      case 'reported': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'investigating': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'terrorism':
      case 'armed attack':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'kidnapping':
        return <Users className="w-4 h-4 text-orange-600" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-600" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const displayedIncidents = incidents.slice(0, limit);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-medium text-gray-900">Latest Incidents</h3>
        <Badge variant="outline" className="text-green-600 border-green-200">
          Live Updates
        </Badge>
      </div>

      {/* Incidents List */}
      <div className="space-y-3">
        {displayedIncidents.map((incident) => (
          <div
            key={incident.id}
            className="p-4 bg-white border rounded-lg hover:shadow-sm transition-shadow"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                {getTypeIcon(incident.type)}
                <h4 className="font-medium text-sm">{incident.type}</h4>
                <Badge 
                  variant="outline"
                  className={getSeverityColor(incident.severity)}
                >
                  {incident.severity.toUpperCase()}
                </Badge>
              </div>
              
              <Badge 
                variant="outline"
                className={getStatusColor(incident.status)}
              >
                {incident.status}
              </Badge>
            </div>

            {/* Location and Date */}
            <div className="flex items-center space-x-4 mb-2 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <MapPin className="w-3 h-3" />
                <span>{incident.location}, {incident.state}</span>
              </div>
              
              <div className="flex items-center space-x-1">
                <Calendar className="w-3 h-3" />
                <span>{formatDate(incident.date)}</span>
              </div>
              
              {incident.fatalities > 0 && (
                <div className="flex items-center space-x-1">
                  <Users className="w-3 h-3" />
                  <span>{incident.fatalities} casualties</span>
                </div>
              )}
            </div>

            {/* Description */}
            <p className="text-sm text-gray-700 mb-3">
              {incident.description}
            </p>

            {/* Actions */}
            <div className="flex items-center justify-between">
              <div className="text-xs text-gray-500">
                Last updated: 2 minutes ago
              </div>
              
              <Button variant="ghost" size="sm" className="text-xs">
                <ExternalLink className="w-3 h-3 mr-1" />
                View Details
              </Button>
            </div>
          </div>
        ))}
      </div>

      {/* Load More Button */}
      {showViewAll && incidents.length > limit && (
        <div className="text-center pt-2">
          <Button variant="outline" size="sm" className="w-full">
            Load More Incidents
          </Button>
        </div>
      )}

      {/* Empty State */}
      {incidents.length === 0 && (
        <div className="text-center py-8">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No recent incidents to display</p>
          <p className="text-sm text-gray-400">Check back later for updates</p>
        </div>
      )}

      {/* Footer */}
      <div className="text-center pt-2 border-t">
        <p className="text-xs text-gray-500">
          Data updated every 15 minutes from verified sources
        </p>
      </div>
    </div>
  );
};

export default RecentIncidents;
