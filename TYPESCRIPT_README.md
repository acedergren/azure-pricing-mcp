# Azure Pricing Service - TypeScript Implementation

TypeScript port of the Python Azure Retail Prices API client with full error handling, retry logic, and comprehensive tests.

## Features

- ✅ Full TypeScript implementation of Azure Pricing Service
- ✅ 6 core methods implemented:
  - `searchPricing` - Search Azure retail prices with filters
  - `comparePricing` - Compare prices across regions or SKUs
  - `estimateCost` - Estimate costs based on usage
  - `discoverSKUs` - Discover available SKUs for a service
  - `intelligentSKUDiscovery` - Fuzzy matching SKU discovery
  - `calculateDiscount` - Apply customer discounts
- ✅ Retry logic with exponential backoff
- ✅ Rate limiting (429) handling
- ✅ Winston logging integration
- ✅ Zod schema validation
- ✅ Comprehensive test suite (37 tests, >90% coverage)
- ✅ Fully typed with TypeScript

## Installation

```bash
npm install
```

## Build

```bash
npm run build
```

## Test

```bash
npm test
npm run test:coverage  # With coverage report
```

## Lint

```bash
npm run lint
npm run lint:fix  # Auto-fix issues
```

## Usage

```typescript
import { AzurePricingService } from './services/azure-pricing.service';
import winston from 'winston';

// Create logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [new winston.transports.Console()],
});

// Create service
const service = new AzurePricingService({
  logger,
  timeout: 30000,
  maxRetries: 3,
});

// Search pricing
const result = await service.searchPricing({
  service: 'Virtual Machines',
  region: 'eastus',
  skuName: 'D2s v3',
});

console.log(result.items);
```

## API Methods

### searchPricing(params)

Search Azure retail prices with various filters.

```typescript
await service.searchPricing({
  service: 'Virtual Machines',
  region: 'eastus',
  skuName: 'D2s',
  priceType: 'Consumption',
  currencyCode: 'USD',
  limit: 50,
  discountPercentage: 10,
  validateSku: true,
});
```

### comparePricing(params)

Compare prices across different regions or SKUs.

```typescript
await service.comparePricing({
  service: 'Virtual Machines',
  regions: ['eastus', 'westus', 'northeurope'],
  currencyCode: 'USD',
  discountPercentage: 10,
});
```

### estimateCost(params)

Estimate monthly costs based on usage.

```typescript
await service.estimateCost({
  service: 'Virtual Machines',
  skuName: 'D2s v3',
  region: 'eastus',
  hoursPerMonth: 730,
  currencyCode: 'USD',
  discountPercentage: 10,
});
```

### discoverSKUs(params)

Discover available SKUs for a service.

```typescript
await service.discoverSKUs({
  service: 'Virtual Machines',
  region: 'eastus',
  priceType: 'Consumption',
  limit: 100,
});
```

### intelligentSKUDiscovery(params)

Intelligent SKU discovery with fuzzy matching.

```typescript
await service.intelligentSKUDiscovery({
  service: 'Virtual Machines',
  skuName: 'D2',
  suggestAlternatives: true,
  currencyCode: 'USD',
  limit: 50,
});
```

## Error Handling

The service includes custom error classes:

- `AzureAPIError` - General API errors
- `RateLimitError` - Rate limiting (429) errors
- `ValidationError` - Input validation errors

All errors are logged using Winston logger and include original error context.

## Retry Logic

- Automatic retry on network errors (exponential backoff: 1s, 2s, 4s)
- Rate limit (429) handling with linear backoff (5s, 10s, 15s)
- Configurable max retries (default: 3)
- Detailed logging for debugging

## Test Coverage

- **Statements**: 90.65%
- **Branches**: 82.35%
- **Functions**: 92.59%
- **Lines**: 92.43%

All tests use mocked axios responses and fake timers for fast execution.

## Development

```bash
# Install dependencies
npm install

# Run tests in watch mode
npm test -- --watch

# Build TypeScript
npm run build

# Clean build artifacts
npm run clean
```

## License

MIT
