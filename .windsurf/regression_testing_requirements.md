# Automated Regression Testing Requirements

## Overview
This document defines the automated regression testing requirements to prevent regressions like the State Comparison issue from occurring in future deployments.

## Critical Test Areas

### 1. Dashboard Component Regression Tests

#### State Comparison Component Tests
```javascript
// Test: State Comparison shows exactly 5 states
describe('StateComparisonChart Regression Tests', () => {
  test('should display exactly 5 states in smart selection mode', async () => {
    const mockApiResponse = {
      data: [
        { state: 'Borno', incidents: 40, fatalities: 350 },
        { state: 'Zamfara', incidents: 126, fatalities: 246 },
        { state: 'Kaduna', incidents: 94, fatalities: 275 },
        { state: 'Plateau', incidents: 197, fatalities: 805 },
        { state: 'Niger', incidents: 99, fatalities: 204 },
        { state: 'Benue', incidents: 88, fatalities: 531 },
        // ... more states
      ],
      status: 'ok'
    };

    // Mock fetch API
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockApiResponse)
    });

    render(<StateComparisonChart defaultToSmartSelection={true} maxStates={5} />);
    
    await waitFor(() => {
      expect(screen.getAllByTestId('state-card')).toHaveLength(5);
    });
  });

  test('should handle API response structure changes gracefully', async () => {
    // Test with different response structures
    const testCases = [
      { data: [{ state: 'Borno', incidents: 40, fatalities: 350 }], status: 'ok' },
      [{ state: 'Borno', incidents: 40, fatalities: 350 }], // Direct array
      { results: [{ state: 'Borno', incidents: 40, fatalities: 350 }] }, // Different key
    ];

    for (const response of testCases) {
      global.fetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(response)
      });

      render(<StateComparisonChart defaultToSmartSelection={true} maxStates={5} />);
      
      await waitFor(() => {
        expect(screen.queryByTestId('state-card')).toBeInTheDocument();
      });
    }
  });
});
```

#### Dashboard Tab Tests
```javascript
// Test: All dashboard tabs load without errors
describe('Dashboard Regression Tests', () => {
  const tabs = ['overview', 'mapping', 'pipeline', 'analytics', 'reports', 'kidnapping'];

  tabs.forEach(tab => {
    test(`should load ${tab} tab without errors`, async () => {
      render(<ConflictDashboard />);
      
      const tabButton = screen.getByRole('tab', { name: new RegExp(tab, 'i') });
      fireEvent.click(tabButton);
      
      await waitFor(() => {
        expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
        expect(screen.queryByTestId('error-message')).not.toBeInTheDocument();
      });
    });
  });
});
```

### 2. API Endpoint Regression Tests

#### Core API Tests
```javascript
// Test: Critical API endpoints return expected structure
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
      const response = await fetch(endpoint);
      
      expect(response.ok).toBe(true);
      const data = await response.json();
      
      // Verify response has expected structure
      expect(data).toHaveProperty('status');
      if (endpoint.includes('/analytics/states')) {
        expect(data).toHaveProperty('data');
        expect(Array.isArray(data.data)).toBe(true);
        if (data.data.length > 0) {
          expect(data.data[0]).toHaveProperty('state');
          expect(data.data[0]).toHaveProperty('incidents');
          expect(data.data[0]).toHaveProperty('fatalities');
        }
      }
    });
  });
});
```

#### API Response Structure Tests
```javascript
// Test: API responses maintain backward compatibility
describe('API Response Structure Tests', () => {
  test('state analytics API maintains expected structure', async () => {
    const response = await fetch('/api/v1/analytics/states?months_back=12');
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
    });
  });
});
```

### 3. Performance Regression Tests

#### Page Load Performance
```javascript
// Test: Page load times don't degrade
describe('Performance Regression Tests', () => {
  test('dashboard should load within performance threshold', async () => {
    const startTime = performance.now();
    
    render(<ConflictDashboard />);
    await waitFor(() => {
      expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
    });
    
    const loadTime = performance.now() - startTime;
    expect(loadTime).toBeLessThan(3000); // 3 seconds
  });

  test('API responses should be fast', async () => {
    const endpoints = [
      '/api/v1/conflicts/stats/dashboard',
      '/api/v1/analytics/states',
      '/api/v1/timeseries/trend-comparison'
    ];

    for (const endpoint of endpoints) {
      const startTime = performance.now();
      const response = await fetch(endpoint);
      await response.json();
      const responseTime = performance.now() - startTime;
      
      expect(responseTime).toBeLessThan(2000); // 2 seconds
    }
  });
});
```

