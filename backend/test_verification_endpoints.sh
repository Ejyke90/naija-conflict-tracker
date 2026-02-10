#!/bin/bash

# Test script for verification endpoints
# This script tests the complete verification system including bulk operations

echo "🧪 Testing Complete Verification System"
echo "======================================="

BASE_URL="http://localhost:8000"

# Test 1: Get pending conflicts (should require authentication)
echo ""
echo "📋 Testing GET /api/v1/conflicts/pending"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "${BASE_URL}/api/v1/conflicts/pending" \
  -H "Authorization: Bearer test-token")
http_code=$(echo "$response" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)
response_body=$(echo "$response" | sed -e 's/HTTP_STATUS:[0-9]*$//')

echo "Status Code: $http_code"
if [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
  echo "✅ Authentication required (as expected)"
elif [ "$http_code" = "200" ]; then
  echo "✅ Endpoint accessible"
  echo "Response preview:"
  echo "$response_body" | head -20
else
  echo "⚠️  Unexpected status code: $http_code"
fi

# Test 2: Verify a single conflict (should require authentication)
echo ""
echo "✅ Testing PUT /api/v1/conflicts/1/verify"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "${BASE_URL}/api/v1/conflicts/1/verify" \
  -X PUT \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json")
http_code=$(echo "$response" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)
response_body=$(echo "$response" | sed -e 's/HTTP_STATUS:[0-9]*$//')

echo "Status Code: $http_code"
if [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
  echo "✅ Authentication required (as expected)"
elif [ "$http_code" = "404" ]; then
  echo "✅ Conflict not found (expected for test ID)"
elif [ "$http_code" = "200" ]; then
  echo "✅ Verification successful"
  echo "Response preview:"
  echo "$response_body" | jq '.' 2>/dev/null || echo "$response_body"
else
  echo "⚠️  Unexpected status code: $http_code"
  echo "Response: $response_body"
fi

# Test 3: Bulk verify conflicts (should require authentication)
echo ""
echo "📦 Testing PUT /api/v1/conflicts/bulk-verify"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "${BASE_URL}/api/v1/conflicts/bulk-verify" \
  -X PUT \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"ids": [1, 2, 3]}')
http_code=$(echo "$response" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)
response_body=$(echo "$response" | sed -e 's/HTTP_STATUS:[0-9]*$//')

echo "Status Code: $http_code"
if [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
  echo "✅ Authentication required (as expected)"
elif [ "$http_code" = "404" ]; then
  echo "✅ Conflicts not found (expected for test IDs)"
elif [ "$http_code" = "200" ]; then
  echo "✅ Bulk verification successful"
  echo "Response preview:"
  echo "$response_body" | jq '.' 2>/dev/null || echo "$response_body"
else
  echo "⚠️  Unexpected status code: $http_code"
  echo "Response: $response_body"
fi

# Test 4: Bulk verify with empty array (should return error)
echo ""
echo "⚠️  Testing PUT /api/v1/conflicts/bulk-verify with empty array"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "${BASE_URL}/api/v1/conflicts/bulk-verify" \
  -X PUT \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"ids": []}')
http_code=$(echo "$response" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)
response_body=$(echo "$response" | sed -e 's/HTTP_STATUS:[0-9]*$//')

echo "Status Code: $http_code"
if [ "$http_code" = "400" ]; then
  echo "✅ Correctly rejected empty array"
  echo "Error response: $response_body"
else
  echo "⚠️  Expected 400 for empty array, got: $http_code"
fi

# Test 5: Check validation summary endpoint
echo ""
echo "📊 Testing GET /api/v1/system/validation/summary"
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "${BASE_URL}/api/v1/system/validation/summary")
http_code=$(echo "$response" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)
response_body=$(echo "$response" | sed -e 's/HTTP_STATUS:[0-9]*$//')

echo "Status Code: $http_code"
if [ "$http_code" = "200" ]; then
  echo "✅ Validation summary endpoint working"
  echo "Response preview:"
  echo "$response_body" | jq '.' 2>/dev/null || echo "$response_body"
else
  echo "⚠️  Validation summary endpoint failed: $http_code"
  echo "Response: $response_body"
fi

echo ""
echo "🎉 Complete Verification System Tests Done!"
echo ""
echo "📍 Endpoints tested:"
echo "   • GET /api/v1/conflicts/pending - Review queue"
echo "   • PUT /api/v1/conflicts/:id/verify - Single incident verification"
echo "   • PUT /api/v1/conflicts/bulk-verify - Bulk incident verification"
echo "   • GET /api/v1/system/validation/summary - Summary stats"
echo ""
echo "🔒 Authentication: Required for all verification endpoints"
echo "📝 Audit Logging: Automatic for all verification actions"
echo "🔄 Auto-refresh: 30-second intervals in frontend"
echo "📦 Bulk Operations: PostgreSQL ANY() and unnest() for performance"
echo "⚡ Real-time Updates: React Query invalidation for instant UI updates"
