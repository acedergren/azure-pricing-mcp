# Testing Guide for Azure Pricing MCP Server

This guide covers testing the TypeScript/Express-based MCP server implementation.

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

## Installation

```bash
npm install
```

## Building the Project

```bash
npm run build
```

The compiled JavaScript will be in the `dist/` directory.

## Running the Server

### Development Mode (with hot reload)

```bash
npm run dev
```

The server will start on port 3000 (or the port specified in the `PORT` environment variable).

### Production Mode

```bash
npm run build
npm start
```

## Running Tests

### All Tests

```bash
npm test
```

### Integration Tests Only

```bash
npm run test:integration
```

**Note:** Some tests may fail in restricted network environments because they try to connect to the Azure Retail Prices API. This is expected behavior.

## Linting

```bash
npm run lint
```

To automatically fix linting issues:

```bash
npm run lint:fix
```

## Manual Testing with cURL

### 1. Health Check

```bash
curl http://localhost:3000/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2025-11-01T12:00:00.000Z",
  "service": "azure-pricing-mcp",
  "version": "2.0.0"
}
```

### 2. List Available Tools

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

Expected response includes the `azure_price_search` tool with its schema.

### 3. Call the azure_price_search Tool

#### With minimal parameters:

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"azure_price_search","arguments":{"limit":5}},"id":2}'
```

#### With service and region filters:

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"azure_price_search","arguments":{"service":"Virtual Machines","region":"eastus","limit":10}},"id":3}'
```

#### With multiple filters:

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"azure_price_search","arguments":{"service":"Storage","region":"westus2","limit":5,"currencyCode":"EUR"}},"id":4}'
```

### 4. Test Error Handling

#### Invalid JSON-RPC version:

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"1.0","method":"tools/list","id":1}'
```

Expected: Error with code -32600 (Invalid Request)

#### Unknown method:

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"unknown/method","id":1}'
```

Expected: Error with code -32601 (Method not found)

#### Unknown tool:

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"unknown_tool","arguments":{}},"id":1}'
```

Expected: Error with code -32602 (Unknown tool)

#### Validation error (invalid limit type):

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"azure_price_search","arguments":{"limit":"invalid"}},"id":1}'
```

Expected: Validation error details from Zod

## Success Criteria Checklist

- [x] Express server starts on port 3000
- [x] Health endpoint returns 200 OK
- [x] MCP endpoint accepts JSON-RPC
- [x] Tool `azure_price_search` works end-to-end (requires network access)
- [x] Proper error responses (MCP protocol)
- [x] Winston logging to console (structured JSON)
- [x] Integration test calling the tool
- [x] Can test with curl commands
- [x] `npm run build` passes
- [x] `npm run lint` passes
- [x] `npm run dev` runs server with hot reload

## Logs

The server uses Winston for structured JSON logging. In development mode, logs are colorized for better readability.

Log levels:
- `info`: General information about server operations
- `debug`: Detailed debugging information (set LOG_LEVEL=debug)
- `error`: Error messages with stack traces

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Available variables:
- `PORT`: Server port (default: 3000)
- `LOG_LEVEL`: Logging level (default: info)
- `NODE_ENV`: Environment (development/production)

## Troubleshooting

### Network Errors

If you see "ENOTFOUND prices.azure.com" errors:
- This indicates the Azure API is not accessible from your environment
- Check network connectivity and firewall settings
- The error handling is working correctly - it's just reporting the network issue

### Build Errors

If TypeScript compilation fails:
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Test Failures

Some tests may fail in restricted environments due to network limitations. This is expected behavior for tests that make actual API calls.

## Architecture

```
src/
├── server.ts              # Main Express server with MCP protocol
├── controllers/
│   └── mcp.controller.ts  # MCP tool handlers
├── services/
│   └── azure-pricing.service.ts  # Azure API client
├── schemas/
│   └── pricing.schema.ts  # Zod validation schemas
└── utils/
    └── logger.ts          # Winston logger configuration

tests/
└── integration/
    └── mcp-server.test.ts # Integration tests
```

## Next Steps

- Add more MCP tools (price comparison, cost estimation, etc.)
- Add unit tests for individual services
- Add mock Azure API responses for testing
- Implement caching for Azure API responses
- Add rate limiting
