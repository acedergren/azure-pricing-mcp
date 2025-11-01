# Azure Pricing MCP Models - Usage Examples

This document demonstrates how to use the Zod schemas for runtime validation and TypeScript types for compile-time safety.

## Installation

```bash
npm install zod
```

## Basic Usage

### Importing Schemas

```typescript
import { 
  PricingSearchSchema, 
  PricingSearchInput,
  CostEstimateSchema,
  CostEstimateInput 
} from './src/models/pricing.models';
```

### Example 1: Validating Pricing Search Input

```typescript
// Valid input - will pass
const searchInput = {
  service_name: 'Virtual Machines',
  region: 'eastus',
  limit: 10
};

try {
  const validated = PricingSearchSchema.parse(searchInput);
  console.log('Validated:', validated);
  // Output includes defaults: currency_code='USD', validate_sku=true
} catch (error) {
  console.error('Validation failed:', error);
}
```

### Example 2: Cost Estimation with Type Safety

```typescript
// Using TypeScript types for compile-time safety
const estimateInput: CostEstimateInput = {
  service_name: 'Virtual Machines',
  sku_name: 'Standard_D2s_v3',
  region: 'westeurope',
  hours_per_month: 160, // Part-time usage
  currency_code: 'EUR'
};

// Runtime validation
const validated = CostEstimateSchema.parse(estimateInput);
```

### Example 3: Handling Validation Errors

```typescript
try {
  // This will fail - limit exceeds maximum
  PricingSearchSchema.parse({
    service_name: 'Storage',
    limit: 2000  // Max is 1000
  });
} catch (error) {
  if (error instanceof z.ZodError) {
    console.error('Validation errors:', error.errors);
    // Shows detailed error about limit constraint
  }
}
```

### Example 4: Comparing Prices Across Regions

```typescript
import { PricingCompareSchema } from './src/models/pricing.models';

const compareInput = {
  service_name: 'Azure SQL Database',
  regions: ['eastus', 'westus', 'westeurope'],
  currency_code: 'USD',
  discount_percentage: 10
};

const validated = PricingCompareSchema.parse(compareInput);
```

### Example 5: SKU Discovery with Fuzzy Matching

```typescript
import { SKUDiscoverySchema } from './src/models/pricing.models';

const discoveryInput = {
  service_hint: 'app service',  // Fuzzy matching supported
  region: 'eastus',
  limit: 20
};

const validated = SKUDiscoverySchema.parse(discoveryInput);
```

## Validation Features

All schemas provide:

- **Strict Mode**: Rejects extra fields not defined in schema
- **Type Inference**: Automatically infer TypeScript types from schemas
- **Default Values**: Sensible defaults (USD currency, reasonable limits)
- **Range Validation**: Min/max constraints on numeric fields
- **Required vs Optional**: Clear distinction between required and optional fields

## Error Handling Best Practice

```typescript
import { z } from 'zod';

function validatePricingSearch(input: unknown) {
  const result = PricingSearchSchema.safeParse(input);
  
  if (!result.success) {
    // Handle validation errors gracefully
    return {
      success: false,
      errors: result.error.errors.map(err => ({
        field: err.path.join('.'),
        message: err.message
      }))
    };
  }
  
  return {
    success: true,
    data: result.data
  };
}
```

## Testing

All schemas have comprehensive test coverage. Run tests with:

```bash
npm test                # Run all tests
npm run test:coverage   # Run with coverage report
```

## Building

Compile TypeScript to JavaScript:

```bash
npm run build           # Compiles to dist/ folder
```

## Common Validation Rules

| Schema | Required Fields | Max Limits | Defaults |
|--------|----------------|------------|----------|
| PricingSearch | - | limit: 1000 | USD, limit: 50 |
| PricingCompare | service_name | - | USD |
| CostEstimate | service_name, sku_name, region | hours: 744 | USD, hours: 730 |
| DiscoverSKUs | service_name | limit: 1000 | Consumption, limit: 100 |
| SKUDiscovery | service_hint | limit: 100 | USD, limit: 30 |
| CustomerDiscount | - | - | - |
