// API utility functions for the Naija Conflict Tracker
// This provides standardized functions for making API calls

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Fetches trend comparison data using the correct method
 * @param stateId - The state ID (null for national view)
 * @param timeRange - The time range string (e.g., "Last 12 months")
 * @returns Promise with trend comparison data
 */
export async function fetchTrendComparison(stateId: number | null = null, timeRange: string = "Last 12 months") {
  try {
    const requestBody = {
      state_id: stateId,
      time_range: timeRange
    };

    console.log('Fetching trend comparison with:', requestBody);

    const response = await fetch(`${API_BASE_URL}/api/v1/timeseries/trend-comparison`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Trend comparison API error:', response.status, errorText);
      
      if (response.status === 422) {
        // Try to parse Pydantic validation errors
        try {
          const errorData = JSON.parse(errorText);
          console.error('Validation errors:', errorData.detail);
          throw new Error(`Validation failed: ${JSON.stringify(errorData.detail)}`);
        } catch {
          throw new Error(`Request validation failed: ${errorText}`);
        }
      }
      
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Trend comparison response:', data);
    return data;
  } catch (error) {
    console.error('Error fetching trend comparison:', error);
    throw error;
  }
}

/**
 * Fetches monthly trends data - tries fast MVP first, falls back to original, then static
 * @param monthsBack - Number of months to look back
 * @param state - Optional state filter
 * @param includeForecast - Whether to include forecast data
 * @returns Promise with monthly trends data
 */
export async function fetchMonthlyTrends(
  monthsBack: number = 12,
  state: string | null = null,
  includeForecast: boolean = true
) {
  // Try 1: Fast MVP endpoint
  try {
    const params = new URLSearchParams({
      months_back: monthsBack.toString(),
    });

    if (state) {
      params.append('state', state);
    }

    console.log('Trying fast MVP monthly trends endpoint...');
    const response = await fetch(`${API_BASE_URL}/api/v1/timeseries-mvp/monthly-trends-fast?${params}`, {
      signal: AbortSignal.timeout(5000) // 5 second timeout
    });

    if (response.ok) {
      const data = await response.json();
      console.log('Fast MVP endpoint successful:', data);
      return data;
    } else {
      throw new Error(`Fast endpoint failed: ${response.status}`);
    }
  } catch (error) {
    console.warn('Fast MVP endpoint failed, trying original endpoint:', error);
    
    // Try 2: Original endpoint
    try {
      const params = new URLSearchParams({
        months_back: monthsBack.toString(),
        include_forecast: includeForecast.toString(),
      });

      if (state) {
        params.append('state', state);
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/timeseries/monthly-trends?${params}`, {
        signal: AbortSignal.timeout(10000) // 10 second timeout
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Original endpoint successful:', data);
        return data;
      } else {
        throw new Error(`Original endpoint failed: ${response.status}`);
      }
    } catch (fallbackError) {
      console.warn('Original endpoint failed, using static fallback:', fallbackError);
      
      // Try 3: Static endpoint (guaranteed to work)
      try {
        const params = new URLSearchParams({
          months_back: monthsBack.toString(),
        });

        if (state) {
          params.append('state', state);
        }

        const response = await fetch(`${API_BASE_URL}/api/v1/timeseries-static/monthly-trends-static?${params}`, {
          signal: AbortSignal.timeout(3000) // 3 second timeout
        });

        if (response.ok) {
          const data = await response.json();
          console.log('Static endpoint successful:', data);
          return data;
        } else {
          throw new Error(`Static endpoint failed: ${response.status}`);
        }
      } catch (staticError) {
        console.error('All endpoints failed:', staticError);
        throw new Error('All monthly trends endpoints failed. Please try again later.');
      }
    }
  }
}

/**
 * Fetches crisis intelligence statistics (replaces kidnapping stats)
 * @returns Promise with crisis intelligence data
 */
export async function fetchCrisisIntelligence() {
  try {
    const token = localStorage.getItem('access_token');
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/crisis-intelligence/crisis-intelligence`, {
      headers,
      signal: AbortSignal.timeout(20000)
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching crisis intelligence:', error);
    throw error;
  }
}

// Export for use in components
export { API_BASE_URL };
