#!/bin/bash
# Test the Medical Agent API using curl

echo "Testing Medical Agent API..."
echo "=========================="

# API base URL
BASE_URL="http://localhost:8000"

# 1. Check health
echo -e "\n1. Health Check:"
curl -s "$BASE_URL/health" | python3 -m json.tool

# 2. Get test customer
echo -e "\n2. Getting test customer:"
CUSTOMER_RESPONSE=$(curl -s "$BASE_URL/api/test-customer")
echo "$CUSTOMER_RESPONSE" | python3 -m json.tool
CUSTOMER_ID=$(echo "$CUSTOMER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['customer_id'])")

# 3. Analyze SOAP note file
echo -e "\n3. Analyzing SOAP note file:"
ANALYSIS_RESPONSE=$(curl -s -X POST "$BASE_URL/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "'$CUSTOMER_ID'",
    "type": "basic",
    "file_path": "/app/medical_files_data/sample_soap_note.txt"
  }')

echo "$ANALYSIS_RESPONSE" | python3 -m json.tool

# Extract job_id if present
JOB_ID=$(echo "$ANALYSIS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('job_id', ''))" 2>/dev/null || echo "")

if [ ! -z "$JOB_ID" ]; then
  echo -e "\n4. Checking job status (waiting 3 seconds):"
  sleep 3
  curl -s "$BASE_URL/api/job/$JOB_ID" | python3 -m json.tool
fi

# 5. Get billing tiers
echo -e "\n5. Available billing tiers:"
curl -s "$BASE_URL/api/billing/tiers" | python3 -m json.tool

# 6. Test with direct text
echo -e "\n6. Testing with direct text query:"
curl -s -X POST "$BASE_URL/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "'$CUSTOMER_ID'",
    "type": "comprehensive",
    "query": "Patient presents with headache, fever 101.5F, BP 130/85, HR 92"
  }' | python3 -m json.tool

echo -e "\n=========================="
echo "Test complete!"