### 4. Database Integrity Tests

#### Schema Validation Tests
```javascript
// Test: Database schema remains consistent
describe('Database Integrity Tests', () => {
  test('conflicts table schema is intact', async () => {
    // Test that required columns exist
    const result = await db.query(`
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_name = 'conflicts'
      ORDER BY ordinal_position
    `);
    
    const requiredColumns = ['id', 'incidence_date', 'state', 'fatalities', 'injuries', 'kidnapped'];
    const actualColumns = result.rows.map(row => row.column_name);
    
    requiredColumns.forEach(column => {
      expect(actualColumns).toContain(column);
    });
  });

  test('state statistics query works correctly', async () => {
    const result = await db.query(`
      SELECT state, COUNT(*) as incidents, SUM(fatalities) as fatalities
      FROM conflicts 
      WHERE incidence_date >= NOW() - INTERVAL '12 months'
      GROUP BY state
      ORDER BY fatalities DESC
      LIMIT 10
    `);
    
    expect(result.rows.length).toBeGreaterThan(0);
    result.rows.forEach(row => {
      expect(row).toHaveProperty('state');
      expect(row).toHaveProperty('incidents');
      expect(row).toHaveProperty('fatalities');
      expect(typeof row.incidents).toBe('number');
      expect(typeof row.fatalities).toBe('number');
    });
  });
});
```

## Automated Testing Pipeline

### Pre-commit Hooks
```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "Running regression tests..."

# Run critical tests
npm run test:regression

# Check build
npm run build

# Run TypeScript check
npx tsc --noEmit

# Run linting
npm run lint

echo "All regression tests passed!"
```

### CI/CD Pipeline Integration
```yaml
# .github/workflows/regression-tests.yml
name: Regression Tests

on: [push, pull_request]

jobs:
  regression-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run regression tests
      run: npm run test:regression
    
    - name: Run API tests
      run: npm run test:api
    
    - name: Check build
      run: npm run build
    
    - name: Performance tests
      run: npm run test:performance
```

### Test Scripts
```json
{
  "scripts": {
    "test:regression": "jest --testPathPattern=regression",
    "test:api": "jest --testPathPattern=api",
    "test:performance": "jest --testPathPattern=performance",
    "test:critical": "jest --testPathPattern=critical --watchAll=false",
    "pre-commit": "npm run test:critical && npm run build && npm run lint"
  }
}
```

## Monitoring & Alerting

### Regression Detection Metrics
1. **Component Render Time** - Alert if > 3 seconds
2. **API Response Time** - Alert if > 2 seconds  
3. **Error Rate** - Alert if > 1% for any endpoint
4. **State Count Validation** - Alert if StateComparison != 5 states
5. **Build Success Rate** - Alert on build failures

### Automated Regression Reports
```javascript
// Generate daily regression report
const generateRegressionReport = async () => {
  const report = {
    date: new Date().toISOString(),
    tests: {
      stateComparison: await testStateComparison(),
      apiEndpoints: await testApiEndpoints(),
      performance: await testPerformance(),
      database: await testDatabaseIntegrity()
    },
    status: 'passed', // or 'failed'
    issues: []
  };
  
  // Send to monitoring system
  await sendToMonitoring(report);
  
  // Create GitHub issue if failed
  if (report.status === 'failed') {
    await createRegressionIssue(report);
  }
};
```

## Implementation Priority

### Phase 1: Critical Tests (Immediate)
1. ✅ State Comparison 5-state validation
2. ✅ Core API endpoint structure validation  
3. ✅ Dashboard tab loading tests
4. ✅ Build verification

### Phase 2: Comprehensive Tests (1 week)
1. Performance regression tests
2. Database integrity tests
3. API response compatibility tests
4. Error handling tests

### Phase 3: Advanced Monitoring (2 weeks)
1. Automated regression reports
2. Performance monitoring
3. Real-time regression detection
4. CI/CD integration

## Success Metrics

- **Zero regressions** in production deployments
- **< 2 minute** regression test execution time
- **100% test coverage** for critical components
- **< 1 hour** regression detection and notification
- **< 5 minute** rollback capability for regressions

---

**Implementation Status**: Phase 1 Complete - Critical tests implemented
**Next Steps**: Implement Phase 2 comprehensive tests
**Owner**: Development Team
**Review Date**: Weekly during sprint planning
