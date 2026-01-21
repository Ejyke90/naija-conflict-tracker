import { useState } from 'react'
import ForecastVisualization from '@/components/ForecastVisualization'

export default function ForecastsPage() {
  const [selectedLocation, setSelectedLocation] = useState('Borno')
  const [locationType, setLocationType] = useState<'state' | 'lga'>('state')
  
  // Top conflict states in Nigeria
  const states = [
    'Borno', 'Adamawa', 'Yobe',  // Northeast
    'Kaduna', 'Zamfara', 'Katsina', 'Sokoto',  // Northwest
    'Plateau', 'Benue',  // North-Central
    'Delta', 'Rivers'  // South
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Conflict Forecasting Dashboard
          </h1>
          <p className="text-lg text-gray-600">
            Advanced ML predictions using Prophet, ARIMA, and Ensemble models
          </p>
        </div>

        {/* Location Selector */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Select Location
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Location Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location Type
              </label>
              <div className="flex gap-4">
                <button
                  onClick={() => setLocationType('state')}
                  className={`px-6 py-2 rounded-lg font-medium transition ${
                    locationType === 'state'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  State
                </button>
                <button
                  onClick={() => setLocationType('lga')}
                  className={`px-6 py-2 rounded-lg font-medium transition ${
                    locationType === 'lga'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  LGA
                </button>
              </div>
            </div>

            {/* State/LGA Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {locationType === 'state' ? 'State' : 'LGA'}
              </label>
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {states.map((state) => (
                  <option key={state} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Info Banner */}
          <div className="mt-6 p-4 bg-blue-50 border-l-4 border-blue-600 rounded">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-blue-700">
                  Forecasts use historical conflict data to predict future incidents using advanced machine learning models.
                  Switch between Prophet, ARIMA, and Ensemble for model comparison.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Forecast Visualization */}
        <ForecastVisualization
          locationName={selectedLocation}
          locationType={locationType}
          weeksAhead={8}
        />

        {/* Additional Info */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Model Info */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Prophet Model
            </h3>
            <p className="text-sm text-gray-600 mb-2">
              Facebook's forecasting tool designed for time-series data with strong seasonal patterns.
            </p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>✓ Automatic seasonality detection</li>
              <li>✓ Trend changepoint identification</li>
              <li>✓ Holiday effects handling</li>
            </ul>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              ARIMA Model
            </h3>
            <p className="text-sm text-gray-600 mb-2">
              Statistical forecasting method that uses autoregressive integrated moving average.
            </p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>✓ Auto-parameter selection</li>
              <li>✓ Stationarity testing</li>
              <li>✓ Proven statistical rigor</li>
            </ul>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Ensemble Model
            </h3>
            <p className="text-sm text-gray-600 mb-2">
              Combines Prophet (50%), ARIMA (30%), and Linear (20%) for robust predictions.
            </p>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>✓ Weighted model averaging</li>
              <li>✓ Reduced prediction variance</li>
              <li>✓ Best overall accuracy</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            Data sourced from news articles, social media, and verified conflict databases.
            <br />
            Models retrained daily with latest conflict data.
          </p>
        </div>
      </div>
    </div>
  )
}
