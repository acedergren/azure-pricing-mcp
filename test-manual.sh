#!/bin/bash
# Manual testing script for Azure Pricing MCP Server

BASE_URL="${BASE_URL:-http://localhost:3000}"
echo "Testing Azure Pricing MCP Server at $BASE_URL"
echo "================================================"
echo

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
curl -s "$BASE_URL/health" | jq '.'
echo
echo

# Test 2: List Tools
echo "Test 2: List Available Tools"
echo "----------------------------"
curl -s -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' | jq '.result.tools[] | {name, description}'
echo
echo

# Test 3: Call Tool with Minimal Parameters
echo "Test 3: Call azure_price_search (minimal params)"
echo "------------------------------------------------"
curl -s -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"azure_price_search","arguments":{"limit":3}},"id":2}' | jq -r '.result.content[0].text | fromjson | .summary'
echo
echo

# Test 4: Call Tool with Service Filter
echo "Test 4: Call azure_price_search (with filters)"
echo "----------------------------------------------"
curl -s -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"azure_price_search","arguments":{"service":"Virtual Machines","region":"eastus","limit":5}},"id":3}' | jq -r '.result.content[0].text | fromjson | .summary'
echo
echo

# Test 5: Validation Error
echo "Test 5: Validation Error (invalid limit)"
echo "----------------------------------------"
curl -s -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"azure_price_search","arguments":{"limit":"invalid"}},"id":4}' | jq '.result.content[0].text | fromjson | {error, details: .details[0]}'
echo
echo

# Test 6: Unknown Tool Error
echo "Test 6: Unknown Tool Error"
echo "-------------------------"
curl -s -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"unknown_tool","arguments":{}},"id":5}' | jq '.error'
echo
echo

# Test 7: Invalid Method Error
echo "Test 7: Invalid Method Error"
echo "---------------------------"
curl -s -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"invalid/method","id":6}' | jq '.error'
echo
echo

# Test 8: Invalid JSON-RPC Version
echo "Test 8: Invalid JSON-RPC Version"
echo "-------------------------------"
curl -s -X POST "$BASE_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"1.0","method":"tools/list","id":7}' | jq '.error'
echo
echo

echo "================================================"
echo "All manual tests completed!"
echo
echo "Note: Tests 3 and 4 may show network errors if the"
echo "Azure Retail Prices API is not accessible from your"
echo "environment. This is expected behavior."
