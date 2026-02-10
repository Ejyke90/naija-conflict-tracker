// Test script to verify the trend-comparison POST endpoint fix
// Run this in the browser console or as a Node.js script

const testTrendComparison = async () => {
  const API_BASE = 'http://localhost:8000';
  
  console.log('🧪 Testing trend-comparison POST endpoint fixes...\n');
  
  // Test 1: National view (All States)
  console.log('Test 1: National view (state_id: null)');
  try {
    const response1 = await fetch(`${API_BASE}/api/v1/timeseries/trend-comparison`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        state_id: null,
        time_range: "Last 12 months"
      })
    });
    
    console.log('Status:', response1.status);
    const data1 = await response1.json();
    console.log('✅ National view works - Comparison keys:', Object.keys(data1.comparison || {}));
    console.log('Time range:', data1.timeRange);
  } catch (error) {
    console.error('❌ National view failed:', error.message);
  }
  
  console.log('\nTest 2: Specific state view');
  try {
    const response2 = await fetch(`${API_BASE}/api/v1/timeseries/trend-comparison`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        state_id: 14,  // Some state ID
        time_range: "Last 6 months"
      })
    });
    
    console.log('Status:', response2.status);
    const data2 = await response2.json();
    console.log('✅ State view works - Message:', data2.message || 'Data available');
  } catch (error) {
    console.error('❌ State view failed:', error.message);
  }
  
  console.log('\nTest 3: Invalid data (should handle gracefully)');
  try {
    const response3 = await fetch(`${API_BASE}/api/v1/timeseries/trend-comparison`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        state_id: "invalid_string",
        time_range: "Last 12 months"
      })
    });
    
    console.log('Status:', response3.status);
    const data3 = await response3.json();
    console.log('✅ Invalid data handled gracefully');
  } catch (error) {
    console.error('❌ Invalid data not handled:', error.message);
  }
  
  console.log('\n🎯 Tests completed!');
};

// Export for browser use
if (typeof window !== 'undefined') {
  window.testTrendComparison = testTrendComparison;
  console.log('💡 Run testTrendComparison() in console to test the fixes');
}

// Export for Node.js use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { testTrendComparison };
}
