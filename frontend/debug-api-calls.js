// Debug utility to capture API calls
// This can be pasted into the browser console to monitor API requests

(function() {
  const originalFetch = window.fetch;
  
  window.fetch = function(...args) {
    const [url, options = {}] = args;
    
    // Log any requests to trend-comparison endpoint
    if (url.includes('trend-comparison')) {
      console.group('🔍 Trend Comparison API Call Detected');
      console.log('URL:', url);
      console.log('Method:', options.method || 'GET');
      console.log('Headers:', options.headers);
      
      if (options.body) {
        try {
          const body = JSON.parse(options.body);
          console.log('Body:', body);
          
          // Check for the problematic pattern
          if (body.state_id !== undefined || body.time_range !== undefined) {
            console.error('❌ PROBLEM: Sending POST with JSON body to GET endpoint!');
            console.error('Expected: GET with query parameters');
            console.error('Actual:', options.method || 'GET', 'with body:', body);
          }
        } catch (e) {
          console.log('Body (raw):', options.body);
        }
      }
      
      // Log the response
      return originalFetch.apply(this, args)
        .then(response => {
          console.log('Response Status:', response.status);
          console.log('Response OK:', response.ok);
          
          // Clone the response to read the body without consuming it
          const clonedResponse = response.clone();
          return clonedResponse.json()
            .then(data => {
              console.log('Response Data:', data);
              console.groupEnd();
              return response; // Return original response
            })
            .catch(() => {
              console.log('Response Body: (not JSON)');
              console.groupEnd();
              return response;
            });
        })
        .catch(error => {
          console.error('Request Error:', error);
          console.groupEnd();
          throw error;
        });
    }
    
    // For all other requests, use original fetch
    return originalFetch.apply(this, args);
  };
  
  console.log('🔍 API Debug Monitor Active - Monitoring trend-comparison calls');
})();
