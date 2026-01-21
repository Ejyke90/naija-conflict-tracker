import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { AlertTriangle, MapPin, TrendingUp } from 'lucide-react';

const RiskAssessment: React.FC = () => {
  const riskData = [
    { name: 'Critical', value: 3, color: '#dc2626', percentage: 7 },
    { name: 'High', value: 8, color: '#ea580c', percentage: 17 },
    { name: 'Medium', value: 12, color: '#f59e0b', percentage: 26 },
    { name: 'Low', value: 23, color: '#22c55e', percentage: 50 }
  ];

  const totalAreas = riskData.reduce((sum, item) => sum + item.value, 0);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border">
          <p className="font-semibold text-slate-900">{data.name} Risk</p>
          <p className="text-slate-600">{data.value} areas ({data.percentage}%)</p>
        </div>
      );
    }
    return null;
  };

  const CustomLegend = (props: any) => {
    const { payload } = props;
    return (
      <div className="flex flex-wrap justify-center gap-4 mt-4">
        {payload.map((entry: any, index: number) => (
          <div key={`legend-${index}`} className="flex items-center space-x-2">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-sm font-medium text-slate-700">
              {entry.value} {entry.payload.name}
            </span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Risk Level Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2 text-amber-500" />
              Risk Distribution
            </h3>
            <span className="text-sm text-slate-500">{totalAreas} total areas</span>
          </div>
          
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend content={<CustomLegend />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Level Cards */}
        <div className="space-y-3">
          {riskData.map((risk) => (
            <div key={risk.name} className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-white/20 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-4 h-4 rounded-full shadow-sm" 
                    style={{ backgroundColor: risk.color }}
                  />
                  <span className="font-semibold text-slate-900">{risk.name} Risk</span>
                </div>
                <div className="flex items-center space-x-1">
                  <TrendingUp className="w-4 h-4 text-slate-400" />
                  <span className="text-sm font-medium text-slate-700">{risk.value}</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">areas monitored</span>
                <span className="text-sm font-medium text-slate-700">{risk.percentage}%</span>
              </div>
              <div className="mt-2 bg-slate-200 rounded-full h-2">
                <div 
                  className="h-full rounded-full transition-all duration-500" 
                  style={{ 
                    width: `${risk.percentage}%`,
                    backgroundColor: risk.color 
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Critical Areas Alert */}
      <div className="bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-xl p-4">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-red-600 mt-0.5" />
          <div>
            <h4 className="font-semibold text-red-900">Critical Risk Alert</h4>
            <p className="text-red-700 mt-1">
              {riskData.find(r => r.name === 'Critical')?.value} areas require immediate attention. 
              Enhanced monitoring and intervention recommended.
            </p>
            <div className="mt-3 flex items-center space-x-4">
              <div className="flex items-center space-x-1">
                <MapPin className="w-4 h-4 text-red-600" />
                <span className="text-sm text-red-700">3 high-risk zones</span>
              </div>
              <button className="text-sm font-medium text-red-700 hover:text-red-900 underline">
                View detailed report →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskAssessment;
