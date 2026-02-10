/**
 * Performance Monitoring Service
 * Tracks click handler performance, API response times, and component health
 */

interface PerformanceMetric {
  type: 'click' | 'api' | 'render' | 'data-load';
  name: string;
  startTime: number;
  endTime: number;
  duration: number;
  timestamp: Date;
  metadata?: Record<string, any>;
}

interface PerformanceAlert {
  type: 'slow-click' | 'slow-api' | 'failed-load' | 'render-error';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  metric: PerformanceMetric;
  suggestions: string[];
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private alerts: PerformanceAlert[] = [];
  private observers: PerformanceObserver[] = [];
  private thresholds = {
    clickHandler: 100, // ms - click handlers should be under 100ms
    apiResponse: 2000, // ms - API responses under 2s
    dataLoad: 5000, // ms - data loading under 5s
    render: 16, // ms - 60fps render target
  };

  constructor() {
    this.initializeObservers();
    this.setupGlobalErrorHandling();
  }

  private initializeObservers() {
    // Observe long tasks
    if ('PerformanceObserver' in window) {
      const longTaskObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > this.thresholds.clickHandler) {
            this.createAlert({
              type: 'slow-click',
              severity: 'high',
              message: `Long task detected: ${entry.duration.toFixed(1)}ms`,
              metric: {
                type: 'click',
                name: 'long-task',
                startTime: entry.startTime,
                endTime: entry.startTime + entry.duration,
                duration: entry.duration,
                timestamp: new Date(),
                metadata: { entryType: entry.entryType, name: entry.name }
              },
              suggestions: [
                'Break up large computations',
                'Use Web Workers for heavy processing',
                'Implement debouncing/throttling',
                'Move operations off main thread'
              ]
            });
          }
        }
      });
      
      longTaskObserver.observe({ entryTypes: ['longtask'] });
      this.observers.push(longTaskObserver);
    }
  }

  private setupGlobalErrorHandling() {
    // Track unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.createAlert({
        type: 'render-error',
        severity: 'critical',
        message: `Unhandled promise rejection: ${event.reason}`,
        metric: {
          type: 'render',
          name: 'unhandled-rejection',
          startTime: Date.now(),
          endTime: Date.now(),
          duration: 0,
          timestamp: new Date(),
          metadata: { reason: event.reason }
        },
        suggestions: [
          'Add proper error boundaries',
          'Implement promise error handling',
          'Check for missing await statements',
          'Verify API error handling'
        ]
      });
    });

    // Track performance entries
    this.trackNavigationTiming();
  }

  private trackNavigationTiming() {
    if ('performance' in window && 'getEntriesByType' in performance) {
      const navigationEntries = performance.getEntriesByType('navigation') as PerformanceNavigationTiming[];
      navigationEntries.forEach(entry => {
        const loadTime = entry.loadEventEnd - entry.loadEventStart;
        if (loadTime > this.thresholds.dataLoad) {
          this.createAlert({
            type: 'slow-api',
            severity: 'medium',
            message: `Page load took ${loadTime.toFixed(1)}ms`,
            metric: {
              type: 'data-load',
              name: 'page-load',
              startTime: entry.loadEventStart,
              endTime: entry.loadEventEnd,
              duration: loadTime,
              timestamp: new Date(),
              metadata: { 
                domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
                firstPaint: entry.responseStart - entry.requestStart
              }
            },
            suggestions: [
              'Optimize bundle size',
              'Implement code splitting',
              'Add lazy loading',
              'Check server response times'
            ]
          });
        }
      });
    }
  }

  // Method to wrap click handlers with performance monitoring
  wrapClickHandler<T = Event>(
    handler: (event: T) => void | Promise<void>,
    name: string
  ): (event: T) => void {
    return (event: T) => {
      const startTime = performance.now();
      
      try {
        const result = handler(event);
        
        // Handle async handlers
        if (result instanceof Promise) {
          result
            .then(() => {
              this.recordMetric({
                type: 'click',
                name,
                startTime,
                endTime: performance.now(),
                duration: performance.now() - startTime,
                timestamp: new Date()
              });
            })
            .catch((error) => {
              this.recordMetric({
                type: 'click',
                name,
                startTime,
                endTime: performance.now(),
                duration: performance.now() - startTime,
                timestamp: new Date(),
                metadata: { error: error.message }
              });
              
              this.createAlert({
                type: 'render-error',
                severity: 'high',
                message: `Click handler failed: ${name} - ${error.message}`,
                metric: {
                  type: 'click',
                  name,
                  startTime,
                  endTime: performance.now(),
                  duration: performance.now() - startTime,
                  timestamp: new Date(),
                  metadata: { error: error.message }
                },
                suggestions: [
                  'Add error handling to click handler',
                  'Check for missing error boundaries',
                  'Verify async/await usage',
                  'Add try-catch blocks'
                ]
              });
            });
        } else {
          // Sync handler completed
          const endTime = performance.now();
          this.recordMetric({
            type: 'click',
            name,
            startTime,
            endTime,
            duration: endTime - startTime,
            timestamp: new Date()
          });
          
          // Alert on slow sync handlers
          if (endTime - startTime > this.thresholds.clickHandler) {
            this.createAlert({
              type: 'slow-click',
              severity: 'high',
              message: `Slow click handler: ${name} took ${(endTime - startTime).toFixed(1)}ms`,
              metric: {
                type: 'click',
                name,
                startTime,
                endTime,
                duration: endTime - startTime,
                timestamp: new Date()
              },
              suggestions: [
                'Move heavy computations to Web Workers',
                'Implement debouncing for frequent events',
                'Break up large operations',
                'Use requestIdleCallback for non-critical work'
              ]
            });
          }
        }
      } catch (error) {
        const endTime = performance.now();
        this.recordMetric({
          type: 'click',
          name,
          startTime,
          endTime,
          duration: endTime - startTime,
          timestamp: new Date(),
          metadata: { error: (error as Error).message }
        });
        
        this.createAlert({
          type: 'render-error',
          severity: 'critical',
          message: `Click handler error: ${name} - ${(error as Error).message}`,
          metric: {
            type: 'click',
            name,
            startTime,
            endTime,
            duration: endTime - startTime,
            timestamp: new Date(),
            metadata: { error: (error as Error).message }
          },
          suggestions: [
            'Add try-catch error handling',
            'Implement proper error boundaries',
            'Check for undefined/null values',
            'Validate input parameters'
          ]
        });
      }
    };
  }

  // Method to track API calls
  trackApiCall<T>(
    apiCall: () => Promise<T>,
    endpoint: string
  ): Promise<T> {
    const startTime = performance.now();
    
    return apiCall()
      .then(result => {
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        this.recordMetric({
          type: 'api',
          name: endpoint,
          startTime,
          endTime,
          duration,
          timestamp: new Date()
        });
        
        if (duration > this.thresholds.apiResponse) {
          this.createAlert({
            type: 'slow-api',
            severity: 'medium',
            message: `Slow API response: ${endpoint} took ${duration.toFixed(1)}ms`,
            metric: {
              type: 'api',
              name: endpoint,
              startTime,
              endTime,
              duration,
              timestamp: new Date()
            },
            suggestions: [
              'Check backend query performance',
              'Implement response caching',
              'Add pagination or filtering',
              'Optimize database queries'
            ]
          });
        }
        
        return result;
      })
      .catch(error => {
        const endTime = performance.now();
        const duration = endTime - startTime;
        
        this.recordMetric({
          type: 'api',
          name: endpoint,
          startTime,
          endTime,
          duration,
          timestamp: new Date(),
          metadata: { error: error.message }
        });
        
        this.createAlert({
          type: 'failed-load',
          severity: 'high',
          message: `API call failed: ${endpoint} - ${error.message}`,
          metric: {
            type: 'api',
            name: endpoint,
            startTime,
            endTime,
            duration,
            timestamp: new Date(),
            metadata: { error: error.message }
          },
          suggestions: [
            'Check network connectivity',
            'Verify API endpoint availability',
            'Implement retry logic',
            'Add proper error handling'
          ]
        });
        
        throw error;
      });
  }

  private recordMetric(metric: PerformanceMetric) {
    this.metrics.push(metric);
    
    // Keep only last 1000 metrics to prevent memory issues
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000);
    }
    
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`🔍 Performance [${metric.type}]: ${metric.name} - ${metric.duration.toFixed(1)}ms`);
    }
  }

  private createAlert(alert: PerformanceAlert) {
    this.alerts.push(alert);
    
    // Keep only last 100 alerts
    if (this.alerts.length > 100) {
      this.alerts = this.alerts.slice(-100);
    }
    
    // Log alerts to console
    console.warn(`⚠️ Performance Alert [${alert.severity}]: ${alert.message}`, alert);
    
    // In production, you might want to send critical alerts to monitoring service
    if (alert.severity === 'critical' && process.env.NODE_ENV === 'production') {
      // TODO: Send to monitoring service
      console.error('🚨 Critical performance alert:', alert);
    }
  }

  // Public methods for getting performance data
  getMetrics(type?: string, timeRange?: number): PerformanceMetric[] {
    let filtered = this.metrics;
    
    if (type) {
      filtered = filtered.filter(m => m.type === type);
    }
    
    if (timeRange) {
      const cutoff = Date.now() - timeRange;
      filtered = filtered.filter(m => m.timestamp.getTime() > cutoff);
    }
    
    return filtered;
  }

  getAlerts(severity?: string, timeRange?: number): PerformanceAlert[] {
    let filtered = this.alerts;
    
    if (severity) {
      filtered = filtered.filter(a => a.severity === severity);
    }
    
    if (timeRange) {
      const cutoff = Date.now() - timeRange;
      filtered = filtered.filter(a => a.metric.timestamp.getTime() > cutoff);
    }
    
    return filtered;
  }

  getPerformanceSummary() {
    const recentMetrics = this.getMetrics(undefined, 300000); // Last 5 minutes
    const recentAlerts = this.getAlerts(undefined, 300000);
    
    const avgClickTime = recentMetrics
      .filter(m => m.type === 'click')
      .reduce((sum, m) => sum + m.duration, 0) / recentMetrics.filter(m => m.type === 'click').length || 0;
    
    const avgApiTime = recentMetrics
      .filter(m => m.type === 'api')
      .reduce((sum, m) => sum + m.duration, 0) / recentMetrics.filter(m => m.type === 'api').length || 0;
    
    return {
      averageClickHandlerTime: avgClickTime,
      averageApiResponseTime: avgApiTime,
      totalAlerts: recentAlerts.length,
      criticalAlerts: recentAlerts.filter(a => a.severity === 'critical').length,
      highAlerts: recentAlerts.filter(a => a.severity === 'high').length,
      metricsCount: recentMetrics.length,
      healthScore: this.calculateHealthScore(recentMetrics, recentAlerts)
    };
  }

  private calculateHealthScore(metrics: PerformanceMetric[], alerts: PerformanceAlert[]): number {
    let score = 100;
    
    // Deduct points for slow operations
    metrics.forEach(metric => {
      if (metric.type === 'click' && metric.duration > this.thresholds.clickHandler) {
        score -= 10;
      }
      if (metric.type === 'api' && metric.duration > this.thresholds.apiResponse) {
        score -= 5;
      }
    });
    
    // Deduct points for alerts
    alerts.forEach(alert => {
      switch (alert.severity) {
        case 'critical': score -= 25; break;
        case 'high': score -= 15; break;
        case 'medium': score -= 10; break;
        case 'low': score -= 5; break;
      }
    });
    
    return Math.max(0, score);
  }

  // Cleanup method
  destroy() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
    this.metrics = [];
    this.alerts = [];
  }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor();

// Export utility functions
export const wrapClickHandler = <T extends Event>(
  handler: (event: T) => void | Promise<void>,
  name: string
) => performanceMonitor.wrapClickHandler(handler, name);

export const trackApiCall = <T>(
  apiCall: () => Promise<T>,
  endpoint: string
) => performanceMonitor.trackApiCall(apiCall, endpoint);

export default performanceMonitor;
