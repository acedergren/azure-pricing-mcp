# Azure Pricing MCP Server - Architecture

## Overview

The Azure Pricing MCP Server is a Model Context Protocol (MCP) server that provides tools for querying Azure retail pricing information. It acts as a bridge between AI assistants (like Claude) and the Azure Retail Prices API.

## Architecture Diagram

```
┌─────────────────────┐
│   AI Assistant      │
│   (Claude, etc.)    │
└──────────┬──────────┘
           │ MCP Protocol (stdio)
           │
┌──────────▼──────────────────────────────────────┐
│  Azure Pricing MCP Server                       │
│  ┌────────────────────────────────────────┐     │
│  │   MCP Handler Layer                    │     │
│  │   - List tools                         │     │
│  │   - Call tools                         │     │
│  │   - Tool schema definitions            │     │
│  └────────────┬───────────────────────────┘     │
│               │                                  │
│  ┌────────────▼───────────────────────────┐     │
│  │   Business Logic Layer                 │     │
│  │   - search_azure_prices()              │     │
│  │   - compare_prices()                   │     │
│  │   - estimate_costs()                   │     │
│  │   - discover_skus()                    │     │
│  │   - search_with_fuzzy_matching()       │     │
│  └────────────┬───────────────────────────┘     │
│               │                                  │
│  ┌────────────▼───────────────────────────┐     │
│  │   API Client Layer                     │     │
│  │   - HTTP session management            │     │
│  │   - Retry logic (rate limiting)        │     │
│  │   - Error handling                     │     │
│  └────────────┬───────────────────────────┘     │
└───────────────┼──────────────────────────────────┘
                │ HTTPS
┌───────────────▼──────────────────────────────────┐
│   Azure Retail Prices API                        │
│   https://prices.azure.com/api/retail/prices     │
└──────────────────────────────────────────────────┘
```

## Components

### 1. MCP Handler Layer

**Responsibility**: Handle MCP protocol communication

**Key Functions**:
- `list_tools()`: Returns available tools and their schemas
- `handle_call_tool()`: Routes tool calls to business logic
- Tool schema definitions using Pydantic models

**Technologies**:
- `mcp.server`: MCP server framework
- `mcp.server.stdio`: Standard I/O transport
- `pydantic`: Data validation and serialization

### 2. Business Logic Layer

**Responsibility**: Implement pricing query and analysis logic

**Key Components**:

#### AzurePricingServer Class
- Main server implementation
- Manages HTTP session lifecycle
- Coordinates API calls and data processing

#### Core Methods:

**`search_azure_prices()`**
- Searches Azure prices with flexible filters
- Supports SKU validation and suggestions
- Applies customer discounts
- Handles pagination

**`compare_prices()`**
- Compares prices across regions and SKUs
- Identifies cheapest options
- Calculates price differences

**`estimate_costs()`**
- Estimates monthly costs based on usage
- Supports custom hours per month
- Includes savings plan information

**`discover_skus()`**
- Discovers available SKUs for a service
- Groups by SKU name and product
- Tracks regional availability

**`search_azure_prices_with_fuzzy_matching()`**
- Performs fuzzy matching on service names
- Falls back to similar services
- Provides suggestions for typos

**`discover_service_skus()`**
- Intelligent SKU discovery
- Natural language query support
- Service hint matching

#### Helper Methods:

**`_validate_and_suggest_skus()`**
- Validates SKU names against API
- Suggests similar SKUs for typos
- Uses fuzzy string matching

**`_apply_discount_to_items()`**
- Applies percentage discounts
- Preserves original pricing
- Updates retail prices

**`_find_similar_services()`**
- Finds similar service names
- Uses Levenshtein distance
- Returns confidence scores

### 3. API Client Layer

**Responsibility**: Communicate with Azure Retail Prices API

**Key Features**:

**HTTP Session Management**
- Async context manager pattern
- Connection pooling via aiohttp
- Proper cleanup on exit

**Retry Logic**
- Handles 429 (Too Many Requests) errors
- Exponential backoff (5s, 10s, 15s)
- Configurable max retries (default: 3)

**Error Handling**
- HTTP errors (4xx, 5xx)
- Network errors
- Timeout handling
- Structured error responses

## Data Flow

### 1. Search Request Flow

