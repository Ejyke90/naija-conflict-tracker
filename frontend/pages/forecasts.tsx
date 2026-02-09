import { useState, useEffect } from 'react'
import ForecastVisualization from '../components/ForecastVisualization'
import ProtectedRoute from '../components/ProtectedRoute'
import ForecastHero from '../components/forecasts/ForecastHero'
import ForecastMainChart from '../components/forecasts/ForecastMainChart'

function ForecastsPageContent() {
  const [selectedLocation, setSelectedLocation] = useState('Nigeria')
  const [locationType, setLocationType] = useState<'state' | 'lga'>('state')
  const [selectedModel, setSelectedModel] = useState('ensemble')
  const [forecastData, setForecastData] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [currentMonthSummary, setCurrentMonthSummary] = useState({
    incidents: 87,
    change: 12,
    accuracy: 92
  })
  
  // Top conflict states in Nigeria
  const states = [
    'Borno', 'Zamfara', 'Kaduna', // Top 3 high fatalities
    'Adamawa', 'Yobe', 'Katsina', 'Sokoto',  // High risk
    'Plateau', 'Benue', 'Niger', // Medium risk
    'Delta', 'Rivers', 'Taraba'  // Others
  ]

  useEffect(() => {
    // Fetch forecast data when location or model changes
    const fetchForecastData = async () => {
      setLoading(true)
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(
          `${apiUrl}/api/v1/forecasts/advanced/${selectedLocation}?` +
          `location_type=${locationType}&model=${selectedModel}&weeks_ahead=12`
        )
        
        if (response.ok) {
          const result = await response.json()
          // Transform data for the chart
          const transformedData = result.forecast?.map((item: any) => ({
            date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            predicted: item.predicted_incidents,
            lower: item.lower_bound,
            upper: item.upper_bound,
            confidence: item.confidence_interval_width
          })) || []
          setForecastData(transformedData)
        }
      } catch (error) {
        console.error('Error fetching forecast:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchForecastData()
  }, [selectedLocation, selectedModel, locationType])

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Hero Section */}
        <div className="mb-8">
          <ForecastHero
            selectedState={selectedLocation}
            onStateChange={setSelectedLocation}
            currentMonthSummary={currentMonthSummary}
            states={states}
          />
        </div>

        {/* Main Forecast Chart */}
        <div className="mb-8">
          <ForecastMainChart
            data={forecastData}
            selectedModel={selectedModel}
            onModelChange={setSelectedModel}
            loading={loading}
          />
        </div>

        {/* Legacy Forecast Visualization (Detailed view) */}
        <div className="mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Detailed Forecast Analysis
            </h2>
            <ForecastVisualization
              location={selectedLocation}
              locationType={locationType}
              model={selectedModel as any}
              weeksAhead={12}
            />
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Model Info */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Prophet Model
            </h3>
            <p className="text-sm text-gray-600 mb-2">
              Facebook&apos;s forecasting tool designed for time-series data with strong seasonal patterns.
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

export default function ForecastsPage() {
  return (
    <ProtectedRoute requiredRole="viewer">
      <ForecastsPageContent />
    </ProtectedRoute>
  )
}
