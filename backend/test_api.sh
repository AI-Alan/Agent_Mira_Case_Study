#!/bin/bash

# Test script for Agent Mira API
BASE_URL="http://127.0.0.1:8000"

echo "🧪 Testing Agent Mira API"
echo "=========================="
echo ""

# Test 1: Health check
echo "1️⃣  Testing health endpoint..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Root endpoint
echo "2️⃣  Testing root endpoint..."
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""
echo ""

# Test 3: Register endpoint
echo "3️⃣  Testing register endpoint..."
curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "test123456"
  }' | python3 -m json.tool
echo ""
echo ""

# Test 4: Login endpoint
echo "4️⃣  Testing login endpoint..."
curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456"
  }' | python3 -m json.tool
echo ""
echo ""

echo "✅ Tests completed!"

