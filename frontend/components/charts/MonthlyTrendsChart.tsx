'use client';

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceDot,
  Area,
  ComposedChart,
} from 'recharts';
import { TrendingUp, TrendingDown, AlertTriangle, Calendar, Package } from 'lucide-react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Skeleton } from '../ui/skeleton';
import { Button } from '../ui/button';

interface MonthlyDataPoint {
  month: string;
  incidents: number;
  fatalities: number;
  civilianCasualties: number;
  geographicSpread: number;
  incidentsTrend: number;
  fatalitiesTrend: number;
  isAnomalousIncidents: boolean;
  isAnomalousFatalities: boolean;
}

interface ForecastDataPoint {
  month: string;
  predictedIncidents: number;
  predictedFatalities: number;
  confidence: string;
}

interface MonthlyTrendsData {
  timeRange: {
    start: string;
    end: string;
    totalMonths: number;
  };
  state: string;
  data: MonthlyDataPoint[];
  summary: {
    avgIncidentsPerMonth: number;
    avgFatalitiesPerMonth: number;
    totalIncidents: number;
    totalFatalities: number;
    peakMonth: string;
    peakIncidents: number;
    anomalyCount: number;
    trendDirection: 'increasing' | 'decreasing';
  };
  dataQuality?: {
    recentDataAvailability: number;
    dataCompletenessWarning: boolean;
    lastSignificantMonth: string | null;
    historicalPeak: number;
    recentAverage: number;
  };
  forecast?: {
    method: string;
    periods: number;
    data: ForecastDataPoint[];
    note: string;
  };
}

interface MonthlyTrendsChartProps {
  monthsBack?: number;
  state?: string | null;
  includeForecast?: boolean;
}

