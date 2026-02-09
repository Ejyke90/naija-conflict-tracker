// API Regression Tests
// These tests verify that API endpoints maintain expected response structures

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

describe('API Endpoint Regression Tests', () => {
  const endpoints = [
    '/api/v1/conflicts/stats/dashboard',
    '/api/v1/analytics/states',
    '/api/v1/timeseries/trend-comparison',
    '/api/v1/monitoring/pipeline-status',
    '/api/v1/alerts/poll',
    '/api/v1/conflicts/stats/kidnapping'
  ];

  endpoints.forEach(endpoint => {
    test(`${endpoint} should return correct response structure`, async () => {
      try {
        const response = await fetch(`${BASE_URL}${endpoint}`);
        
        expect(response.ok).toBe(true);
        const data = await response.json();
        
        // Verify response has expected structure
        expect(data).toHaveProperty('status');
        expect(['ok', 'degraded', 'error']).toContain(data.status);
        
        if (endpoint.includes('/analytics/states')) {
          expect(data).toHaveProperty('data');
          expect(Array.isArray(data.data)).toBe(true);
          
          if (data.data.length > 0) {
            expect(data.data[0]).toHaveProperty('state');
            expect(data.data[0]).toHaveProperty('incidents');
            expect(data.data[0]).toHaveProperty('fatalities');
            expect(typeof data.data[0].state).toBe('string');
            expect(typeof data.data[0].incidents).toBe('number');
            expect(typeof data.data[0].fatalities).toBe('number');
          }
        }
        
        if (endpoint.includes('/stats/dashboard')) {
          expect(data).toHaveProperty('by_state');
          expect(data).toHaveProperty('by_event_type');
          expect(data).toHaveProperty('by_month');
          expect(data).toHaveProperty('kidnapping_stats');
        }
        
        if (endpoint.includes('/stats/kidnapping')) {
          expect(data).toHaveProperty('current_period');
          expect(data).toHaveProperty('by_state');
          expect(data).toHaveProperty('monthly_trends');
          expect(data).toHaveProperty('last_updated');
        }
        
      } catch (error) {
        console.error(`API test failed for ${endpoint}:`, error);
        throw error;
      }
    });
  });

  test('CRITICAL: state analytics API maintains expected structure', async () => {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/analytics/states?months_back=12`);
      const data = await response.json();
      
      // Critical: Must have data field
      expect(data).toHaveProperty('data');
      expect(Array.isArray(data.data)).toBe(true);
      
      // Each state must have required fields
      data.data.forEach(state => {
        expect(state).toHaveProperty('state');
        expect(state).toHaveProperty('incidents');
        expect(state).toHaveProperty('fatalities');
        expect(typeof state.state).toBe('string');
        expect(typeof state.incidents).toBe('number');
        expect(typeof state.fatalities).toBe('number');
        expect(state.incidents).toBeGreaterThanOrEqual(0);
        expect(state.fatalities).toBeGreaterThanOrEqual(0);
      });
      
      // Should have at least some states
      expect(data.data.length).toBeGreaterThan(0);
      
    } catch (error) {
      console.error('State analytics structure test failed:', error);
      throw error;
    }
  });

  test('CRITICAL: kidnapping stats API maintains expected structure', async () => {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/conflicts/stats/kidnapping`);
      const data = await response.json();
      
      // Critical structure validation
      expect(data).toHaveProperty('current_period');
      expect(data).toHaveProperty('by_state');
      expect(data).toHaveProperty('monthly_trends');
      expect(data).toHaveProperty('last_updated');
      
      // Current period structure
      expect(data.current_period).toHaveProperty('victims');
      expect(data.current_period).toHaveProperty('incidents');
      expect(data.current_period).toHaveProperty('victims_change');
      expect(data.current_period).toHaveProperty('incidents_change');
      
      expect(typeof data.current_period.victims).toBe('number');
      expect(typeof data.current_period.incidents).toBe('number');
      expect(typeof data.current_period.victims_change).toBe('number');
      expect(typeof data.current_period.incidents_change).toBe('number');
      
      // By state structure
      expect(Array.isArray(data.by_state)).toBe(true);
      data.by_state.forEach(state => {
        expect(state).toHaveProperty('state');
        expect(state).toHaveProperty('victims');
        expect(state).toHaveProperty('incidents');
      });
      
      // Monthly trends structure
      expect(Array.isArray(data.monthly_trends)).toBe(true);
      data.monthly_trends.forEach(trend => {
        expect(trend).toHaveProperty('month');
        expect(trend).toHaveProperty('victims');
        expect(trend).toHaveProperty('incidents');
      });
      
    } catch (error) {
      console.error('Kidnapping stats structure test failed:', error);
      throw error;
    }
  });

  test('API response times should be acceptable', async () => {
    const endpoints = [
      '/api/v1/conflicts/stats/dashboard',
      '/api/v1/analytics/states',
      '/api/v1/conflicts/stats/kidnapping'
    ];

    for (const endpoint of endpoints) {
      const startTime = performance.now();
      
      try {
        const response = await fetch(`${BASE_URL}${endpoint}`);
        await response.json();
        
        const responseTime = performance.now() - startTime;
        
        // API should respond within 2 seconds
        expect(responseTime).toBeLessThan(2000);
        
      } catch (error) {
        console.error(`Performance test failed for ${endpoint}:`, error);
        throw error;
      }
    }
  });
});

// Manual regression test runner
const runManualRegressionTests = async () => {
  console.log('🧪 Running Manual API Regression Tests...');
  
  const results = {
    passed: 0,
    failed: 0,
    errors: []
  };

  const testEndpoint = async (endpoint, description) => {
    try {
      const response = await fetch(`${BASE_URL}${endpoint}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Basic structure validation
      if (!data.status) {
        throw new Error('Missing status field in response');
      }
      
      console.log(`✅ ${description}`);
      results.passed++;
      
    } catch (error) {
      console.error(`❌ ${description}: ${error.message}`);
      results.failed++;
      results.errors.push({ endpoint, error: error.message });
    }
  };

  // Critical endpoints
  await testEndpoint('/api/v1/analytics/states?months_back=12', 'State Analytics API');
  await testEndpoint('/api/v1/conflicts/stats/dashboard', 'Dashboard Stats API');
  await testEndpoint('/api/v1/conflicts/stats/kidnapping', 'Kidnapping Stats API');
  await testEndpoint('/api/v1/timeseries/trend-comparison?states=Borno,Zamfara&months_back=12', 'Trend Comparison API');

  console.log(`\n📊 Test Results: ${results.passed} passed, ${results.failed} failed`);
  
  if (results.failed > 0) {
    console.log('\n❌ Failed Tests:');
    results.errors.forEach(({ endpoint, error }) => {
      console.log(`  - ${endpoint}: ${error}`);
    });
  }

  return results;
};

// Export for use in browser console or CI
if (typeof window !== 'undefined') {
  window.runManualRegressionTests = runManualRegressionTests;
}

module.exports = { runManualRegressionTests };
