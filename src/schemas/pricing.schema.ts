import { z } from 'zod';

/**
 * Schema for pricing search input
 */
export const PricingSearchSchema = z.object({
  service: z.string().optional().describe('Azure service name (e.g., "Virtual Machines")'),
  region: z.string().optional().describe('Azure region (e.g., "eastus")'),
  limit: z.number().int().positive().max(1000).default(10).describe('Maximum number of results to return'),
  armRegionName: z.string().optional().describe('ARM region name filter'),
  location: z.string().optional().describe('Location filter'),
  meterId: z.string().optional().describe('Meter ID filter'),
  meterName: z.string().optional().describe('Meter name filter'),
  productName: z.string().optional().describe('Product name filter'),
  skuName: z.string().optional().describe('SKU name filter'),
  serviceName: z.string().optional().describe('Service name filter'),
  serviceFamily: z.string().optional().describe('Service family filter'),
  priceType: z.string().optional().describe('Price type filter (e.g., "Consumption", "Reservation")'),
  armSkuName: z.string().optional().describe('ARM SKU name filter'),
  currencyCode: z.string().default('USD').describe('Currency code (default: USD)'),
});

export type PricingSearchInput = z.infer<typeof PricingSearchSchema>;

/**
 * Schema for Azure pricing item response
 */
export const AzurePricingItemSchema = z.object({
  currencyCode: z.string(),
  tierMinimumUnits: z.number(),
  retailPrice: z.number(),
  unitPrice: z.number(),
  armRegionName: z.string(),
  location: z.string(),
  effectiveStartDate: z.string(),
  meterId: z.string(),
  meterName: z.string(),
  productId: z.string(),
  skuId: z.string(),
  productName: z.string(),
  skuName: z.string(),
  serviceName: z.string(),
  serviceId: z.string(),
  serviceFamily: z.string(),
  unitOfMeasure: z.string(),
  type: z.string(),
  isPrimaryMeterRegion: z.boolean(),
  armSkuName: z.string().optional(),
  reservationTerm: z.string().optional(),
  savingsPlan: z.array(z.any()).optional(),
});

export type AzurePricingItem = z.infer<typeof AzurePricingItemSchema>;

/**
 * Schema for Azure pricing API response
 */
export const AzurePricingResponseSchema = z.object({
  BillingCurrency: z.string(),
  CustomerEntityId: z.string(),
  CustomerEntityType: z.string(),
  Items: z.array(AzurePricingItemSchema),
  NextPageLink: z.string().optional(),
  Count: z.number(),
});

export type AzurePricingResponse = z.infer<typeof AzurePricingResponseSchema>;

/**
 * Schema for MCP tool result
 */
export const MCPResultSchema = z.object({
  content: z.array(
    z.object({
      type: z.literal('text'),
      text: z.string(),
    })
  ),
});

export type MCPResult = z.infer<typeof MCPResultSchema>;
