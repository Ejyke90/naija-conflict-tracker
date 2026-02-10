/**
 * Simple performance monitoring utilities
 */

interface PerformanceMetric {
  type: 'click' | 'api';
  name: string;
  duration: number;
  timestamp: number;
}

class SimplePerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private readonly maxMetrics = 1000;
  private readonly clickThreshold = 100; // 100ms
  private readonly apiThreshold = 2000; // 2s

  recordClick(name: string, duration: number) {
    this.recordMetric({
      type: 'click',
      name,
      duration,
      timestamp: Date.now()
    });

    if (duration > this.clickThreshold) {
      console.warn(`⚠️ Slow click handler: ${name} took ${duration.toFixed(1)}ms`);
    }
  }

  recordApi(name: string, duration: number) {
    this.recordMetric({
      type: 'api',
      name,
      duration,
      timestamp: Date.now()
    });

    if (duration > this.apiThreshold) {
      console.warn(`⚠️ Slow API call: ${name} took ${duration.toFixed(1)}ms`);
    }
  }

  private recordMetric(metric: PerformanceMetric) {
    this.metrics.push(metric);
    
    // Keep only recent metrics
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics);
    }
  }

  wrapClickHandler(handler: () => void | Promise<void>, name: string) {
    return async () => {
      const startTime = performance.now();
      
      try {
        const result = handler();
        
        if (result instanceof Promise) {
          await result;
        }
        
        const endTime = performance.now();
        this.recordClick(name, endTime - startTime);
      } catch (error) {
        const endTime = performance.now();
        this.recordClick(name, endTime - startTime);
        console.error(`❌ Click handler error: ${name}`, error);
        throw error;
      }
    };
  }

  wrapApiCall<T>(apiCall: () => Promise<T>, name: string): Promise<T> {
    const startTime = performance.now();
    
    return apiCall()
      .then(result => {
        const endTime = performance.now();
        this.recordApi(name, endTime - startTime);
        return result;
      })
      .catch(error => {
        const endTime = performance.now();
        this.recordApi(name, endTime - startTime);
        console.error(`❌ API call error: ${name}`, error);
        throw error;
      });
  }

  getSummary() {
    const recentMetrics = this.metrics.slice(-100); // Last 100 metrics
    
    const clickMetrics = recentMetrics.filter(m => m.type === 'click');
    const apiMetrics = recentMetrics.filter(m => m.type === 'api');
    
    const avgClickTime = clickMetrics.length > 0 
      ? clickMetrics.reduce((sum, m) => sum + m.duration, 0) / clickMetrics.length 
      : 0;
    
    const avgApiTime = apiMetrics.length > 0
      ? apiMetrics.reduce((sum, m) => sum + m.duration, 0) / apiMetrics.length
      : 0;

    const slowClicks = clickMetrics.filter(m => m.duration > this.clickThreshold).length;
    const slowApis = apiMetrics.filter(m => m.duration > this.apiThreshold).length;

    return {
      totalMetrics: recentMetrics.length,
      avgClickTime,
      avgApiTime,
      slowClicks,
      slowApis,
      healthScore: Math.max(0, 100 - (slowClicks * 10) - (slowApis * 5))
    };
  }
}

export const performanceMonitor = new SimplePerformanceMonitor();

// Utility functions
export const wrapClick = (handler: () => void | Promise<void>, name: string) => {
  return performanceMonitor.wrapClickHandler(handler, name);
};

export const wrapApi = <T>(apiCall: () => Promise<T>, name: string) => {
  return performanceMonitor.wrapApiCall(apiCall, name);
};

export const getPerformanceSummary = () => {
  return performanceMonitor.getSummary();
};
