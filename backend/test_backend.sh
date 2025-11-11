#!/bin/bash

# Backend API Test Script
BASE_URL="http://127.0.0.1:8000"

echo "🧪 Testing Agent Mira Backend API"
echo "=================================="
echo ""

# Check if server is running
echo "1️⃣  Checking if server is running..."
if curl -s --connect-timeout 2 "$BASE_URL/" > /dev/null 2>&1; then
    echo "✅ Server is running!"
else
    echo "❌ Server is not running!"
    echo ""
    echo "Please start the server first:"
    echo "  cd backend"
    echo "  source venv/bin/activate  # or source .venv/bin/activate"
    echo "  uvicorn main:app --reload --host 127.0.0.1 --port 8000"
    exit 1
fi
echo ""

# Test 1: Root endpoint
echo "2️⃣  Testing root endpoint..."
ROOT_RESPONSE=$(curl -s "$BASE_URL/")
echo "$ROOT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ROOT_RESPONSE"
echo ""

# Test 2: Health check
echo "3️⃣  Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""

# Test 3: Register endpoint
echo "4️⃣  Testing register endpoint..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "testuser'$(date +%s)'@example.com",
    "password": "test123456"
  }')
echo "$REGISTER_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_RESPONSE"
echo ""

# Extract email from register response if successful
TEST_EMAIL=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('email', ''))" 2>/dev/null || echo "")

if [ -n "$TEST_EMAIL" ]; then
    # Test 4: Login endpoint
    echo "5️⃣  Testing login endpoint..."
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
      -H "Content-Type: application/json" \
      -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"test123456\"
      }")
    echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
    echo ""
    
    # Extract token
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access_token', ''))" 2>/dev/null || echo "")
    
    if [ -n "$TOKEN" ]; then
        # Test 5: Get current user
        echo "6️⃣  Testing /auth/me endpoint..."
        ME_RESPONSE=$(curl -s "$BASE_URL/auth/me" \
          -H "Authorization: Bearer $TOKEN")
        echo "$ME_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ME_RESPONSE"
        echo ""
    fi
else
    echo "⚠️  Registration failed, skipping login test"
    echo ""
fi

# Test 6: Properties endpoint
echo "7️⃣  Testing properties endpoint..."
PROPERTIES_RESPONSE=$(curl -s "$BASE_URL/properties?location=Mumbai&bedrooms=2")
echo "$PROPERTIES_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Found {len(data.get('properties', []))} properties\")" 2>/dev/null || echo "$PROPERTIES_RESPONSE"
echo ""

echo "✅ Backend tests completed!"
echo ""
echo "💡 To view API documentation, visit: http://127.0.0.1:8000/docs"

