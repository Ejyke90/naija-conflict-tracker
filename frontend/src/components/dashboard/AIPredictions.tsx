import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { AlertCircle, TrendingUp, RefreshCw } from 'lucide-react';
import { getAccessToken } from '../../../contexts/AuthContext';

export default function AIPredictions() {
  const [forecasts, setForecasts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [state, setState] = useState("Borno");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchForecast() {
      setLoading(true);
      setError(null);
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        const token = getAccessToken();
        const headers: HeadersInit = {};
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        const res = await fetch(`${apiUrl}/api/v1/forecasts/advanced/${state}?location_type=state&weeks_ahead=4&model=prophet`, {
          headers
        });
        
        if (res.ok) {
          const data = await res.json();
          if (data.forecast) {
             setForecasts(data.forecast);
          } else if (data.error) {
             setError(data.error);
             setForecasts([]);
          } else {
             setForecasts([]); 
          }
        } else {
            // Check if 404/500
            if (res.status === 404) {
               setError("Forecast model not available for this region yet.");
            } else {
               const errText = await res.text();
               setError(`Failed to fetch forecast: ${res.statusText}`);
               console.error("Forecast error:", errText);
            }
        }
      } catch (e) {
        console.error(e);
        setError("Connection error");
      } finally {
        setLoading(false);
      }
    }
    fetchForecast();
  }, [state]);

  const states = ["Borno", "Kaduna", "Benue", "Plateau", "Zamfara", "Delta", "Lagos", "Abuja"];

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
            <TrendingUp className="w-64 h-64 text-indigo-500" />
        </div>
        
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-4 relative z-10">
        <div>
           <h3 className="text-lg font-bold text-gray-900 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-indigo-600" />
            AI Conflict Forecast
           </h3>
           <p className="text-sm text-gray-500">Predictive modeling using Prophet (4-week outlook)</p>
        </div>
        
        <div className="flex items-center gap-3">
             <select 
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="block w-full min-w-[150px] rounded-md border-gray-300 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6 px-3 bg-white"
             >
                {states.map(s => <option key={s} value={s}>{s} State</option>)}
             </select>
             
             {loading && <RefreshCw className="w-4 h-4 text-indigo-600 animate-spin" />}
        </div>
      </div>
      
      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-4 flex items-center text-sm border border-red-100">
            <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
            {error}
        </div>
      )}
      
      {!error && !loading && forecasts.length === 0 && (
         <div className="h-64 flex items-center justify-center text-gray-400 bg-gray-50 rounded-lg border border-dashed border-gray-300">
            No forecast data available for this region.
         </div>
      )}
      
      {!error && forecasts.length > 0 && (
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
            <LineChart data={forecasts} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                <XAxis 
                    dataKey="ds" 
                    tickFormatter={(val) => {
                        const d = new Date(val);
                        return `${d.getDate()}/${d.getMonth()+1}`;
                    }}
                    stroke="#9ca3af"
                    tick={{fontSize: 12}}
                />
                <YAxis stroke="#9ca3af" tick={{fontSize: 12}} />
                <Tooltip 
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}
                    labelFormatter={(label) => new Date(label).toLocaleDateString(undefined, {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'})}
                    formatter={(value: number) => [value.toFixed(1), "Predicted Incidents"]}
                />
                <Line 
                    type="monotone" 
                    dataKey="yhat" 
                    name="Prediction" 
                    stroke="#4f46e5" 
                    strokeWidth={3} 
                    dot={{ r: 4, fill: "#4f46e5", strokeWidth: 2, stroke: "#fff" }} 
                    activeDot={{ r: 6 }} 
                />
                <Line 
                    type="monotone" 
                    dataKey="yhat_upper" 
                    name="Upper Bound" 
                    stroke="#a5b4fc" 
                    strokeWidth={1} 
                    strokeDasharray="5 5" 
                    dot={false} 
                />
                <Line 
                    type="monotone" 
                    dataKey="yhat_lower" 
                    name="Lower Bound" 
                    stroke="#a5b4fc" 
                    strokeWidth={1} 
                    strokeDasharray="5 5" 
                    dot={false} 
                />
            </LineChart>
            </ResponsiveContainer>
          </div>
      )}
      
      <div className="mt-4 flex flex-wrap gap-4 text-xs text-gray-500 border-t border-gray-100 pt-4">
         <div className="flex items-center">
            <div className="w-3 h-0.5 bg-indigo-600 mr-2"></div>
            Predicted Incidents
         </div>
         <div className="flex items-center">
            <div className="w-3 h-0.5 bg-indigo-300 border-dashed mr-2"></div>
            95% Confidence Interval
         </div>
         <div className="ml-auto flex items-center text-gray-400">
            Model: Facebook Prophet
         </div>
      </div>
    </div>
  );
}
