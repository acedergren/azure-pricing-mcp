# TypeScript Type Models for Azure Pricing MCP

This directory contains TypeScript type definitions and Zod validation schemas for the Azure Pricing MCP Server tools.

## Overview

The models provide:
- ✅ **Runtime Validation** using Zod schemas
- ✅ **Type Safety** with TypeScript types
- ✅ **Strict Mode** validation (rejects extra fields)
- ✅ **100% Test Coverage** with comprehensive test suite

## Files

- `pricing.models.ts` - Zod schemas and TypeScript types for all 6 MCP tools
- `pricing.models.test.ts` - Comprehensive test suite with 47 test cases
- `../index.ts` - Central export file for easy imports

## Schemas Included

### 1. PricingSearchSchema
Search Azure retail prices with various filters including service name, region, SKU, and price type.

### 2. PricingCompareSchema
Compare Azure prices across different regions or SKUs for the same service.

### 3. CostEstimateSchema
Estimate Azure costs based on usage patterns (hours per month).

### 4. DiscoverSKUsSchema
Discover available SKUs for a specific Azure service.

### 5. SKUDiscoverySchema
Intelligent SKU discovery with fuzzy matching for service names.

### 6. CustomerDiscountSchema
Get customer discount information for pricing calculations.

## Usage

```typescript
import { PricingSearchSchema, PricingSearchInput } from './models/pricing.models';

// Validate input at runtime
const input = {
  service_name: 'Virtual Machines',
  region: 'eastus',
  limit: 10
};

const validated = PricingSearchSchema.parse(input);
// validated has type PricingSearchInput
```

See [MODELS_USAGE.md](../MODELS_USAGE.md) for more detailed examples.

## Testing

Run the test suite:

```bash
npm test                # Run all tests
npm run test:coverage   # Run with coverage report
```

## Quality Metrics

- **Test Cases**: 47 comprehensive tests
- **Coverage**: 100% (branches, functions, lines, statements)
- **TypeScript**: Strict mode enabled
- **Validation**: Zod strict mode for all schemas
