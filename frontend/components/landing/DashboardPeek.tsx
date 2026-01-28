import React from 'react';
import { motion } from 'framer-motion';
import { Monitor, Maximize2, Minus, X } from 'lucide-react';

export const DashboardPeek: React.FC = () => {
  return (
    <section className="py-20 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Intelligence at Your Fingertips
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            Experience the power of real-time conflict intelligence with our comprehensive analytics dashboard.
          </p>
        </motion.div>

        {/* Browser Mockup */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9, rotateY: 15 }}
          whileInView={{ opacity: 1, scale: 1, rotateY: 0 }}
          transition={{ duration: 1, delay: 0.3 }}
          viewport={{ once: true }}
          className="relative max-w-6xl mx-auto"
        >
          {/* Browser Window Frame */}
          <div className="bg-slate-800 rounded-t-xl border border-slate-700 overflow-hidden shadow-2xl">
            {/* Browser Header */}
            <div className="bg-slate-900 px-4 py-3 flex items-center justify-between border-b border-slate-700">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              </div>
              <div className="flex-1 mx-4">
                <div className="bg-slate-800 rounded-md px-3 py-1 text-center text-sm text-slate-400 border border-slate-600">
                  app.naijaconflicttracker.com/dashboard
                </div>
              </div>
              <div className="flex gap-2">
                <Minus className="w-4 h-4 text-slate-400" />
                <Maximize2 className="w-4 h-4 text-slate-400" />
                <X className="w-4 h-4 text-slate-400" />
              </div>
            </div>

            {/* Browser Content - Blurred Dashboard Preview */}
            <div className="relative bg-slate-900 p-6 min-h-[500px] overflow-hidden">
              {/* Blur overlay */}
              <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-md z-10 flex items-center justify-center">
                <div className="text-center">
                  <Monitor className="w-16 h-16 text-slate-500 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-white mb-2">Dashboard Preview</h3>
                  <p className="text-slate-400 mb-6">Request access to unlock full analytics</p>
                  <button className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors">
                    Request Access
                  </button>
                </div>
              </div>

              {/* Mock Dashboard Content (blurred) */}
              <div className="filter blur-sm opacity-30">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h1 className="text-2xl font-bold text-white">Naija Conflict Tracker</h1>
                    <p className="text-slate-400">Real-time conflict monitoring</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-slate-400">Last Updated</div>
                    <div className="text-lg font-mono text-emerald-400">14:32:15</div>
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                  {[
                    { label: 'Active Incidents', value: '47', color: 'text-blue-400' },
                    { label: 'High Risk Areas', value: '12', color: 'text-red-400' },
                    { label: 'AI Confidence', value: '94%', color: 'text-green-400' },
                    { label: 'Response Time', value: '2.3s', color: 'text-purple-400' }
                  ].map((metric, index) => (
                    <div key={index} className="bg-slate-800/50 p-6 rounded-xl border border-slate-700">
                      <div className="text-2xl font-bold text-white mb-1">{metric.value}</div>
                      <div className="text-sm text-slate-400">{metric.label}</div>
                    </div>
                  ))}
                </div>

                {/* Map and Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Map Placeholder */}
                  <div className="lg:col-span-2 bg-slate-800/50 rounded-xl border border-slate-700 p-6">
                    <h3 className="text-lg font-bold text-white mb-4">Threat Map</h3>
                    <div className="bg-slate-900 rounded-lg h-64 flex items-center justify-center">
                      <div className="text-slate-500">Interactive Map</div>
                    </div>
                  </div>

                  {/* Sidebar */}
                  <div className="space-y-6">
                    {/* AI Foresight */}
                    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
                      <h3 className="text-lg font-bold text-white mb-4">AI Foresight</h3>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-slate-400">Risk Level</span>
                          <span className="text-red-400 font-semibold">HIGH</span>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div className="bg-red-500 h-2 rounded-full w-3/4"></div>
                        </div>
                      </div>
                    </div>

                    {/* Incident Feed */}
                    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
                      <h3 className="text-lg font-bold text-white mb-4">Recent Incidents</h3>
                      <div className="space-y-3">
                        {[
                          { location: 'Kaduna North', type: 'Armed Conflict', time: '2h ago' },
                          { location: 'Borno South', type: 'Kidnapping', time: '4h ago' },
                          { location: 'Zamfara Central', type: 'Banditry', time: '6h ago' }
                        ].map((incident, index) => (
                          <div key={index} className="flex items-center justify-between py-2 border-b border-slate-700 last:border-b-0">
                            <div>
                              <div className="text-white font-medium">{incident.location}</div>
                              <div className="text-slate-400 text-sm">{incident.type}</div>
                            </div>
                            <div className="text-slate-500 text-sm">{incident.time}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Browser Shadow */}
          <div className="absolute -bottom-4 -right-4 w-full h-full bg-slate-800 rounded-xl -z-10 opacity-50"></div>
        </motion.div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
          className="text-center mt-16"
        >
          <p className="text-lg text-slate-300 mb-6">
            Join government agencies and NGOs already using our platform to prevent violence and save lives.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-8 py-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-all hover:shadow-lg hover:shadow-red-500/50">
              Request Demo
            </button>
            <button className="px-8 py-4 border border-slate-600 text-slate-300 hover:text-white hover:border-slate-500 font-semibold rounded-lg transition-all">
              Learn More
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
};