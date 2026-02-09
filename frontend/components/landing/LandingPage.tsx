/* eslint-disable @next/next/no-img-element */
import React, { useState, useEffect } from 'react';
import { HeroSection } from './HeroSection';
import { LivePulse } from './LivePulse';
import { DashboardPeek } from './DashboardPeek';
import ForecastTeaser from '../forecasts/ForecastTeaser';

const LandingPage: React.FC = () => {
  const [forecastData, setForecastData] = useState({
    nextWeekPrediction: 23,
    trend: 12,
    confidence: 92,
    previewData: [] as Array<{ date: string; value: number }>
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch real forecast data from API
    const fetchForecastPreview = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        // Fetch Nigeria-wide forecast for landing page
        const response = await fetch(
          `${apiUrl}/api/v1/forecasts/advanced/Nigeria?location_type=state&model=ensemble&weeks_ahead=8`
        );

        if (response.ok) {
          const result = await response.json();
          
          // Extract preview data for sparkline
          const preview = result.forecast?.slice(0, 8).map((item: any) => ({
            date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            value: Math.round(item.predicted_incidents)
          })) || [];

          // Calculate metrics
          const nextWeek = result.forecast?.[0]?.predicted_incidents || 23;
          const currentWeek = result.metadata?.training_data_points || 20;
          const trendCalc = ((nextWeek - currentWeek) / currentWeek * 100).toFixed(0);
          const confidenceCalc = (result.metadata?.confidence_level * 100) || 92;

          setForecastData({
            nextWeekPrediction: Math.round(nextWeek),
            trend: parseInt(trendCalc),
            confidence: Math.round(confidenceCalc),
            previewData: preview
          });
        } else {
          // Fallback to reasonable defaults if API fails (landing page should still load)
          console.warn('Forecast API failed, using fallback data');
        }
      } catch (error) {
        console.error('Error fetching forecast preview:', error);
        // Keep default values on error
      } finally {
        setLoading(false);
      }
    };

    fetchForecastPreview();
  }, []);

  return (
    <div className="min-h-screen bg-slate-900">
      <HeroSection />
      <LivePulse />
      
      {/* AI-Powered Conflict Forecasting - Replaces How It Works section */}
      {!loading && (
        <section className="py-20 bg-slate-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <ForecastTeaser
              nextWeekPrediction={forecastData.nextWeekPrediction}
              trend={forecastData.trend}
              confidence={forecastData.confidence}
              previewData={forecastData.previewData}
            />
          </div>
        </section>
      )}
      
      <DashboardPeek />
    </div>
  );
};

export default LandingPage;
