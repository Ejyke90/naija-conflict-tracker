import React from 'react';
import { motion } from 'framer-motion';
import {
  Newspaper,
  MessageSquare,
  Radio,
  Brain,
  Network,
  Smartphone,
  Bell,
  Shield
} from 'lucide-react';

export const HowItWorks: React.FC = () => {
  const features = [
    {
      title: 'Data Aggregation',
      description: 'Real-time collection from multiple sources including news outlets, social media, and field reports.',
      icon: <Newspaper className="w-8 h-8" />,
      items: [
        { icon: <Newspaper className="w-5 h-5" />, label: 'News Sources' },
        { icon: <MessageSquare className="w-5 h-5" />, label: 'Social Media' },
        { icon: <Radio className="w-5 h-5" />, label: 'Field Reports' }
      ],
      span: 'col-span-1 md:col-span-2'
    },
    {
      title: 'AI Engine',
      description: 'Advanced machine learning algorithms analyze patterns and predict conflict escalation with high accuracy.',
      icon: <Brain className="w-8 h-8" />,
      visualization: (
        <div className="mt-4 p-4 bg-slate-800/50 rounded-lg">
          <div className="flex items-center justify-center space-x-2">
            <div className="w-3 h-3 bg-blue-400 rounded-full animate-pulse"></div>
            <div className="w-8 h-0.5 bg-slate-600"></div>
            <div className="w-4 h-4 bg-green-400 rounded-full"></div>
            <div className="w-8 h-0.5 bg-slate-600"></div>
            <Network className="w-5 h-5 text-purple-400" />
            <div className="w-8 h-0.5 bg-slate-600"></div>
            <div className="w-3 h-3 bg-red-400 rounded-full animate-pulse"></div>
          </div>
          <p className="text-xs text-slate-400 mt-2 text-center">Neural Network Processing</p>
        </div>
      ),
      span: 'col-span-1'
    },
    {
      title: 'Decision Support',
      description: 'Instant alerts and actionable intelligence delivered directly to decision-makers.',
      icon: <Smartphone className="w-8 h-8" />,
      mockup: (
        <div className="mt-4 p-4 bg-slate-800/50 rounded-lg">
          <div className="bg-slate-900 rounded-lg p-3 border border-red-500/30">
            <div className="flex items-center gap-2 mb-2">
              <Bell className="w-4 h-4 text-red-400" />
              <span className="text-sm font-semibold text-white">CRITICAL ALERT</span>
            </div>
            <p className="text-xs text-slate-300 mb-2">
              Escalation detected in Kaduna North. Risk level: HIGH
            </p>
            <div className="flex gap-2">
              <button className="px-2 py-1 bg-red-600 text-white text-xs rounded">View Details</button>
              <button className="px-2 py-1 bg-slate-700 text-slate-300 text-xs rounded">Dismiss</button>
            </div>
          </div>
        </div>
      ),
      span: 'col-span-1'
    }
  ];

  return (
    <section className="py-20 bg-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            How It Works
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            From raw data to actionable intelligence: our sovereign technology stack processes
            millions of data points to deliver unprecedented visibility into Nigeria&apos;s security landscape.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
              viewport={{ once: true }}
              className={`group relative ${feature.span}`}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-700/50 group-hover:border-slate-600/50 transition-all duration-300"></div>

              <div className="relative p-8 h-full">
                <div className="flex items-center gap-4 mb-6">
                  <div className="p-3 rounded-lg bg-slate-800/50 text-blue-400">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-bold text-white">
                    {feature.title}
                  </h3>
                </div>

                <p className="text-slate-300 mb-6 leading-relaxed">
                  {feature.description}
                </p>

                {/* Feature-specific content */}
                {feature.items && (
                  <div className="space-y-3">
                    {feature.items.map((item, itemIndex) => (
                      <div key={itemIndex} className="flex items-center gap-3">
                        <div className="text-slate-400">
                          {item.icon}
                        </div>
                        <span className="text-sm text-slate-300">{item.label}</span>
                      </div>
                    ))}
                  </div>
                )}

                {feature.visualization && feature.visualization}

                {feature.mockup && feature.mockup}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          viewport={{ once: true }}
          className="text-center mt-16"
        >
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-slate-800/50 rounded-lg border border-slate-700/50">
            <Shield className="w-5 h-5 text-green-400" />
            <span className="text-slate-300">End-to-end encrypted • Sovereign infrastructure • Zero data sharing</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
};