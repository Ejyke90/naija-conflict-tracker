import React, { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';

interface SeasonalPatternChartProps {
  state?: string;
  monthsBack?: number;
}

const SeasonalPatternChart: React.FC<SeasonalPatternChartProps> = ({ 
  state, 
  monthsBack = 12 
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // TODO: Temporarily disabled to prevent 500 error loops
        // const params = new URLSearchParams();
        // if (state) {
        //   params.append('state', state);
        // }

        // const queryString = params.toString();
        // const url = `/api/v1/timeseries/seasonal-analysis${queryString ? `?${queryString}` : ''}`;
        // const response = await fetch(url);

        // if (!response.ok) {
        //   throw new Error(`Failed to fetch seasonal data: ${response.statusText}`);
        // }

        // const responseData: any = await response.json();
        
        // if (responseData && responseData.seasonalPattern && responseData.seasonalPattern.length > 0) {
        //   // Process data...
        // } else {
        //   setError(responseData.message || 'No seasonal pattern data available');
        // }
        
        // Set loading to false by default
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [state]);

  if (loading) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading seasonal patterns...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-red-50 rounded-lg">
        <div className="text-center text-red-600">
          <AlertTriangle className="h-12 w-12 mx-auto mb-4" />
          <p>{error}</p>
        </div>
      </div>
    );
  }

  // Return placeholder when API is disabled
  return (
    <div className="w-full h-96 flex items-center justify-center bg-gray-50 rounded-lg">
      <div className="text-center text-gray-600">
        <AlertTriangle className="h-12 w-12 mx-auto mb-4" />
        <p>Seasonal analysis temporarily disabled</p>
      </div>
    </div>
  );
};

export default SeasonalPatternChart;