export default function MonthlyTrendsChart({
  monthsBack = 12,  // Changed back to 12 months for reasonable default
  state = null,
  includeForecast = true,
}: MonthlyTrendsChartProps) {
  const [data, setData] = useState<MonthlyTrendsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'incidents' | 'fatalities'>('incidents');
  const [isCached, setIsCached] = useState(false);
  const [cachedAt, setCachedAt] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'ok' | 'degraded' | 'error'>('ok');
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);
  const [lastRetryTime, setLastRetryTime] = useState<number | null>(null);

  // Enhanced retry configuration with exponential backoff
  const maxRetries = 3;
  const baseDelay = 1000; // 1 second base delay
  const maxDelay = 10000; // 10 second max delay
  
  const calculateRetryDelay = (attemptNumber: number): number => {
    const exponentialDelay = baseDelay * Math.pow(2, attemptNumber - 1);
    const jitter = Math.random() * 0.1 * exponentialDelay; // Add 10% jitter to prevent thundering herd
    return Math.min(exponentialDelay + jitter, maxDelay);
  };
  
  const shouldRetry = (error: Error | string | null, currentRetryCount: number): boolean => {
    if (currentRetryCount >= maxRetries) return false;
    
    const errorMessage = typeof error === 'string' ? error : error?.message || '';
    
    // Don't retry on authentication errors or client errors (4xx)
    if (errorMessage.includes('401') || 
        errorMessage.includes('authenticate') ||
        errorMessage.includes('token') ||
        errorMessage.includes('unauthorized') ||
        errorMessage.includes('400') ||
        errorMessage.includes('403') ||
        errorMessage.includes('404')) {
      return false;
    }
    
    // Retry on network errors, timeouts, and server errors (5xx)
    return errorMessage.includes('timeout') ||
           errorMessage.includes('network') ||
           errorMessage.includes('Failed to fetch') ||
           errorMessage.includes('502') ||
           errorMessage.includes('503') ||
           errorMessage.includes('504') ||
           errorMessage.includes('gateway') ||
           errorMessage.includes('service unavailable') ||
           errorMessage.includes('connect') ||
           errorMessage.includes('ECONNRESET');
  };
  
  const sleep = (ms: number): Promise<void> => {
    return new Promise(resolve => setTimeout(resolve, ms));
  };

  useEffect(() => {
    const fetchData = async (attemptNumber: number = 1) => {
      try {
        setLoading(true);
        setError(null);
        setIsRetrying(attemptNumber > 1);
        
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 20000); // Increased to 20 second timeout
        
        const params = new URLSearchParams({
          months_back: monthsBack.toString(),
          include_forecast: includeForecast.toString(),
        });

        if (state) {
          params.append('state', state);
        }

        console.log(`MonthlyTrendsChart - Fetching data (attempt ${attemptNumber}/${maxRetries})`);
        
        const response = await fetch(`/api/v1/timeseries/monthly-trends?${params}`, {
          signal: controller.signal,
        });
        clearTimeout(timeout);
        
        if (!response.ok) {
          const errorText = await response.text().catch(() => 'Unknown error');
          throw new Error(`Failed to fetch trends: ${response.status} ${response.statusText} - ${errorText}`);
        }

        let responseData: any = await response.json();
        
        // First check if this is an error response
        if (responseData && (responseData.detail || responseData.error || responseData.message)) {
          console.error('MonthlyTrendsChart - API returned error:', responseData);
          throw new Error(responseData.detail || responseData.error || responseData.message || 'API error');
        }
        
        // Enhanced flexible data property detection with multiple strategies
        let isValidData = false;
        let validationReason = '';
        
        // Log the actual response structure for debugging
        console.log('MonthlyTrendsChart - Raw response:', {
          status: response.status,
          statusText: response.statusText,
          responseDataKeys: Object.keys(responseData || {}),
          responseData: responseData
        });
        
        // Strategy 1: Standard API response format with data property
        if (responseData && responseData.data && Array.isArray(responseData.data)) {
          if (responseData.data.length > 0) {
            isValidData = true;
            validationReason = 'Standard format with data array';
          } else {
            // Empty data array is still valid, just no data
            isValidData = true;
            validationReason = 'Standard format with empty data array';
          }
        }
        // Strategy 2: Direct array response (some endpoints return this)
        else if (Array.isArray(responseData)) {
          if (responseData.length > 0) {
            // Wrap direct array in expected format
            responseData = {
              data: responseData,
              state: state || 'Nigeria',
              timeRange: { start: '', end: '', totalMonths: responseData.length },
              summary: {
                avgIncidentsPerMonth: responseData.reduce((sum: number, item: any) => sum + (item.incidents || 0), 0) / responseData.length,
                avgFatalitiesPerMonth: responseData.reduce((sum: number, item: any) => sum + (item.fatalities || 0), 0) / responseData.length,
                totalIncidents: responseData.reduce((sum: number, item: any) => sum + (item.incidents || 0), 0),
                totalFatalities: responseData.reduce((sum: number, item: any) => sum + (item.fatalities || 0), 0),
                peakMonth: responseData[0]?.month || '',
                peakIncidents: Math.max(...responseData.map((item: any) => item.incidents || 0)),
                anomalyCount: 0,
                trendDirection: 'decreasing' as const,
              }
            };
            isValidData = true;
            validationReason = 'Direct array format wrapped';
          } else {
            // Empty direct array
            responseData = {
              data: [],
              state: state || 'Nigeria',
              timeRange: { start: '', end: '', totalMonths: 0 },
              summary: {
                avgIncidentsPerMonth: 0,
                avgFatalitiesPerMonth: 0,
                totalIncidents: 0,
                totalFatalities: 0,
                peakMonth: '',
                peakIncidents: 0,
                anomalyCount: 0,
                trendDirection: 'decreasing' as const,
              }
            };
            isValidData = true;
            validationReason = 'Empty direct array wrapped';
          }
        }
        // Strategy 3: Flexible data property detection
        else if (responseData && typeof responseData === 'object') {
          const possibleDataKeys = ['data', 'results', 'items', 'records', 'monthlyData', 'trends', 'timeSeries', 'monthlyData'];
          let foundDataKey = null;
          
          for (const key of possibleDataKeys) {
            if (responseData[key] && Array.isArray(responseData[key])) {
              // Found array data in this property
              if (responseData[key].length > 0 || key === 'data') {
                // Move the found data to the standard 'data' property
                responseData.data = responseData[key];
                foundDataKey = key;
                isValidData = true;
                validationReason = `Found data in '${key}' property`;
                break;
              }
            }
          }
          
          // If no data array found but object has expected structure, create empty data array
          if (!isValidData && responseData && typeof responseData === 'object') {
            const hasExpectedStructure = (
              'state' in responseData || 
              'timeRange' in responseData || 
              'summary' in responseData ||
              'status' in responseData ||
              'cached' in responseData
            );
            
            if (hasExpectedStructure) {
              responseData.data = responseData.data || [];
              isValidData = true;
              validationReason = 'Expected structure found, created empty data array';
            }
          }
          
          // Log data property detection results
          if (foundDataKey) {
            console.log(`MonthlyTrendsChart - Data property detection: moved '${foundDataKey}' to 'data'`);
          }
        }
        
        console.log('MonthlyTrendsChart - Validation Result:', {
          isValidData,
          validationReason,
          responseKeys: Object.keys(responseData || {}),
          hasData: !!responseData?.data,
          dataType: Array.isArray(responseData?.data) ? 'array' : typeof responseData?.data,
          dataLength: responseData?.data?.length
        });
        
        if (isValidData) {
          // API returns data directly, not wrapped in an array
          const result: MonthlyTrendsData = {
            state: responseData.state || 'Nigeria',
            timeRange: responseData.timeRange || { start: '', end: '', totalMonths: 0 },
            data: responseData.data,
            summary: responseData.summary || {
              avgIncidentsPerMonth: 0,
              avgFatalitiesPerMonth: 0,
              totalIncidents: 0,
              totalFatalities: 0,
              peakMonth: '',
              peakIncidents: 0,
              anomalyCount: 0,
              trendDirection: 'decreasing' as const,
            },
            forecast: responseData.forecast,
          };
          
          // Check if we have valid data structure but no actual data records
          if (result.data.length === 0 && result.timeRange.totalMonths > 0) {
            // This is a valid response with no data - don't treat as error
            setData(result);
            setIsCached(responseData.cached || false);
            setCachedAt(responseData.cached_at || null);
            setApiStatus('ok');
            setError(null);
          } else if (result.data.length > 0) {
            // Normal case with data
            setData(result);
            setIsCached(responseData.cached || false);
            setCachedAt(responseData.cached_at || null);
            setApiStatus(responseData.status as 'ok' | 'degraded' | 'error' || 'ok');
            setError(null);
          } else {
            // Edge case: no time range information
            const errorMessage = 'Unable to determine time range for analysis';
            setError(errorMessage);
            setData(null);
            setApiStatus('error');
          }
        } else {
          // Enhanced graceful error handling for empty or malformed responses
          const errorDetails = {
            responseData,
            hasResponse: !!responseData,
            hasData: !!responseData?.data,
            isArray: Array.isArray(responseData?.data),
            length: responseData?.data?.length,
            responseKeys: Object.keys(responseData || {}),
            validationReason: 'No valid data format found'
          };
          console.error('MonthlyTrendsChart - Data validation failed:', errorDetails);
          
          // Enhanced graceful error handling with context-aware messages
          let errorMessage = 'No conflict data available for this period';
          let errorSeverity = 'info';
          let suggestedActions: string[] = [];
          
          if (!responseData) {
            errorMessage = 'Unable to connect to the server';
            errorSeverity = 'error';
            suggestedActions = ['Check internet connection', 'Try refreshing the page', 'Contact support if issue persists'];
          } else if (responseData.detail || responseData.error) {
            // API error response
            errorMessage = responseData.detail || responseData.error || 'API error occurred';
            errorSeverity = 'error';
            suggestedActions = ['Try again in a few moments', 'Check if service is available'];
          } else if (Object.keys(responseData).length === 0) {
            errorMessage = 'Server returned empty response';
            errorSeverity = 'warning';
            suggestedActions = ['Refresh the page', 'Try a different time range'];
          } else if (!responseData.data && typeof responseData === 'object') {
            // Response exists but no data field
            const availableFields = Object.keys(responseData).filter(key => 
              typeof responseData[key] === 'object' && responseData[key] !== null
            );
            
            if (availableFields.length > 0) {
              errorMessage = `Data format unexpected. Found fields: ${availableFields.join(', ')}`;
              errorSeverity = 'warning';
              suggestedActions = ['Try refreshing the page', 'Contact support about data format'];
            } else {
              errorMessage = 'Server response missing data field';
              errorSeverity = 'error';
              suggestedActions = ['Contact support about API response format'];
            }
          } else if (!Array.isArray(responseData.data)) {
            errorMessage = 'Server returned invalid data format';
            errorSeverity = 'error';
            suggestedActions = ['Contact support about data format issue'];
          } else if (responseData.data.length === 0) {
            // Check if this is a valid empty response (has time range) vs actual error
            if (responseData.timeRange && responseData.timeRange.totalMonths > 0) {
              // This is a valid response with no data - not an error
              isValidData = true;
              validationReason = 'Valid empty response with time range';
            } else {
              // Empty data array - provide contextual help
              const timeRangeText = monthsBack ? `last ${monthsBack} months` : 'selected time period';
              const stateText = state ? ` in ${state}` : ' in Nigeria';
              
              errorMessage = `No conflict records found${stateText} for ${timeRangeText}`;
              errorSeverity = 'info';
              suggestedActions = [
                'Try a longer time range',
                'Try a different state',
                'Check if data exists for this period'
              ];
            }
          } else if (responseData.summary?.totalIncidents === 0) {
            errorMessage = 'No incidents recorded in the selected time period';
            errorSeverity = 'info';
            suggestedActions = ['Try a different time range', 'Explore other states'];
          }
          
          // Store enhanced error information for UI display
          setError(errorMessage);
          setData(null);
          setApiStatus(responseData?.status as 'ok' | 'degraded' | 'error' || 'error');
          setIsCached(responseData?.cached || false);
          setCachedAt(responseData?.cached_at || null);
          
          // Store additional error context for UI components
          (window as any).__monthlyTrendsErrorContext = {
            message: errorMessage,
            severity: errorSeverity,
            suggestedActions,
            details: errorDetails,
            timestamp: new Date().toISOString()
          };
        }
      } catch (err) {
        console.error(`MonthlyTrendsChart - Fetch error (attempt ${attemptNumber}/${maxRetries}):`, err);
        
        const errorObj = err instanceof Error ? err : new Error(String(err));
        
        // Check if we should retry
        if (shouldRetry(errorObj, attemptNumber)) {
          const retryDelay = calculateRetryDelay(attemptNumber);
          
          console.log(`MonthlyTrendsChart - Retrying in ${retryDelay}ms (attempt ${attemptNumber + 1}/${maxRetries})`);
          
          // Update retry state for UI
          setRetryCount(attemptNumber);
          setLastRetryTime(Date.now());
          
          // Wait before retrying
          await sleep(retryDelay);
          
          // Retry the request
          return fetchData(attemptNumber + 1);
        }
        
        // No more retries or error not retryable - handle the error
        setIsRetrying(false);
        
        if (errorObj.name === 'AbortError') {
          setError('Request timed out - data is taking too long to load');
          setApiStatus('degraded');
        } else if (errorObj.message.includes('401') || 
                   errorObj.message.includes('authenticate') ||
                   errorObj.message.includes('token') ||
                   errorObj.message.includes('unauthorized')) {
          setError('Authentication required. Please log in again.');
          setApiStatus('error');
          // Trigger auth context refresh
          window.dispatchEvent(new CustomEvent('auth:refresh-required'));
        } else if (errorObj.message.includes('502') ||
                   errorObj.message.includes('503') ||
                   errorObj.message.includes('504') ||
                   errorObj.message.includes('gateway') ||
                   errorObj.message.includes('service unavailable')) {
          const retryMessage = attemptNumber > 1 
            ? `Service temporarily unavailable after ${attemptNumber} attempts. Please try again later.`
            : 'Service temporarily unavailable. Please try again in a few moments.';
          setError(retryMessage);
          setApiStatus('error');
        } else if (errorObj.message.includes('timeout') ||
                   errorObj.message.includes('network')) {
          const retryMessage = attemptNumber > 1
            ? `Network connection issues persist after ${attemptNumber} attempts. Please check your connection.`
            : 'Network connection issue. Please check your internet connection.';
          setError(retryMessage);
          setApiStatus('degraded');
        } else {
          const retryMessage = attemptNumber > 1
            ? `Failed to load data after ${attemptNumber} attempts: ${errorObj.message}`
            : errorObj.message;
          setError(retryMessage);
          setApiStatus('error');
        }
      } finally {
        setLoading(false);
        setIsRetrying(false);
      }
    };

    // Reset retry count when parameters change
    setRetryCount(0);
    setLastRetryTime(null);
    fetchData();
  }, [monthsBack, state, includeForecast]);

  if (loading) {
    return (
      <div className="w-full space-y-4">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-64" />
            <Skeleton className="h-4 w-48 mt-2" />
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <Skeleton key={i} className="h-24 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-96 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !data) {
    // Get enhanced error context if available
    const errorContext = (window as any).__monthlyTrendsErrorContext;
    const suggestedActions = errorContext?.suggestedActions || [];
    const errorSeverity = errorContext?.severity || 'info';
    
    return (
      <Card className={`border-2 ${
        errorSeverity === 'error' ? 'border-red-200 bg-red-50/30' :
        errorSeverity === 'warning' ? 'border-orange-200 bg-orange-50/30' :
        'border-blue-200 bg-blue-50/30'
      }`}>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Calendar className={`h-5 w-5 ${
              errorSeverity === 'error' ? 'text-red-600' :
              errorSeverity === 'warning' ? 'text-orange-600' :
              'text-blue-600'
            }`} />
            Monthly Trends & Forecasting
            {isRetrying && (
              <Badge variant="outline" className="ml-2 animate-pulse">
                Retrying... ({retryCount}/{maxRetries})
              </Badge>
            )}
          </CardTitle>
          <CardDescription className="text-sm text-gray-600">
            Historical patterns and predictive analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="flex flex-col items-center justify-center py-12">
            <AlertTriangle className={`h-12 w-12 mb-4 ${
              errorSeverity === 'error' ? 'text-red-500' :
              errorSeverity === 'warning' ? 'text-orange-500' :
              'text-blue-500'
            }`} />
            
            <div className="text-center mb-6">
              <p className={`font-medium text-center mb-2 ${
                errorSeverity === 'error' ? 'text-red-700' :
                errorSeverity === 'warning' ? 'text-orange-700' :
                'text-blue-700'
              }`}>
                {error || 'No data available'}
              </p>
              
              {/* Show retry progress */}
              {isRetrying && lastRetryTime && (
                <div className="text-sm text-gray-600 mt-2">
                  <p>Automatic retry in progress...</p>
                  <p className="text-xs mt-1">Last attempt: {new Date(lastRetryTime).toLocaleTimeString()}</p>
                </div>
              )}
              
              {/* Show enhanced error context */}
              {errorContext && (
                <div className="text-xs text-gray-500 mt-2">
                  <p>Error type: {errorSeverity}</p>
                  {errorContext.timestamp && (
                    <p>Occurred: {new Date(errorContext.timestamp).toLocaleTimeString()}</p>
                  )}
                </div>
              )}
            </div>
            
            {/* Enhanced recovery options */}
            <div className="w-full max-w-md space-y-4">
              {/* Suggested actions */}
              {suggestedActions.length > 0 && (
                <div className="bg-white/50 rounded-lg p-4 border border-gray-200">
                  <p className="text-sm font-medium text-gray-700 mb-2">Suggested actions:</p>
                  <ul className="text-sm text-gray-600 space-y-1">
                    {suggestedActions.map((action: string, index: number) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-gray-400 mt-0.5">•</span>
                        <span>{action}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Recovery buttons */}
              <div className="flex flex-col sm:flex-row gap-2 justify-center">
                {/* Manual retry button */}
                {!isRetrying && shouldRetry(error, retryCount) && retryCount < maxRetries && (
                  <Button 
                    variant="default" 
                    size="sm" 
                    onClick={() => setRetryCount(prev => prev + 1)}
                    disabled={loading}
                    className="min-w-[120px]"
                  >
                    Retry Now ({retryCount}/{maxRetries})
                  </Button>
                )}
                
                {/* Refresh page button */}
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => window.location.reload()}
                  disabled={loading}
                  className="min-w-[120px]"
                >
                  Refresh Page
                </Button>
                
                {/* Change parameters button */}
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => {
                    // Reset to default parameters
                    const url = new URL(window.location.href);
                    url.searchParams.delete('state');
                    url.searchParams.delete('monthsBack');
                    window.location.href = url.toString();
                  }}
                  disabled={loading}
                  className="min-w-[120px]"
                >
                  Reset Filters
                </Button>
              </div>
              
              {/* Authentication specific recovery */}
              {error?.includes('Authentication') && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <p className="text-sm text-yellow-800 mb-2">
                    💡 Authentication issue detected
                  </p>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => {
                      // Trigger auth refresh
                      window.dispatchEvent(new CustomEvent('auth:refresh-required'));
                      // Also clear any stored auth state
                      localStorage.removeItem('auth_token');
                      sessionStorage.removeItem('auth_token');
                    }}
                    className="w-full"
                  >
                    Sign In Again
                  </Button>
                </div>
              )}
              
              {/* Service status indicator */}
              <div className="text-center text-xs text-gray-500">
                <p>Service Status: {apiStatus}</p>
                {cachedAt && (
                  <p>Last cached: {new Date(cachedAt).toLocaleDateString()}</p>
                )}
              </div>
            </div>
            
            {/* Debug info for development */}
            {process.env.NODE_ENV === 'development' && (
              <div className="text-center text-xs text-gray-500 mt-6">
                <details className="cursor-pointer">
                  <summary className="font-medium">Debug Information</summary>
                  <div className="text-left mt-2 p-3 bg-gray-100 rounded border border-gray-300">
                    <p><strong>Backend:</strong> {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</p>
                    <p><strong>Endpoint:</strong> /api/v1/timeseries/monthly-trends</p>
                    <p><strong>Params:</strong> months_back={monthsBack}, include_forecast={includeForecast}</p>
                    {state && <p><strong>State:</strong> {state}</p>}
                    <p><strong>Retry Count:</strong> {retryCount}/{maxRetries}</p>
                    <p><strong>Error Severity:</strong> {errorSeverity}</p>
                    {errorContext && (
                      <>
                        <p><strong>Error Context:</strong></p>
                        <pre className="text-xs bg-white p-2 rounded border border-gray-200 mt-1">
                          {JSON.stringify(errorContext.details, null, 2)}
                        </pre>
                      </>
                    )}
                  </div>
                </details>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  // Special case: Valid structure but no data records
  if (data && data.data.length === 0 && data.timeRange.totalMonths > 0) {
    return (
      <motion.div
        className="w-full space-y-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl">
                  Monthly Conflict Trends - {data.state}
                </CardTitle>
                <CardDescription>
                  {data.timeRange.start} to {data.timeRange.end} ({data.timeRange.totalMonths} months)
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center py-12">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Calendar className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No Conflict Data Available
                </h3>
                <p className="text-gray-600 mb-4">
                  No conflict records were found in {data.state} during the selected {data.timeRange.totalMonths}-month period.
                </p>
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-gray-400">0</p>
                      <p className="text-sm text-gray-600">Avg Incidents/Month</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-400">0</p>
                      <p className="text-sm text-gray-600">Avg Fatalities/Month</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-400">0</p>
                      <p className="text-sm text-gray-600">Total Incidents</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-400">0</p>
                      <p className="text-sm text-gray-600">Total Fatalities</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Action suggestions */}
              <div className="w-full max-w-md space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-blue-800 mb-2">
                    💡 Suggestions to find data:
                  </p>
                  <ul className="text-sm text-blue-700 space-y-1">
                    <li>• Try a longer time range (12, 24, or 60 months)</li>
                    <li>• Try different states with known conflict activity</li>
                    <li>• Check historical data from earlier periods</li>
                  </ul>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-2 justify-center">
                  <Button 
                    variant="default" 
                    size="sm" 
                    onClick={() => {
                      // Try 12 months instead
                      const url = new URL(window.location.href);
                      url.searchParams.set('monthsBack', '12');
                      window.location.href = url.toString();
                    }}
                    className="min-w-[120px]"
                  >
                    Try 12 Months
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => {
                      // Try 24 months
                      const url = new URL(window.location.href);
                      url.searchParams.set('monthsBack', '24');
                      window.location.href = url.toString();
                    }}
                    className="min-w-[120px]"
                  >
                    Try 24 Months
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => {
                      // Try high-activity states
                      const url = new URL(window.location.href);
                      url.searchParams.set('state', 'Borno');
                      url.searchParams.set('monthsBack', '24');
                      window.location.href = url.toString();
                    }}
                    className="min-w-[120px]"
                  >
                    Try Borno (24mo)
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  // Combine historical and forecast data for charting
  const combinedData = [...data.data];
  
  if (data.forecast) {
    data.forecast.data.forEach((forecast) => {
      combinedData.push({
        month: forecast.month,
        incidents: 0, // Will show as gap
        fatalities: 0,
        civilianCasualties: 0,
        geographicSpread: 0,
        incidentsTrend: isNaN(forecast.predictedIncidents) ? 0 : forecast.predictedIncidents,
        fatalitiesTrend: isNaN(forecast.predictedFatalities) ? 0 : forecast.predictedFatalities,
        isAnomalousIncidents: false,
        isAnomalousFatalities: false,
      });
    });
  }

  // Validate and clean data to prevent NaN values
  const cleanedData = combinedData.map(item => ({
    ...item,
    incidents: isNaN(item.incidents) ? 0 : item.incidents,
    fatalities: isNaN(item.fatalities) ? 0 : item.fatalities,
    civilianCasualties: isNaN(item.civilianCasualties) ? 0 : item.civilianCasualties,
    geographicSpread: isNaN(item.geographicSpread) ? 0 : item.geographicSpread,
    incidentsTrend: isNaN(item.incidentsTrend) ? 0 : item.incidentsTrend,
    fatalitiesTrend: isNaN(item.fatalitiesTrend) ? 0 : item.fatalitiesTrend,
  }));

  // Find anomalies for highlighting
  const anomalies = data.data.filter((d) =>
    viewMode === 'incidents' ? d.isAnomalousIncidents : d.isAnomalousFatalities
  );

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    const dataPoint = payload[0].payload;
    const isForecast = !dataPoint.incidents && !dataPoint.fatalities;

    return (
      <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-semibold text-gray-900 mb-2">{label}</p>
        {isForecast ? (
          <>
            <p className="text-sm text-blue-600 mb-1">📈 Forecast</p>
            <p className="text-sm">
              <span className="font-medium">Predicted {viewMode}:</span>{' '}
              {viewMode === 'incidents'
                ? dataPoint.incidentsTrend.toFixed(1)
                : dataPoint.fatalitiesTrend.toFixed(1)}
            </p>
          </>
        ) : (
          <>
            <p className="text-sm">
              <span className="font-medium">Incidents:</span> {dataPoint.incidents}
              {dataPoint.isAnomalousIncidents && (
                <span className="ml-2 text-red-600 font-bold">⚠️ SPIKE</span>
              )}
            </p>
            <p className="text-sm">
              <span className="font-medium">Fatalities:</span> {dataPoint.fatalities}
              {dataPoint.isAnomalousFatalities && (
                <span className="ml-2 text-red-600 font-bold">⚠️ SPIKE</span>
              )}
            </p>
            <p className="text-sm">
              <span className="font-medium">Civilian Deaths:</span> {dataPoint.civilianCasualties}
            </p>
            <p className="text-sm">
              <span className="font-medium">LGAs Affected:</span> {dataPoint.geographicSpread}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              <span className="font-medium">Trend (3mo avg):</span>{' '}
              {viewMode === 'incidents'
                ? dataPoint.incidentsTrend.toFixed(1)
                : dataPoint.fatalitiesTrend.toFixed(1)}
            </p>
          </>
        )}
      </div>
    );
  };

  return (
    <motion.div
      className="w-full space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header with Summary Stats */}
      <Card className={apiStatus === 'degraded' ? 'border-yellow-200 bg-yellow-50/30' : ''}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl">
                Monthly Conflict Trends - {data.state}
              </CardTitle>
              <CardDescription>
                {data.timeRange.start} to {data.timeRange.end} ({data.timeRange.totalMonths} months)
              </CardDescription>
            </div>
            
            <div className="flex items-center gap-2 flex-col">
              {/* Cached Data Badge */}
              {isCached && cachedAt && (
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${
                  apiStatus === 'degraded'
                    ? 'bg-yellow-100 text-yellow-800 border border-yellow-300'
                    : 'bg-blue-100 text-blue-800 border border-blue-300'
                }`}>
                  <Package className="h-3 w-3" />
                  <span>Cached • {cachedAt ? new Date(cachedAt).toLocaleDateString() : 'Unknown'}</span>
                  {apiStatus === 'degraded' && <span>⚠️ Degraded</span>}
                </div>
              )}

              <div className="flex items-center gap-2">
                <Button
                  onClick={() => setViewMode('incidents')}
                  variant={viewMode === 'incidents' ? 'default' : 'outline'}
                  size="sm"
                >
                  Incidents
                </Button>
                <Button
                  onClick={() => setViewMode('fatalities')}
                  variant={viewMode === 'fatalities' ? 'default' : 'outline'}
                  size="sm"
                  className={viewMode === 'fatalities' ? 'bg-destructive hover:bg-destructive/90' : ''}
                >
                  Fatalities
                </Button>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>

          {/* Summary Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <Card className="border-l-4 border-l-primary">
                <CardContent className="pt-6">
                  <div className="text-sm font-medium text-muted-foreground mb-2">Avg Incidents/Month</div>
                  <div className="text-2xl font-bold">
                    {data.summary.avgIncidentsPerMonth.toFixed(1)}
                  </div>
                  {data.dataQuality && (
                    <div className="text-xs text-muted-foreground mt-1">
                      Recent: {data.dataQuality.recentAverage}
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
              <Card className="border-l-4 border-l-destructive">
                <CardContent className="pt-6">
                  <div className="text-sm font-medium text-muted-foreground mb-2">Avg Fatalities/Month</div>
                  <div className="text-2xl font-bold">
                    {data.summary.avgFatalitiesPerMonth.toFixed(1)}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <Card className="border-l-4 border-l-blue-500">
                <CardContent className="pt-6">
                  <div className="text-sm font-medium text-muted-foreground mb-2">Peak Month</div>
                  <div className="text-lg font-bold">
                    {data.summary.peakMonth}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {data.summary.peakIncidents} incidents
                  </div>
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
              <Card className={`border-l-4 ${
                data.summary.trendDirection === 'increasing' ? 'border-l-red-500' : 'border-l-green-500'
              }`}>
                <CardContent className="pt-6">
                  <div className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-1">
                    Trend Direction
                    {data.summary.trendDirection === 'increasing' ? (
                      <TrendingUp className="h-4 w-4 text-red-500" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-green-500" />
                    )}
                  </div>
                  <div className="text-lg font-bold capitalize">
                    {data.summary.trendDirection}
                  </div>
                  {data.dataQuality?.dataCompletenessWarning && (
                    <div className="text-xs text-orange-600 mt-1">
                      ⚠️ Limited recent data
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Data Quality Alert */}
          {data.dataQuality && data.dataQuality.dataCompletenessWarning && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="bg-orange-50 border border-orange-200 rounded-lg p-4"
            >
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-orange-600 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-orange-800 mb-1">Data Availability Notice</h4>
                  <p className="text-sm text-orange-700 mb-2">
                    Recent conflict data shows significantly reduced activity compared to historical patterns.
                  </p>
                  <div className="text-xs text-orange-600 space-y-1">
                    <p>• Historical peak: {data.dataQuality.historicalPeak} incidents/month</p>
                    <p>• Recent average: {data.dataQuality.recentAverage} incidents/month</p>
                    <p>• Last significant activity: {data.dataQuality.lastSignificantMonth || 'None recorded'}</p>
                    <p>• Recent data availability: {Math.round(data.dataQuality.recentDataAvailability * 100)}%</p>
                  </div>
                  <div className="mt-3 text-xs text-orange-600">
                    <p className="font-medium">This may indicate:</p>
                    <ul className="list-disc list-inside mt-1 space-y-1">
                      <li>Reduced conflict activity in the region</li>
                      <li>Data collection issues or gaps</li>
                      <li>Reporting delays or system changes</li>
                    </ul>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {data.summary.anomalyCount > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-4"
            >
              <Card className="border-yellow-200 bg-yellow-50">
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-yellow-900">
                        {data.summary.anomalyCount} Anomal{data.summary.anomalyCount === 1 ? 'y' : 'ies'}{' '}
                        Detected
                      </p>
                      <p className="text-xs text-yellow-700">
                        Unusual conflict spikes identified using statistical analysis
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </CardContent>
      </Card>

      {/* Chart */}
      <Card>
        <CardContent className="pt-6">
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={cleanedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <defs>
              <linearGradient id="incidentsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="fatalitiesGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis 
              tick={{ fontSize: 12 }} 
              domain={[0, 'dataMax + 10']} 
              allowDecimals={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />

            {/* Area fill for actual data */}
            {viewMode === 'incidents' && (
              <Area
                type="monotone"
                dataKey="incidents"
                stroke="none"
                fill="url(#incidentsGradient)"
                name="Incidents"
              />
            )}
            {viewMode === 'fatalities' && (
              <Area
                type="monotone"
                dataKey="fatalities"
                stroke="none"
                fill="url(#fatalitiesGradient)"
                name="Fatalities"
              />
            )}

            {/* Actual data line */}
            <Line
              type="monotone"
              dataKey={viewMode === 'incidents' ? 'incidents' : 'fatalities'}
              stroke={viewMode === 'incidents' ? '#3b82f6' : '#ef4444'}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name={viewMode === 'incidents' ? 'Incidents' : 'Fatalities'}
            />

            {/* Trend line (moving average) */}
            <Line
              type="monotone"
              dataKey={viewMode === 'incidents' ? 'incidentsTrend' : 'fatalitiesTrend'}
              stroke={viewMode === 'incidents' ? '#1e40af' : '#991b1b'}
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="Trend (3mo avg)"
            />

            {/* Anomaly markers */}
            {anomalies.map((anomaly) => (
              <ReferenceDot
                key={anomaly.month}
                x={anomaly.month}
                y={viewMode === 'incidents' ? anomaly.incidents : anomaly.fatalities}
                r={8}
                fill="#ef4444"
                stroke="#fff"
                strokeWidth={2}
              />
            ))}
          </ComposedChart>
        </ResponsiveContainer>

        {data.forecast && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4"
          >
            <Card className="border-primary bg-primary/5">
              <CardContent className="pt-4 pb-4">
                <p className="text-sm font-medium mb-1">
                  📈 AI-Powered Conflict Forecasting
                </p>
                <p className="text-xs text-muted-foreground">{data.forecast.note}</p>
                <div className="mt-2 grid grid-cols-3 gap-2">
                  {data.forecast.data.map((f) => (
                    <Card key={f.month}>
                      <CardContent className="pt-3 pb-3 text-center">
                        <p className="text-xs font-medium text-muted-foreground">{f.month}</p>
                        <p className="text-sm font-bold">
                          {viewMode === 'incidents'
                            ? f.predictedIncidents.toFixed(1)
                            : f.predictedFatalities.toFixed(1)}
                        </p>
                        <Badge variant="outline" className="text-xs mt-1">{f.confidence}</Badge>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
