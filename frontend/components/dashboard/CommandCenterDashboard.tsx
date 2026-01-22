// frontend/components/dashboard/CommandCenterDashboard.tsx
import React, { useState } from 'react';
import { 
  BarChart3, 
  Map as MapIcon, 
  PieChart, 
  FileText, 
  Settings, 
  Search, 
  Bell, 
  ChevronRight, 
  Database,
  Menu,
  MoreVertical,
  Activity,
  ArrowUpRight,
  Filter
} from 'lucide-react';
import dynamic from 'next/dynamic';

// Dynamic import for the map to avoid SSR issues with Leaflet/Mapbox
const ConflictMap = dynamic(() => import('./MinimalMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-slate-100 animate-pulse flex items-center justify-center text-slate-400">
      Loading Map Data...
    </div>
  )
});

// Mock Data for Sparklines
const Sparkline = ({ data, color = "stroke-blue-500", fill = "fill-blue-500/10" }: { data: number[], color?: string, fill?: string }) => {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const width = 100;
  const height = 30;
  
  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((val - min) / range) * height; // Invert Y
    return `${x},${y}`;
  }).join(' ');

  const areaPoints = `${points} ${width},${height} 0,${height}`;

  return (
    <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} className="overflow-visible">
        <defs>
        <linearGradient id="gradient">
            <stop offset="0%" stopColor="currentColor" stopOpacity="0.2"/>
            <stop offset="100%" stopColor="currentColor" stopOpacity="0"/>
        </linearGradient>
        </defs>
      <path d={`M ${areaPoints}`} className={fill} stroke="none" />
      <polyline points={points} fill="none" className={`${color} stroke-[2]`} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

const KPICard = ({ title, value, trend, trendValue, sparkData, color }: {
  title: string;
  value: string;
  trend?: 'up' | 'down';
  trendValue?: string;
  sparkData?: number[];
  color: 'red' | 'amber' | 'green' | 'blue';
}) => {
  const colorMap = {
    red: { text: 'text-red-500', stroke: 'stroke-red-500', fill: 'fill-red-500/10', bg: 'bg-red-50' },
    amber: { text: 'text-amber-500', stroke: 'stroke-amber-500', fill: 'fill-amber-500/10', bg: 'bg-amber-50' },
    green: { text: 'text-green-500', stroke: 'stroke-green-500', fill: 'fill-green-500/10', bg: 'bg-green-50' },
    blue: { text: 'text-blue-500', stroke: 'stroke-blue-500', fill: 'fill-blue-500/10', bg: 'bg-blue-50' }
  };

  const theme = colorMap[color];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-4 flex flex-col justify-between h-28 relative overflow-hidden group hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start z-10">
        <div>
          <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-bold text-slate-800 mt-1">{value}</h3>
        </div>
        {trend && trendValue && (
            <div className={`flex items-center text-xs font-semibold px-2 py-1 rounded-full ${theme.bg} ${theme.text}`}>
               {trend === 'up' ? '↑' : '↓'} {trendValue}
            </div>
        )}
      </div>
      
      {sparkData && sparkData.length > 0 && (
          <div className="absolute bottom-0 left-0 right-0 h-12 w-full opacity-50 z-0">
              <Sparkline data={sparkData} color={theme.stroke} fill={theme.fill} />
          </div>
      )}
    </div>
  );
};

