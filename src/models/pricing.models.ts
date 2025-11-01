import { z } from 'zod';

/**
 * Zod schemas for Azure Pricing Service inputs and outputs
 */

// Input schemas
export const PricingSearchSchema = z.object({
  service: z.string().optional(),
  serviceFamily: z.string().optional(),
  region: z.string().optional(),
  skuName: z.string().optional(),
  priceType: z.string().optional(),
  currencyCode: z.string().default('USD'),
  limit: z.number().min(1).max(1000).default(50),
  discountPercentage: z.number().min(0).max(100).optional(),
  validateSku: z.boolean().default(true),
});

export const PricingCompareSchema = z.object({
  service: z.string(),
  skuName: z.string().optional(),
  regions: z.array(z.string()).optional(),
  currencyCode: z.string().default('USD'),
  discountPercentage: z.number().min(0).max(100).optional(),
});

export const CostEstimateSchema = z.object({
  service: z.string(),
  skuName: z.string(),
  region: z.string(),
  hoursPerMonth: z.number().min(0).default(730),
  currencyCode: z.string().default('USD'),
  discountPercentage: z.number().min(0).max(100).optional(),
});

export const DiscoverSKUsSchema = z.object({
  service: z.string(),
  region: z.string().optional(),
  priceType: z.string().default('Consumption'),
  limit: z.number().min(1).max(1000).default(100),
});

export const SKUDiscoverySchema = z.object({
  service: z.string().optional(),
  serviceFamily: z.string().optional(),
  region: z.string().optional(),
  skuName: z.string().optional(),
  priceType: z.string().optional(),
  currencyCode: z.string().default('USD'),
  limit: z.number().min(1).max(1000).default(50),
  suggestAlternatives: z.boolean().default(true),
});

export const CustomerDiscountSchema = z.object({
  customerId: z.string().optional(),
});

// Type exports - use z.input for input types (before defaults applied)
export type PricingSearchInput = z.input<typeof PricingSearchSchema>;
export type PricingCompareInput = z.input<typeof PricingCompareSchema>;
export type CostEstimateInput = z.input<typeof CostEstimateSchema>;
export type DiscoverSKUsInput = z.input<typeof DiscoverSKUsSchema>;
export type SKUDiscoveryInput = z.input<typeof SKUDiscoverySchema>;
export type CustomerDiscountInput = z.input<typeof CustomerDiscountSchema>;

// Output types
export interface PricingItem {
  currencyCode: string;
  tierMinimumUnits: number;
  retailPrice: number;
  unitPrice: number;
  armRegionName: string;
  location: string;
  effectiveStartDate: string;
  meterId: string;
  meterName: string;
  productId: string;
  skuId: string;
  productName: string;
  skuName: string;
  serviceName: string;
  serviceId: string;
  serviceFamily: string;
  unitOfMeasure: string;
  type: string;
  isPrimaryMeterRegion: boolean;
  armSkuName: string;
  originalPrice?: number;
  savingsPlan?: SavingsPlan[];
}

export interface SavingsPlan {
  term: string;
  retailPrice: number;
  originalPrice?: number;
}

export interface PricingSearchResult {
  items: PricingItem[];
  count: number;
  hasMore: boolean;
  nextLink?: string;
  currency: string;
  filtersApplied: string[];
  discountApplied?: {
    percentage: number;
    note: string;
  };
  skuValidation?: {
    originalSku: string;
    found: boolean;
    message: string;
    suggestions: SKUInfo[];
  };
  clarification?: {
    message: string;
    suggestions: string[];
  };
}

export interface ComparisonItem {
  region?: string;
  skuName?: string;
  retailPrice: number;
  unitOfMeasure: string;
  productName: string;
  meterName: string;
  originalPrice?: number;
}

export interface ComparisonResult {
  comparisons: ComparisonItem[];
  service: string;
  currency: string;
  comparisonType: 'regions' | 'skus';
  discountApplied?: {
    percentage: number;
    note: string;
  };
}

export interface CostEstimate {
  service: string;
  skuName: string;
  region: string;
  productName: string;
  unitOfMeasure: string;
  currency: string;
  onDemandPricing: {
    hourlyRate: number;
    dailyCost: number;
    monthlyCost: number;
    yearlyCost: number;
    originalHourlyRate?: number;
    originalDailyCost?: number;
    originalMonthlyCost?: number;
    originalYearlyCost?: number;
  };
  usageAssumptions: {
    hoursPerMonth: number;
    hoursPerDay: number;
  };
  savingsPlans: Array<{
    term: string;
    hourlyRate: number;
    monthlyCost: number;
    yearlyCost: number;
    savingsPercent: number;
    annualSavings: number;
    originalHourlyRate?: number;
    originalMonthlyCost?: number;
    originalYearlyCost?: number;
  }>;
  discountApplied?: {
    percentage: number;
    note: string;
  };
}

export interface SKUInfo {
  skuName: string;
  armSkuName?: string;
  productName: string;
  samplePrice: number;
  unitOfMeasure: string;
  meterName: string;
  sampleRegion: string;
  availableRegions: string[];
}

export interface DiscoverSKUsResult {
  service: string;
  skus: SKUInfo[];
  totalSkus: number;
  priceType: string;
  regionFilter?: string;
}

export interface CustomerDiscount {
  customerId: string;
  discountPercentage: number;
  discountType: string;
  description: string;
  validUntil?: string;
  applicableServices: string;
  note: string;
}