```
AI Assistant → MCP Request → handle_call_tool() →
search_azure_prices() → _make_request() →
Azure API → Response Processing → JSON Result →
MCP Response → AI Assistant
```

### 2. Price Comparison Flow

```
compare_prices() →
  ├─ search_azure_prices(region1)
  ├─ search_azure_prices(region2)
  ├─ ...
  └─ Aggregate & Compare → Result
```

### 3. Cost Estimation Flow

```
estimate_costs() →
  ├─ search_azure_prices(specific_sku)
  ├─ Calculate hourly costs
  ├─ Apply usage multipliers
  └─ Format estimation result
```

## API Integration

### Azure Retail Prices API

**Endpoint**: `https://prices.azure.com/api/retail/prices`  
**Version**: `2023-01-01-preview`  
**Authentication**: None (public API)

**Query Parameters**:
- `$filter`: OData filter expressions
- `api-version`: API version
- `currencyCode`: Currency for pricing (USD, EUR, etc.)
- `$skip`: Pagination offset

**Response Format**:
```json
{
  "Count": 100,
  "Items": [
    {
      "currencyCode": "USD",
      "retailPrice": 0.096,
      "unitPrice": 0.096,
      "armRegionName": "eastus",
      "location": "US East",
      "serviceName": "Virtual Machines",
      "skuName": "D2s v3",
      ...
    }
  ],
  "NextPageLink": "..."
}
```

## Configuration

### Environment Variables
None required - API is public

### Constants
- `AZURE_PRICING_BASE_URL`: API endpoint
- `DEFAULT_API_VERSION`: API version
- `MAX_RESULTS_PER_REQUEST`: 1000

## Testing Architecture

### Test Structure
```
tests/
├── conftest.py              # Shared fixtures
├── test_pricing_search.py   # Search functionality tests
├── test_price_comparison.py # Comparison tests
├── test_cost_estimation.py  # Estimation tests
├── test_sku_discovery.py    # Discovery tests
└── test_integration.py      # API integration tests
```

### Test Types

**Unit Tests**
- Mock HTTP responses
- Test business logic in isolation
- Fast execution

**Integration Tests**
- Real API calls
- End-to-end workflows
- Marked with `@pytest.mark.integration`

## Performance Considerations

### Caching Strategy
Currently not implemented - potential enhancement:
- Cache API responses with TTL
- In-memory or Redis-based cache
- Invalidation strategies

### Rate Limiting
- Handled by retry logic
- Exponential backoff
- Respects Azure API limits

### Pagination
- Automatic pagination support
- Configurable result limits
- Memory-efficient streaming (potential enhancement)

## Security

### API Security
- No authentication required
- Public pricing data
- No sensitive information

### Input Validation
- Pydantic models for type safety
- Parameter validation
- SQL injection prevention (no SQL used)

### Error Handling
- No sensitive data in errors
- Structured error responses
- Logging for debugging

## Scalability

### Current Limitations
- Single process
- No caching
- Memory-bounded result sets

### Future Enhancements
- Multi-process support
- Caching layer
- Database for historical data
- Load balancing

## Deployment

### Current Model
- Runs locally via MCP
- Integrated with Claude Desktop
- Standard I/O communication

### Potential Deployments
- HTTP server mode
- Docker container
- Cloud function
- Kubernetes deployment

## Monitoring and Logging

### Logging
- Python `logging` module
- INFO level for operations
- ERROR level for failures
- Structured log messages

### Metrics (Future)
- Request count
- Response times
- Error rates
- Cache hit rates

## Dependencies

### Core Dependencies
- `mcp>=1.0.0`: MCP protocol
- `aiohttp>=3.9.0`: Async HTTP client
- `pydantic>=2.0.0`: Data validation

### Development Dependencies
- `pytest`: Testing framework
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting
- `black`, `isort`, `flake8`, `pylint`: Code quality

## Maintenance

### Version Management
- Semantic versioning
- CHANGELOG.md tracking
- GitHub releases

### Dependency Updates
- Dependabot automated PRs
- Weekly security scans
- Compatibility testing

## Future Architecture Enhancements

### Phase 2
- Caching layer
- Historical pricing data
- Cost optimization recommendations
- Alert system

### Phase 3
- Multi-cloud support (AWS, GCP)
- Machine learning for cost prediction
- Advanced analytics
- Web dashboard

---

For questions or suggestions about the architecture, please open an issue on GitHub.
