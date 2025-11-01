import { z } from 'zod';

/**
 * Common enums and types for Azure Pricing MCP Tools
 */

// Currency codes supported by Azure Pricing API
export const CurrencyCodeSchema = z.enum(['USD', 'EUR', 'GBP', 'AUD', 'CAD', 'JPY', 'INR']);
export type CurrencyCode = z.infer<typeof CurrencyCodeSchema>;

// Price types available in Azure
export const PriceTypeSchema = z.enum(['Consumption', 'Reservation', 'DevTestConsumption']);
export type PriceType = z.infer<typeof PriceTypeSchema>;

/**
 * Tool 1: PricingSearchSchema
 * Search Azure retail prices with various filters
 * Based on: azure_price_search tool in Python implementation
 */
export const PricingSearchSchema = z.object({
  service_name: z.string().optional(),
  service_family: z.string().optional(),
  region: z.string().optional(),
  sku_name: z.string().optional(),
  price_type: PriceTypeSchema.optional(),
  currency_code: CurrencyCodeSchema.default('USD'),
  limit: z.number().int().min(1).max(1000).default(50),
  discount_percentage: z.number().min(0).max(100).optional(),
  validate_sku: z.boolean().default(true)
}).strict();

export type PricingSearchInput = z.infer<typeof PricingSearchSchema>;

/**
 * Tool 2: PricingCompareSchema
 * Compare Azure prices across regions or SKUs
 * Based on: azure_price_compare tool in Python implementation
 */
export const PricingCompareSchema = z.object({
  service_name: z.string().min(1),
  sku_name: z.string().optional(),
  regions: z.array(z.string()).optional(),
  currency_code: CurrencyCodeSchema.default('USD'),
  discount_percentage: z.number().min(0).max(100).optional()
}).strict();

export type PricingCompareInput = z.infer<typeof PricingCompareSchema>;

/**
 * Tool 3: CostEstimateSchema
 * Estimate Azure costs based on usage patterns
 * Based on: azure_cost_estimate tool in Python implementation
 */
export const CostEstimateSchema = z.object({
  service_name: z.string().min(1),
  sku_name: z.string().min(1),
  region: z.string().min(1),
  hours_per_month: z.number().min(0).max(744).default(730),
  currency_code: CurrencyCodeSchema.default('USD'),
  discount_percentage: z.number().min(0).max(100).optional()
}).strict();

export type CostEstimateInput = z.infer<typeof CostEstimateSchema>;

/**
 * Tool 4: DiscoverSKUsSchema
 * Discover available SKUs for a specific Azure service
 * Based on: azure_discover_skus tool in Python implementation
 */
export const DiscoverSKUsSchema = z.object({
  service_name: z.string().min(1),
  region: z.string().optional(),
  price_type: PriceTypeSchema.default('Consumption'),
  limit: z.number().int().min(1).max(1000).default(100)
}).strict();

export type DiscoverSKUsInput = z.infer<typeof DiscoverSKUsSchema>;

/**
 * Tool 5: SKUDiscoverySchema
 * Discover available SKUs for Azure services with intelligent name matching
 * Based on: azure_sku_discovery tool in Python implementation
 */
export const SKUDiscoverySchema = z.object({
  service_hint: z.string().min(1),
  region: z.string().optional(),
  currency_code: CurrencyCodeSchema.default('USD'),
  limit: z.number().int().min(1).max(100).default(30)
}).strict();

export type SKUDiscoveryInput = z.infer<typeof SKUDiscoverySchema>;

/**
 * Tool 6: CustomerDiscountSchema
 * Get customer discount information
 * Based on: get_customer_discount tool in Python implementation
 */
export const CustomerDiscountSchema = z.object({
  customer_id: z.string().optional()
}).strict();

export type CustomerDiscountInput = z.infer<typeof CustomerDiscountSchema>;
