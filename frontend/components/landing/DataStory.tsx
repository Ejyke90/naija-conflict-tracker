import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Users, MapPin, Calendar, AlertTriangle } from 'lucide-react';

interface DataStoryProps {
  stats: {
    total_incidents_30d: number;
    total_fatalities_30d: number;
    states_affected: number;
    active_hotspots: number;
    top_states: Array<{
      name: string;
      incidents: number;
      fatalities: number;
    }>;
    timeline_sparkline?: number[];
  };
}

export const DataStory: React.FC<DataStoryProps> = ({ stats }) => {
  // Calculate insights
  const avgFatalitiesPerIncident = stats.total_incidents_30d > 0
    ? (stats.total_fatalities_30d / stats.total_incidents_30d).toFixed(1)
    : '0';

  const mostAffectedState = stats.top_states?.[0]?.name || 'N/A';
  const mostAffectedIncidents = stats.top_states?.[0]?.incidents || 0;

  // Calculate trend
  const sparkline = stats.timeline_sparkline || [];
  const recentTrend = sparkline.length >= 2
    ? sparkline[sparkline.length - 1] > sparkline[sparkline.length - 2]
      ? 'increasing'
      : 'decreasing'
    : 'stable';

  return (
    <div className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm border border-gray-700 rounded-xl p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-lg bg-gradient-to-br from-red-500/20 to-orange-500/20">
            <AlertTriangle className="w-6 h-6 text-red-400" />
          </div>
          <h2 className="text-2xl font-bold text-white">Conflict Landscape: Last 30 Days</h2>
        </div>

        <div className="space-y-6 text-gray-300 leading-relaxed">
          {/* Opening statement */}
          <p className="text-lg">
            Nigeria recorded{' '}
            <span className="text-red-400 font-bold text-xl">{stats.total_incidents_30d}</span>{' '}
            violent conflict incidents in the past 30 days, resulting in{' '}
            <span className="text-orange-400 font-bold text-xl">{stats.total_fatalities_30d}</span>{' '}
            fatalities across{' '}
            <span className="text-yellow-400 font-bold">{stats.states_affected}</span> states.
          </p>

          {/* Geographic concentration */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <MapPin className="w-5 h-5 text-red-400 mt-1 flex-shrink-0" />
              <div>
                <p className="font-semibold text-white mb-2">Geographic Concentration</p>
                <p>
                  <span className="text-red-400 font-bold">{mostAffectedState}</span> remains the
                  epicenter with{' '}
                  <span className="text-white font-semibold">{mostAffectedIncidents} incidents</span>,
                  representing{' '}
                  {((mostAffectedIncidents / stats.total_incidents_30d) * 100).toFixed(1)}% of all
                  conflicts. Violence is concentrated in{' '}
                  <span className="text-orange-400 font-semibold">{stats.active_hotspots}</span>{' '}
                  active hotspot LGAs.
                </p>
              </div>
            </div>
          </div>

          {/* Severity analysis */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Users className="w-5 h-5 text-orange-400 mt-1 flex-shrink-0" />
              <div>
                <p className="font-semibold text-white mb-2">Impact & Severity</p>
                <p>
                  Each incident averages{' '}
                  <span className="text-orange-400 font-bold text-lg">{avgFatalitiesPerIncident}</span>{' '}
                  fatalities, indicating {parseFloat(avgFatalitiesPerIncident) > 3 ? 'high-intensity' : 'moderate'}{' '}
                  violence. The human toll continues to mount, with communities facing displacement,
                  economic disruption, and psychological trauma.
                </p>
              </div>
            </div>
          </div>

          {/* Temporal trend */}
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <TrendingUp className="w-5 h-5 text-yellow-400 mt-1 flex-shrink-0" />
              <div>
                <p className="font-semibold text-white mb-2">Recent Trends</p>
                <p>
                  Violence is currently{' '}
                  <span
                    className={`font-bold ${
                      recentTrend === 'increasing'
                        ? 'text-red-400'
                        : recentTrend === 'decreasing'
                        ? 'text-green-400'
                        : 'text-yellow-400'
                    }`}
                  >
                    {recentTrend}
                  </span>
                  . The conflict trajectory shows{' '}
                  {recentTrend === 'increasing'
                    ? 'an alarming escalation requiring urgent intervention'
                    : recentTrend === 'decreasing'
                    ? 'a positive de-escalation, though vigilance remains critical'
                    : 'persistent instability with no clear resolution'}
                  .
                </p>
              </div>
            </div>
          </div>

          {/* Call to action context */}
          <div className="pt-4 border-t border-gray-700">
            <p className="text-sm text-gray-400 italic">
              <Calendar className="w-4 h-4 inline mr-2" />
              This data-driven narrative updates daily, providing real-time insights into Nigeria&apos;s
              conflict dynamics. Access the full platform for predictive analytics, interactive maps,
              and detailed incident reports.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
