# Azure Pricing MCP Server - TypeScript Implementation

A Model Context Protocol (MCP) server built with Express.js and TypeScript that provides tools for querying Azure retail pricing information using the Azure Retail Prices API.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev

# Or build and run production
npm run build
npm start
```

The server will start on port 3000 (configurable via `PORT` environment variable).

## ✨ Features

- **Express.js Server**: RESTful API with MCP protocol support
- **TypeScript**: Full type safety and IntelliSense support
- **Winston Logging**: Structured JSON logging with configurable levels
- **Zod Validation**: Runtime type checking and validation
- **Azure Integration**: Direct integration with Azure Retail Prices API
- **MCP Protocol**: JSON-RPC 2.0 compliant implementation
- **Comprehensive Testing**: Integration tests with Jest and Supertest
- **Hot Reload**: Development mode with automatic reloading
- **ESLint**: Code quality and consistency checking

## 🛠️ Available Tools

### azure_price_search

Search Azure retail pricing information with flexible filtering options.

**Parameters:**
- `service` (optional): Azure service name (e.g., "Virtual Machines")
- `region` (optional): Azure region (e.g., "eastus")
- `limit` (optional): Maximum results to return (1-1000, default: 10)
- `armRegionName` (optional): ARM region name filter
- `location` (optional): Location filter
- `meterId` (optional): Meter ID filter
- `meterName` (optional): Meter name filter
- `productName` (optional): Product name filter
- `skuName` (optional): SKU name filter
- `serviceName` (optional): Service name filter
- `serviceFamily` (optional): Service family filter
- `priceType` (optional): Price type filter (e.g., "Consumption", "Reservation")
- `armSkuName` (optional): ARM SKU name filter
- `currencyCode` (optional): Currency code (default: "USD")

**Example Response:**
```json
{
  "summary": {
    "itemCount": 5,
    "currency": "USD",
    "hasMore": false
  },
  "items": [
    {
      "service": "Virtual Machines",
      "product": "Virtual Machines A Series",
      "sku": "A0",
      "region": "eastus",
      "location": "US East",
      "price": {
        "retail": 0.02,
        "unit": 0.02,
        "currency": "USD",
        "unitOfMeasure": "1 Hour"
      },
      "meter": {
        "id": "...",
        "name": "A0"
      },
      "effectiveDate": "2024-01-01T00:00:00Z",
      "priceType": "Consumption"
    }
  ]
}
```

## 📋 API Endpoints

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-11-01T12:00:00.000Z",
  "service": "azure-pricing-mcp",
  "version": "2.0.0"
}
```

### POST /mcp

MCP protocol endpoint for JSON-RPC 2.0 requests.

**Supported Methods:**
- `tools/list` - List available tools
- `tools/call` - Call a specific tool

**Example Request (tools/list):**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

**Example Request (tools/call):**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "azure_price_search",
    "arguments": {
      "service": "Virtual Machines",
      "region": "eastus",
      "limit": 5
    }
  },
  "id": 2
}
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Run integration tests
npm run test:integration

# Run linter
npm run lint

# Fix linting issues
npm run lint:fix

# Build TypeScript
npm run build
```

See [TESTING.md](TESTING.md) for comprehensive testing documentation.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
PORT=3000
LOG_LEVEL=info
NODE_ENV=development
```

### Available Settings

- `PORT`: Server port (default: 3000)
- `LOG_LEVEL`: Winston log level (debug, info, warn, error)
- `NODE_ENV`: Environment mode (development, production, test)

## 📁 Project Structure

```
.
├── src/
│   ├── server.ts                    # Main Express server
│   ├── controllers/
│   │   └── mcp.controller.ts        # MCP tool handlers
│   ├── services/
│   │   └── azure-pricing.service.ts # Azure API client
│   ├── schemas/
│   │   └── pricing.schema.ts        # Zod validation schemas
│   └── utils/
│       └── logger.ts                # Winston logger setup
├── tests/
│   └── integration/
│       └── mcp-server.test.ts       # Integration tests
├── dist/                             # Compiled JavaScript (gitignored)
├── package.json                      # Dependencies and scripts
├── tsconfig.json                     # TypeScript configuration
├── jest.config.js                    # Jest test configuration
├── .eslintrc.json                   # ESLint configuration
└── .env.example                      # Example environment file
```

## 🔌 Azure API Integration

This server uses the official Azure Retail Prices API:
- **Endpoint**: `https://prices.azure.com/api/retail/prices`
- **Version**: `2023-01-01-preview`
- **Authentication**: None required (public API)
- **Rate Limits**: Generous limits for retail pricing data

### OData Query Support

The Azure service supports OData filters for precise querying:
- `contains()`: Substring matching
- `eq`: Exact matching
- `and`: Combining multiple filters
- `tolower()`: Case-insensitive matching

## 📊 Logging

Structured JSON logging with Winston:

```json
{
  "timestamp": "2025-11-01T12:00:00.000Z",
  "level": "info",
  "message": "Azure Pricing MCP Server started",
  "service": "azure-pricing-mcp",
  "port": 3000,
  "env": "development"
}
```

## 🔒 Error Handling

The server provides comprehensive error handling:

1. **JSON-RPC Errors**:
   - `-32600`: Invalid Request (malformed JSON-RPC)
   - `-32601`: Method not found
   - `-32602`: Invalid params (unknown tool)
   - `-32603`: Internal error

2. **Validation Errors**:
   - Zod validation errors with detailed field-level messages

3. **Network Errors**:
   - Azure API connection failures
   - Timeout handling

## 🚦 Graceful Shutdown

The server handles SIGTERM and SIGINT signals for graceful shutdown:
- Closes active connections
- Logs shutdown events
- Exits cleanly

## 🔜 Future Enhancements

- [ ] Additional MCP tools (price comparison, cost estimation)
- [ ] Response caching with Redis
- [ ] Rate limiting middleware
- [ ] WebSocket support for real-time updates
- [ ] Metrics and monitoring (Prometheus)
- [ ] API key authentication
- [ ] Request/response compression
- [ ] Multi-region deployment support

## 📚 Documentation

- [TESTING.md](TESTING.md) - Comprehensive testing guide
- [QUICK_START.md](QUICK_START.md) - Original Python server quick start
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Usage examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`npm test`)
5. Ensure linting passes (`npm run lint`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙋‍♂️ Support

- Check [TESTING.md](TESTING.md) for troubleshooting
- Open an issue for bugs or feature requests
- Review existing documentation for common questions

---

*Built with Express.js, TypeScript, and the Model Context Protocol (MCP) for seamless integration with AI assistants.*
