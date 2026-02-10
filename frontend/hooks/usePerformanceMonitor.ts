import { useEffect, useRef, useCallback } from 'react';
import { performanceMonitor } from '../services/performanceMonitor';

interface UsePerformanceMonitorOptions {
  componentName?: string;
  trackClicks?: boolean;
  trackApiCalls?: boolean;
  alertThreshold?: number;
}

export function usePerformanceMonitor(options: UsePerformanceMonitorOptions = {}) {
  const {
    componentName = 'Component',
    trackClicks = true,
    trackApiCalls = true,
    alertThreshold = 80
  } = options;

  // Method to wrap click handlers with performance monitoring
  const wrapClick = useCallback(
    (handler: (event: React.MouseEvent) => void | Promise<void>, name?: string) => {
      if (!trackClicks) return handler;
      
      const handlerName = name || `${componentName}-click`;
      return performanceMonitor.wrapClickHandler(handler, handlerName) as (event: React.MouseEvent) => void;
    },
    [componentName, trackClicks]
  );

  // Method to track API calls
  const trackApi = useCallback(<T>(
    apiCall: () => Promise<T>,
    endpoint?: string
  ) => {
    if (!trackApiCalls) return apiCall;
    
    const apiEndpoint = endpoint || `${componentName}-api`;
    return performanceMonitor.trackApiCall(apiCall, apiEndpoint);
  }, [componentName, trackApiCalls]);

  // Method to get current performance data
  const getPerformanceData = useCallback(() => {
    const metrics = performanceMonitor.getMetrics();
    const alerts = performanceMonitor.getAlerts();
    const summary = performanceMonitor.getPerformanceSummary();
    
    return {
      metrics,
      alerts,
      summary,
      isHealthy: summary.healthScore >= alertThreshold
    };
  }, [alertThreshold]);

  // Method to check if component is healthy
  const checkHealth = useCallback(() => {
    const data = getPerformanceData();
    return data.isHealthy;
  }, [getPerformanceData]);

  // Log component mount/unmount for performance tracking
  useEffect(() => {
    const mountTime = performance.now();
    console.log(`🚀 Component mounted: ${componentName} at ${mountTime.toFixed(1)}ms`);
    
    return () => {
      const unmountTime = performance.now();
      const duration = unmountTime - mountTime;
      console.log(`🔄 Component unmounted: ${componentName} after ${duration.toFixed(1)}ms`);
    };
  }, [componentName]);

  return {
    wrapClick,
    trackApi,
    getPerformanceData,
    checkHealth
  };
}

export default usePerformanceMonitor;