export const CommandCenterDashboard = () => {
    const [isSidebarCollapsed, setSidebarCollapsed] = useState(true);
    // Add active tab state for navigation
    const [activeTab, setActiveTab] = useState('dashboard');
    const [stats, setStats] = useState({
      totalIncidents: '0',
      fatalities: '0',
      activeHotspots: '0',
      statesAffected: '0'
    });
    const [incidents, setIncidents] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    React.useEffect(() => {
      const fetchData = async () => {
        try {
          const [statsRes, incidentsRes] = await Promise.all([
             fetch(`${API_URL}/api/dashboard/stats?days=30`),
             fetch(`${API_URL}/api/dashboard/recent-incidents?limit=20`)
          ]);

          if (statsRes.ok && incidentsRes.ok) {
            const statsData = await statsRes.json();
            const incidentsData = await incidentsRes.json();
            
            setStats({
              totalIncidents: (statsData.total_incidents || 0).toLocaleString(),
              fatalities: (statsData.total_fatalities || 0).toLocaleString(),
              activeHotspots: (statsData.active_hotspots || 0).toString(),
              statesAffected: (statsData.states_affected || 0).toString()
            });

            setIncidents(incidentsData.incidents.map((inc: any) => ({
                id: inc.id,
                location: inc.location,
                time: inc.date, // Needs formatting
                type: inc.type,
                severity: inc.fatalities > 0 ? 'high' : 'medium', // Simple logic
                details: inc.description || `Incident reported in ${inc.location}`
            })));
          }
        } catch (error) {
          console.error("Failed to fetch dashboard data", error);
        } finally {
            setLoading(false);
        }
      };

      fetchData();
    }, []);

  return (
    <div className="flex h-screen w-full bg-slate-50 font-sans text-slate-900 overflow-hidden">
      
      {/* Sidebar - Slim, Collapsible */}
      <aside className={`bg-white border-r border-slate-200 flex-shrink-0 transition-all duration-300 ${isSidebarCollapsed ? 'w-16' : 'w-64'} flex flex-col items-center py-4 z-20`}>
        <div className="mb-8 p-2">
            <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-indigo-200">
                N
            </div>
        </div>

        <nav className="flex-1 w-full flex flex-col gap-2 px-2">
            {[
                { id: 'dashboard', icon: BarChart3, label: "Dashboard" },
                { id: 'map', icon: MapIcon, label: "Map" },
                { id: 'analytics', icon: PieChart, label: "Analytics" },
                { id: 'reports', icon: FileText, label: "Reports" },
                { id: 'pipeline', icon: Database, label: "Pipeline" },
            ].map((item) => (
                <button 
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center p-3 rounded-lg transition-colors group relative ${
                        activeTab === item.id 
                        ? 'bg-indigo-50 text-indigo-600' 
                        : 'text-slate-500 hover:bg-slate-100 hover:text-slate-800'
                    }`}
                >
                    <item.icon size={22} strokeWidth={1.5} />
                    {!isSidebarCollapsed && <span className="ml-3 font-medium text-sm">{item.label}</span>}
                    {/* Tooltip for collapsed state */}
                    {isSidebarCollapsed && (
                        <div className="absolute left-full ml-2 px-2 py-1 bg-slate-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
                            {item.label}
                        </div>
                    )}
                </button>
            ))}
        </nav>

        <div className="w-full px-2 mt-auto">
             <button 
                onClick={() => setSidebarCollapsed(!isSidebarCollapsed)}
                className="w-full flex items-center p-3 text-slate-500 hover:bg-slate-100 rounded-lg"
            >
                {isSidebarCollapsed ? <Menu size={22} /> : <div className="flex items-center"><Menu size={22} /><span className="ml-3 text-sm">Collapse</span></div>}
            </button>
            <button className="w-full flex items-center p-3 text-slate-500 hover:bg-slate-100 rounded-lg">
                <Settings size={22} />
            </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        
        {/* Global Header */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 flex-shrink-0 shadow-sm z-10">
            <div className="flex items-center gap-4">
                <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700">Nextier Conflict Tracker</h1>
                <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-slate-100 rounded-full border border-slate-200">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                    </span>
                    <span className="text-xs font-semibold text-slate-600 uppercase">Live: Monitoring</span>
                </div>
            </div>

            <div className="flex items-center gap-4">
                <div className="relative hidden md:block group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-indigo-500 transition-colors" size={18} />
                    <input 
                        type="text" 
                        placeholder="Search locations, events..." 
                        className="pl-10 pr-4 py-2 bg-slate-50 border-none rounded-full text-sm w-64 focus:ring-2 focus:ring-indigo-100 focus:bg-white transition-all text-slate-700 placeholder-slate-400"
                    />
                </div>
                
                <button className="relative p-2 text-slate-500 hover:bg-slate-100 rounded-full transition-colors">
                    <Bell size={20} />
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
                </button>
                
                <div className="flex items-center gap-2 pl-4 border-l border-slate-200">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 text-white flex items-center justify-center font-bold text-xs ring-2 ring-white shadow-sm">
                        JD
                    </div>
                </div>
            </div>
        </header>

        {/* Dashboard Content */}
        <div className="flex-1 flex flex-col p-4 md:p-6 gap-6 overflow-hidden">
            
            {/* KPI Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 flex-shrink-0">
                <KPICard 
                    title="Total Incidents (30d)" 
                    value={stats.totalIncidents} 
                    color="red"
                />
                 <KPICard 
                    title="Fatalities" 
                    value={stats.fatalities} 
                    color="amber"
                />
                 <KPICard 
                    title="Active Hotspots" 
                    value={stats.activeHotspots} 
                    color="red"
                />
                 <KPICard 
                    title="States Affected" 
                    value={stats.statesAffected} 
                    color="blue"
                />
            </div>

            {/* Main Split View */}
            <div className="flex-1 flex flex-col lg:flex-row gap-6 min-h-0">
                
                {/* Map Area (70%) */}
                <div className="lg:w-[70%] bg-white rounded-xl shadow-sm border border-slate-200 relative overflow-hidden flex flex-col">
                    <div className="absolute top-4 left-4 z-10 flex gap-2">
                        <button className="bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded-lg shadow-sm border border-slate-200 text-xs font-semibold text-slate-700 flex items-center gap-2 hover:bg-white transition-colors">
                            <MapIcon size={14} /> All States
                        </button>
                         <button className="bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded-lg shadow-sm border border-slate-200 text-xs font-semibold text-slate-700 flex items-center gap-2 hover:bg-white transition-colors">
                            <Filter size={14} /> Filter Risk
                        </button>
                    </div>
                    

                    <div className="flex-1 w-full bg-slate-100 relative">
                         <div className="absolute inset-0">
                            {/* Pass data to map if needed, or implement map interaction */}
                            {/* Only render map when tab is dashboard or map */}
                            {(activeTab === 'dashboard' || activeTab === 'map') && (
                                <ConflictMap incidents={incidents} />
                            )}
                            {activeTab !== 'dashboard' && activeTab !== 'map' && (
                                <div className="flex items-center justify-center h-full text-slate-400">
                                    {activeTab === 'analytics' && "Analytics Module Loading..."}
                                    {activeTab === 'reports' && "Reports Module Loading..."}
                                    {activeTab === 'pipeline' && "Data Pipeline Status..."}
                                </div>
                            )}
                         </div>
                    </div>
                </div>

                {/* Live Incident Feed (30%) */}
                <div className="lg:w-[30%] flex flex-col gap-4 min-h-0 bg-white rounded-xl shadow-sm border border-slate-200 p-4">
                    <div className="flex items-center justify-between flex-shrink-0">
                        <h2 className="font-bold text-slate-800 flex items-center gap-2">
                             <Activity size={18} className="text-red-500" />
                            Live Incident Feed
                        </h2>
                        <button className="text-xs text-indigo-600 hover:text-indigo-800 font-medium">View All</button>
                    </div>

                    <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
                        {loading ? (
                             <div className="text-center py-10 text-slate-400">Loading incidents...</div>
                        ) : incidents.length === 0 ? (
                             <div className="text-center py-10 text-slate-400">No recent incidents found.</div>
                        ) : (
                            incidents.map((incident) => (
                            <div key={incident.id} className={`p-3 rounded-lg border-l-4 ${
                                incident.severity === 'high' ? 'border-l-red-500 bg-red-50/50' : 
                                incident.severity === 'medium' ? 'border-l-amber-500 bg-amber-50/50' : 'border-l-blue-500 bg-blue-50/50'
                                } hover:bg-slate-50 transition-colors group cursor-pointer border-t border-r border-b border-t-slate-100 border-r-slate-100 border-b-slate-100`}
                            >
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-xs font-bold text-slate-700">{incident.location}</span>
                                    <span className="text-[10px] text-slate-400 font-medium bg-white px-1.5 py-0.5 rounded border border-slate-100">{incident.time}</span>
                                </div>
                                <h4 className="text-sm font-semibold text-slate-900 mb-1 leading-tight">{incident.type}</h4>
                                <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">{incident.details}</p>
                            </div>
                        )))}
                    </div>
                </div>
            </div>
        </div>
      </main>
    </div>
  );
};

export default CommandCenterDashboard;
