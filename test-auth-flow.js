#!/usr/bin/env node

/**
 * Manual Authentication Flow Test Script
 * 
 * This script tests the authentication flow by making actual API calls
 * to verify the authentication system works correctly.
 * 
 * Usage: node test-auth-flow.js [backend-url]
 * Example: node test-auth-flow.js http://localhost:8000
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');

// Configuration
const BACKEND_URL = process.argv[2] || 'http://localhost:8000';
const TEST_TIMEOUT = 10000; // 10 seconds

// Test credentials
const VALID_CREDENTIALS = {
  email: 'ejike.udeze@yahoo.com',
  password: 'Kneejerk12345'
};

const INVALID_CREDENTIALS = {
  email: 'invalid@example.com',
  password: 'wrongpassword'
};

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logSuccess(message) {
  log(`✅ ${message}`, colors.green);
}

function logError(message) {
  log(`❌ ${message}`, colors.red);
}

function logInfo(message) {
  log(`ℹ️  ${message}`, colors.blue);
}

function logWarning(message) {
  log(`⚠️  ${message}`, colors.yellow);
}

// HTTP client helper
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const isHttps = urlObj.protocol === 'https:';
    const client = isHttps ? https : http;
    
    const requestOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port || (isHttps ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    };

    const req = client.request(requestOptions, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const jsonData = data ? JSON.parse(data) : {};
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: jsonData
          });
        } catch (error) {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: data
          });
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    if (options.body) {
      req.write(typeof options.body === 'string' ? options.body : JSON.stringify(options.body));
    }

    req.setTimeout(TEST_TIMEOUT, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.end();
  });
}

// Test functions
async function testBackendHealth() {
  logInfo('Testing backend health...');
  
  try {
    const response = await makeRequest(`${BACKEND_URL}/api/v1/auth/test`);
    
    if (response.status === 200) {
      logSuccess('Backend is healthy');
      return true;
    } else {
      logError(`Backend returned status ${response.status}`);
      return false;
    }
  } catch (error) {
    logError(`Backend health check failed: ${error.message}`);
    return false;
  }
}

async function testLoginWithValidCredentials() {
  logInfo('Testing login with valid credentials...');
  
  try {
    const response = await makeRequest(`${BACKEND_URL}/api/v1/auth/login`, {
      method: 'POST',
      body: VALID_CREDENTIALS
    });
    
    if (response.status === 200) {
      logSuccess('Login with valid credentials successful');
      
      const { access_token, refresh_token, user } = response.data;
      
      if (!access_token || !refresh_token || !user) {
        logError('Login response missing required fields');
        return null;
      }
      
      logInfo(`User: ${user.email}, Role: ${user.role}`);
      
      return {
        accessToken: access_token,
        refreshToken: refresh_token,
        user: user
      };
    } else if (response.status === 401) {
      logWarning('Login failed - invalid credentials (expected for test)');
      return null;
    } else {
      logError(`Login failed with status ${response.status}: ${JSON.stringify(response.data)}`);
      return null;
    }
  } catch (error) {
    logError(`Login request failed: ${error.message}`);
    return null;
  }
}

async function testLoginWithInvalidCredentials() {
  logInfo('Testing login with invalid credentials...');
  
  try {
    const response = await makeRequest(`${BACKEND_URL}/api/v1/auth/login`, {
      method: 'POST',
      body: INVALID_CREDENTIALS
    });
    
    if (response.status === 401) {
      logSuccess('Login with invalid credentials properly rejected');
      return true;
    } else {
      logError(`Invalid login should return 401, got ${response.status}`);
      return false;
    }
  } catch (error) {
    logError(`Invalid login request failed: ${error.message}`);
    return false;
  }
}

async function testProtectedEndpoint(accessToken) {
  logInfo('Testing protected endpoint access...');
  
  try {
    const response = await makeRequest(`${BACKEND_URL}/api/v1/auth/me`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (response.status === 200) {
      logSuccess('Protected endpoint access successful');
      
      const { id, email, role } = response.data;
      logInfo(`Current user: ${email} (${role})`);
      
      return response.data;
    } else if (response.status === 401) {
      logError('Protected endpoint rejected valid token');
      return null;
    } else {
      logError(`Protected endpoint returned status ${response.status}`);
      return null;
    }
  } catch (error) {
    logError(`Protected endpoint request failed: ${error.message}`);
    return null;
  }
}

async function testTokenRefresh(refreshToken) {
  logInfo('Testing token refresh...');
  
  try {
    const response = await makeRequest(`${BACKEND_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      body: { refresh_token: refreshToken }
    });
    
    if (response.status === 200) {
      logSuccess('Token refresh successful');
      
      const { access_token } = response.data;
      
      if (!access_token) {
        logError('Token refresh response missing access_token');
        return null;
      }
      
      return access_token;
    } else if (response.status === 401) {
      logError('Token refresh failed - invalid refresh token');
      return null;
    } else {
      logError(`Token refresh returned status ${response.status}`);
      return null;
    }
  } catch (error) {
    logError(`Token refresh request failed: ${error.message}`);
    return null;
  }
}

async function testLogout(accessToken) {
  logInfo('Testing logout...');
  
  try {
    const response = await makeRequest(`${BACKEND_URL}/api/v1/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (response.status === 200) {
      logSuccess('Logout successful');
      return true;
    } else {
      logError(`Logout returned status ${response.status}`);
      return false;
    }
  } catch (error) {
    logError(`Logout request failed: ${error.message}`);
    return false;
  }
}

async function testInvalidTokenAccess() {
  logInfo('Testing access with invalid token...');
  
  try {
    const response = await makeRequest(`${BACKEND_URL}/api/v1/auth/me`, {
      headers: {
        'Authorization': 'Bearer invalid-token-12345'
      }
    });
    
    if (response.status === 401) {
      logSuccess('Invalid token properly rejected');
      return true;
    } else {
      logError(`Invalid token should return 401, got ${response.status}`);
      return false;
    }
  } catch (error) {
    logError(`Invalid token test failed: ${error.message}`);
    return false;
  }
}

async function testExpiredTokenAccess() {
  logInfo('Testing access with expired token...');
  
  // This test uses a token that looks valid but is expired
  const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid';
  
  try {
    const response = await makeRequest(`${BACKEND_URL}/api/v1/auth/me`, {
      headers: {
        'Authorization': `Bearer ${expiredToken}`
      }
    });
    
    if (response.status === 401) {
      logSuccess('Expired token properly rejected');
      return true;
    } else {
      logError(`Expired token should return 401, got ${response.status}`);
      return false;
    }
  } catch (error) {
    logError(`Expired token test failed: ${error.message}`);
    return false;
  }
}

// Main test runner
async function runAuthenticationTests() {
  log('\n🧪 Authentication Flow Test Suite', colors.cyan);
  log(`📍 Backend URL: ${BACKEND_URL}`, colors.cyan);
  log('━'.repeat(50), colors.cyan);
  
  const results = {
    backendHealth: false,
    validLogin: false,
    invalidLogin: false,
    protectedAccess: false,
    tokenRefresh: false,
    logout: false,
    invalidToken: false,
    expiredToken: false
  };
  
  let authData = null;
  
  // Test 1: Backend health
  results.backendHealth = await testBackendHealth();
  
  if (!results.backendHealth) {
    logError('Backend is not healthy - stopping tests');
    return results;
  }
  
  // Test 2: Login with invalid credentials
  results.invalidLogin = await testLoginWithInvalidCredentials();
  
  // Test 3: Login with valid credentials
  authData = await testLoginWithValidCredentials();
  results.validLogin = authData !== null;
  
  if (authData) {
    // Test 4: Protected endpoint access
    const userData = await testProtectedEndpoint(authData.accessToken);
    results.protectedAccess = userData !== null;
    
    // Test 5: Token refresh
    const newAccessToken = await testTokenRefresh(authData.refreshToken);
    results.tokenRefresh = newAccessToken !== null;
    
    if (newAccessToken) {
      // Test protected endpoint with new token
      await testProtectedEndpoint(newAccessToken);
    }
    
    // Test 6: Logout
    results.logout = await testLogout(authData.accessToken);
  }
  
  // Test 7: Invalid token access
  results.invalidToken = await testInvalidTokenAccess();
  
  // Test 8: Expired token access
  results.expiredToken = await testExpiredTokenAccess();
  
  // Results summary
  log('\n📊 Test Results Summary', colors.magenta);
  log('━'.repeat(50), colors.magenta);
  
  const passedTests = Object.values(results).filter(Boolean).length;
  const totalTests = Object.keys(results).length;
  
  Object.entries(results).forEach(([test, passed]) => {
    const testName = test.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
    const status = passed ? '✅ PASS' : '❌ FAIL';
    const color = passed ? colors.green : colors.red;
    log(`${testName.padEnd(25)} ${status}`, color);
  });
  
  log(`\n🎯 Overall: ${passedTests}/${totalTests} tests passed`, 
    passedTests === totalTests ? colors.green : colors.yellow);
  
  if (passedTests === totalTests) {
    logSuccess('All authentication tests passed! 🎉');
  } else {
    logWarning('Some tests failed. Please check the authentication system.');
  }
  
  return results;
}

// Run tests if this script is executed directly
if (require.main === module) {
  runAuthenticationTests().catch(error => {
    logError(`Test suite failed: ${error.message}`);
    process.exit(1);
  });
}

module.exports = {
  runAuthenticationTests,
  testBackendHealth,
  testLoginWithValidCredentials,
  testLoginWithInvalidCredentials,
  testProtectedEndpoint,
  testTokenRefresh,
  testLogout,
  testInvalidTokenAccess,
  testExpiredTokenAccess
};
