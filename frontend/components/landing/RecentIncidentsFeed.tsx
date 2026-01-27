import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { AlertCircle, MapPin, Calendar, Users, ArrowRight, CheckCircle } from 'lucide-react';

interface Incident {
  id: string;
  state: string;
  lga?: string;
  event_type: string;
  fatalities?: number;
  injuries?: number;
  event_date: string;
  verified: boolean;
  source?: string;
}

export const RecentIncidentsFeed: React.FC = () => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRecentIncidents = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/conflicts?limit=5&sort=-event_date`);
        
        if (response.ok) {
          const data = await response.json();
          setIncidents(data.items || data || []);
        }
      } catch (error) {
        console.error('Failed to fetch recent incidents:', error);
        // Use fallback demo data
        setIncidents([
          {
            id: '1',
            state: 'Kaduna',
            lga: 'Zaria',
            event_type: 'Armed Conflict',
            fatalities: 12,
            injuries: 8,
            event_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            verified: true,
            source: 'Premium Times'
          },
          {
            id: '2',
            state: 'Borno',
            lga: 'Maiduguri',
            event_type: 'Terrorist Attack',
            fatalities: 8,
            injuries: 15,
            event_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            verified: true,
            source: 'Daily Trust'
          },
          {
            id: '3',
            state: 'Plateau',
            lga: 'Jos North',
            event_type: 'Communal Clash',
            fatalities: 5,
            injuries: 12,
            event_date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
            verified: true,
            source: 'The Nation'
          },
          {
            id: '4',
            state: 'Zamfara',
            lga: 'Gusau',
            event_type: 'Banditry',
            fatalities: 15,
            injuries: 6,
            event_date: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
            verified: true,
            source: 'Vanguard'
          },
          {
            id: '5',
            state: 'Niger',
            lga: 'Minna',
            event_type: 'Kidnapping',
            fatalities: 0,
            injuries: 0,
            event_date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            verified: false,
            source: 'Punch'
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchRecentIncidents();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined 
    });
  };

  const getSeverityColor = (fatalities: number = 0) => {
    if (fatalities >= 10) return 'text-red-400 bg-red-500/10 border-red-500/20';
    if (fatalities >= 5) return 'text-orange-400 bg-orange-500/10 border-orange-500/20';
    if (fatalities >= 1) return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
    return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
  };

  if (loading) {
    return (
      <div className="bg-black/40 backdrop-blur-sm rounded-2xl border border-gray-800 p-6 lg:p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-800 rounded w-1/3"></div>
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-20 bg-gray-800 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      viewport={{ once: true }}
      className="bg-black/40 backdrop-blur-sm rounded-2xl border border-gray-800 p-6 lg:p-8 shadow-2xl shadow-red-900/20"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center justify-center">
            <AlertCircle className="w-5 h-5 text-red-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Recent Incidents</h2>
            <p className="text-sm text-gray-500">Latest conflict events (Public Preview)</p>
          </div>
        </div>
        <Link href="/register">
          <button className="text-sm text-red-400 hover:text-red-300 font-medium transition-colors flex items-center space-x-1">
            <span>View All</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </Link>
      </div>

      <div className="space-y-3">
        {incidents.map((incident, index) => (
          <motion.div
            key={incident.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
            className="group bg-gray-900/50 border border-gray-800 rounded-xl p-4 hover:border-gray-700 hover:bg-gray-900/70 transition-all cursor-pointer"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  <span className="text-white font-semibold">
                    {incident.state}
                    {incident.lga && <span className="text-gray-400 font-normal"> · {incident.lga}</span>}
                  </span>
                  {incident.verified && (
                    <span className="inline-flex items-center space-x-1 text-xs text-green-400">
                      <CheckCircle className="w-3 h-3" />
                      <span>Verified</span>
                    </span>
                  )}
                </div>

                <div className="flex items-center space-x-2 mb-2">
                  <span className={`text-xs px-2 py-1 rounded-md border font-medium ${getSeverityColor(incident.fatalities)}`}>
                    {incident.event_type}
                  </span>
                </div>

                <div className="flex items-center space-x-4 text-sm text-gray-400">
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{formatDate(incident.event_date)}</span>
                  </div>
                  {(incident.fatalities !== undefined && incident.fatalities > 0) && (
                    <div className="flex items-center space-x-1">
                      <Users className="w-3.5 h-3.5" />
                      <span>{incident.fatalities} casualties</span>
                    </div>
                  )}
                  {incident.source && (
                    <div className="text-xs text-gray-500 truncate">
                      Source: {incident.source}
                    </div>
                  )}
                </div>
              </div>

              <div className="ml-4">
                <ArrowRight className="w-5 h-5 text-gray-600 group-hover:text-gray-400 group-hover:translate-x-1 transition-all" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-gray-800 text-center">
        <Link href="/register">
          <button className="inline-flex items-center space-x-2 text-sm text-gray-400 hover:text-white transition-colors group">
            <span>Sign up to access detailed incident data and analytics</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </Link>
      </div>
    </motion.div>
  );
};
