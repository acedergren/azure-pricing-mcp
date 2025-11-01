import axios, { AxiosInstance, AxiosError } from 'axios';
import { Logger } from 'winston';
import {
  PricingSearchSchema,
  PricingSearchInput,
  PricingSearchResult,
  PricingCompareSchema,
  PricingCompareInput,
  ComparisonResult,
  CostEstimateSchema,
  CostEstimateInput,
  CostEstimate,
  DiscoverSKUsSchema,
  DiscoverSKUsInput,
  DiscoverSKUsResult,
  SKUDiscoverySchema,
  SKUDiscoveryInput,
  CustomerDiscountSchema,
  CustomerDiscountInput,
  CustomerDiscount,
  PricingItem,
  SKUInfo,
  ComparisonItem,
} from '../models/pricing.models';
import { AzureAPIError, RateLimitError, ValidationError } from '../utils/errors';

export interface AzurePricingServiceConfig {
  logger: Logger;
  cache?: unknown;
  timeout?: number;
  maxRetries?: number;
}

interface AzureAPIResponse {
  Items: PricingItem[];
  Count: number;
  NextPageLink?: string;
}

export class AzurePricingService {
  private readonly client: AxiosInstance;
  private readonly logger: Logger;
  private readonly baseURL = 'https://prices.azure.com/api/retail/prices';
  private readonly apiVersion = '2023-01-01-preview';
  private readonly maxResultsPerRequest = 1000;
  private readonly maxRetries: number;

  constructor(config: AzurePricingServiceConfig) {
    this.logger = config.logger;
    this.maxRetries = config.maxRetries ?? 3;
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: config.timeout ?? 30000,
      headers: {
        'Accept': 'application/json',
      },
    });
  }

  /**
   * Search Azure retail prices with various filters
   */
  async searchPricing(params: PricingSearchInput): Promise<PricingSearchResult> {
    // Validate input
    const validated = PricingSearchSchema.parse(params);
    
    this.logger.info('Searching Azure pricing', { params: validated });

    // Build filter conditions
    const filters: string[] = [];
    if (validated.service) {
      filters.push(`serviceName eq '${validated.service}'`);
    }
    if (validated.serviceFamily) {
      filters.push(`serviceFamily eq '${validated.serviceFamily}'`);
    }
    if (validated.region) {
      filters.push(`armRegionName eq '${validated.region}'`);
    }
    if (validated.skuName) {
      filters.push(`contains(skuName, '${validated.skuName}')`);
    }
    if (validated.priceType) {
      filters.push(`priceType eq '${validated.priceType}'`);
    }

    // Construct query parameters
    const queryParams: Record<string, string> = {
      'api-version': this.apiVersion,
      'currencyCode': validated.currencyCode,
    };

    if (filters.length > 0) {
      queryParams['$filter'] = filters.join(' and ');
    }

    if (validated.limit < this.maxResultsPerRequest) {
      queryParams['$top'] = validated.limit.toString();
    }

    try {
      const response = await this.makeRequestWithRetry<AzureAPIResponse>(queryParams);
      
      let items = response.Items || [];
      
      // Truncate if needed
      if (items.length > validated.limit) {
        items = items.slice(0, validated.limit);
      }

      // SKU validation and clarification
      let skuValidation;
      let clarification;
      
      if (validated.validateSku && validated.skuName && items.length === 0) {
        skuValidation = await this.validateAndSuggestSKUs(
          validated.service,
          validated.skuName,
          validated.currencyCode
        );
      } else if (validated.validateSku && validated.skuName && items.length > 10) {
        clarification = {
          message: `Found ${items.length} SKUs matching '${validated.skuName}'. Consider being more specific.`,
          suggestions: items.slice(0, 5).map(item => item.skuName).filter(Boolean) as string[],
        };
      }

      // Apply discount if provided
      if (validated.discountPercentage && validated.discountPercentage > 0) {
        items = this.applyDiscountToItems(items, validated.discountPercentage);
      }

      const result: PricingSearchResult = {
        items,
        count: items.length,
        hasMore: !!response.NextPageLink,
        nextLink: response.NextPageLink,
        currency: validated.currencyCode,
        filtersApplied: filters,
      };

      if (validated.discountPercentage && validated.discountPercentage > 0) {
        result.discountApplied = {
          percentage: validated.discountPercentage,
          note: 'Prices shown are after discount',
        };
      }

      if (skuValidation) {
        result.skuValidation = skuValidation;
      }

      if (clarification) {
        result.clarification = clarification;
      }

      this.logger.info('Price search completed', { count: items.length });
      return result;

    } catch (error) {
      this.logger.error('Azure API error during price search', { error });
      if (error instanceof ValidationError || error instanceof RateLimitError) {
        throw error;
      }
      throw new AzureAPIError('Failed to fetch pricing', error);
    }
  }

  /**
   * Compare prices across different regions or SKUs
   */
  async comparePricing(params: PricingCompareInput): Promise<ComparisonResult> {
    const validated = PricingCompareSchema.parse(params);
    
    this.logger.info('Comparing pricing', { params: validated });

    const comparisons: ComparisonItem[] = [];

    if (validated.regions && validated.regions.length > 0) {
      // Compare across regions
      for (const region of validated.regions) {
        try {
          const result = await this.searchPricing({
            service: validated.service,
            skuName: validated.skuName,
            region,
            currencyCode: validated.currencyCode,
            limit: 10,
            validateSku: false,
          });

          if (result.items.length > 0) {
            const item = result.items[0];
            comparisons.push({
              region,
              skuName: item.skuName,
              retailPrice: item.retailPrice,
              unitOfMeasure: item.unitOfMeasure,
              productName: item.productName,
              meterName: item.meterName,
            });
          }
        } catch (error) {
          this.logger.warn(`Failed to get prices for region ${region}`, { error });
        }
      }
    } else {
      // Compare different SKUs within the same service
      const result = await this.searchPricing({
        service: validated.service,
        currencyCode: validated.currencyCode,
        limit: 20,
        validateSku: false,
      });

      // Group by SKU
      const skuPrices = new Map<string, ComparisonItem>();
      for (const item of result.items) {
        if (item.skuName && !skuPrices.has(item.skuName)) {
          skuPrices.set(item.skuName, {
            skuName: item.skuName,
            retailPrice: item.retailPrice,
            unitOfMeasure: item.unitOfMeasure,
            productName: item.productName,
            meterName: item.meterName,
            region: item.armRegionName,
          });
        }
      }

      comparisons.push(...skuPrices.values());
    }

    // Apply discount if provided
    if (validated.discountPercentage && validated.discountPercentage > 0) {
      for (const comparison of comparisons) {
        const originalPrice = comparison.retailPrice;
        comparison.retailPrice = this.roundPrice(
          originalPrice * (1 - validated.discountPercentage / 100)
        );
        comparison.originalPrice = originalPrice;
      }
    }

    // Sort by price
    comparisons.sort((a, b) => a.retailPrice - b.retailPrice);

    const result: ComparisonResult = {
      comparisons,
      service: validated.service,
      currency: validated.currencyCode,
      comparisonType: validated.regions && validated.regions.length > 0 ? 'regions' : 'skus',
    };

    if (validated.discountPercentage && validated.discountPercentage > 0) {
      result.discountApplied = {
        percentage: validated.discountPercentage,
        note: 'Prices shown are after discount',
      };
    }

    this.logger.info('Price comparison completed', { comparisons: comparisons.length });
    return result;
  }

  /**
   * Estimate monthly costs based on usage
   */
  async estimateCost(params: CostEstimateInput): Promise<CostEstimate> {
    const validated = CostEstimateSchema.parse(params);
    
    this.logger.info('Estimating costs', { params: validated });

    const result = await this.searchPricing({
      service: validated.service,
      skuName: validated.skuName,
      region: validated.region,
      currencyCode: validated.currencyCode,
      limit: 5,
      validateSku: false,
    });

    if (result.items.length === 0) {
      throw new AzureAPIError(
        `No pricing found for ${validated.skuName} in ${validated.region}`
      );
    }

    const item = result.items[0];
    let hourlyRate = item.retailPrice;
    let originalHourlyRate: number | undefined;

    // Apply discount if provided
    if (validated.discountPercentage && validated.discountPercentage > 0) {
      originalHourlyRate = hourlyRate;
      hourlyRate = hourlyRate * (1 - validated.discountPercentage / 100);
    }

    // Calculate estimates
    const monthlyCost = hourlyRate * validated.hoursPerMonth;
    const dailyCost = hourlyRate * 24;
    const yearlyCost = monthlyCost * 12;

    // Process savings plans
    const savingsPlans = (item.savingsPlan || []).map(plan => {
      let planHourly = plan.retailPrice;
      let originalPlanHourly: number | undefined;

      if (validated.discountPercentage && validated.discountPercentage > 0) {
        originalPlanHourly = planHourly;
        planHourly = planHourly * (1 - validated.discountPercentage / 100);
      }

      const planMonthly = planHourly * validated.hoursPerMonth;
      const planYearly = planMonthly * 12;
      const savingsPercent = hourlyRate > 0 
        ? ((hourlyRate - planHourly) / hourlyRate) * 100 
        : 0;

      const planData: CostEstimate['savingsPlans'][0] = {
        term: plan.term,
        hourlyRate: this.roundPrice(planHourly),
        monthlyCost: this.roundPrice(planMonthly, 2),
        yearlyCost: this.roundPrice(planYearly, 2),
        savingsPercent: this.roundPrice(savingsPercent, 2),
        annualSavings: this.roundPrice(yearlyCost - planYearly, 2),
      };

      if (originalPlanHourly !== undefined) {
        planData.originalHourlyRate = originalPlanHourly;
        planData.originalMonthlyCost = this.roundPrice(
          originalPlanHourly * validated.hoursPerMonth,
          2
        );
        planData.originalYearlyCost = this.roundPrice(
          originalPlanHourly * validated.hoursPerMonth * 12,
          2
        );
      }

      return planData;
    });

    const estimate: CostEstimate = {
      service: validated.service,
      skuName: item.skuName,
      region: validated.region,
      productName: item.productName,
      unitOfMeasure: item.unitOfMeasure,
      currency: validated.currencyCode,
      onDemandPricing: {
        hourlyRate: this.roundPrice(hourlyRate),
        dailyCost: this.roundPrice(dailyCost, 2),
        monthlyCost: this.roundPrice(monthlyCost, 2),
        yearlyCost: this.roundPrice(yearlyCost, 2),
      },
      usageAssumptions: {
        hoursPerMonth: validated.hoursPerMonth,
        hoursPerDay: this.roundPrice(validated.hoursPerMonth / 30.44, 2),
      },
      savingsPlans,
    };

    if (originalHourlyRate !== undefined) {
      estimate.onDemandPricing.originalHourlyRate = originalHourlyRate;
      estimate.onDemandPricing.originalDailyCost = this.roundPrice(
        originalHourlyRate * 24,
        2
      );
      estimate.onDemandPricing.originalMonthlyCost = this.roundPrice(
        originalHourlyRate * validated.hoursPerMonth,
        2
      );
      estimate.onDemandPricing.originalYearlyCost = this.roundPrice(
        originalHourlyRate * validated.hoursPerMonth * 12,
        2
      );
    }

    if (validated.discountPercentage && validated.discountPercentage > 0) {
      estimate.discountApplied = {
        percentage: validated.discountPercentage,
        note: 'All prices shown are after discount',
      };
    }

    this.logger.info('Cost estimation completed');
    return estimate;
  }

  /**
   * Discover available SKUs for a specific Azure service
   */
  async discoverSKUs(params: DiscoverSKUsInput): Promise<DiscoverSKUsResult> {
    const validated = DiscoverSKUsSchema.parse(params);
    
    this.logger.info('Discovering SKUs', { params: validated });

    const filters: string[] = [`serviceName eq '${validated.service}'`];
    
    if (validated.region) {
      filters.push(`armRegionName eq '${validated.region}'`);
    }
    
    if (validated.priceType) {
      filters.push(`priceType eq '${validated.priceType}'`);
    }

    const queryParams: Record<string, string> = {
      'api-version': this.apiVersion,
      'currencyCode': 'USD',
      '$filter': filters.join(' and '),
    };

    if (validated.limit < this.maxResultsPerRequest) {
      queryParams['$top'] = validated.limit.toString();
    }

    const response = await this.makeRequestWithRetry<AzureAPIResponse>(queryParams);
    
    // Deduplicate and process SKUs
    const skusMap = new Map<string, SKUInfo>();
    const items = response.Items || [];

    for (const item of items) {
      const skuName = item.skuName;
      if (!skuName) continue;

      if (!skusMap.has(skuName)) {
        skusMap.set(skuName, {
          skuName,
          armSkuName: item.armSkuName,
          productName: item.productName,
          samplePrice: item.retailPrice,
          unitOfMeasure: item.unitOfMeasure,
          meterName: item.meterName,
          sampleRegion: item.armRegionName,
          availableRegions: item.armRegionName ? [item.armRegionName] : [],
        });
      } else if (item.armRegionName) {
        const sku = skusMap.get(skuName)!;
        if (!sku.availableRegions.includes(item.armRegionName)) {
          sku.availableRegions.push(item.armRegionName);
        }
      }
    }

    // Convert to list and sort
    const skuList = Array.from(skusMap.values()).sort((a, b) =>
      a.skuName.localeCompare(b.skuName)
    );

    const result: DiscoverSKUsResult = {
      service: validated.service,
      skus: skuList,
      totalSkus: skuList.length,
      priceType: validated.priceType,
      regionFilter: validated.region,
    };

    this.logger.info('SKU discovery completed', { totalSkus: skuList.length });
    return result;
  }

  /**
   * Intelligent SKU discovery with fuzzy matching
   */
  async intelligentSKUDiscovery(params: SKUDiscoveryInput): Promise<SKUInfo[]> {
    const validated = SKUDiscoverySchema.parse(params);
    
    this.logger.info('Intelligent SKU discovery', { params: validated });

    // First try exact search
    const exactResult = await this.searchPricing({
      service: validated.service,
      serviceFamily: validated.serviceFamily,
      region: validated.region,
      skuName: validated.skuName,
      priceType: validated.priceType,
      currencyCode: validated.currencyCode,
      limit: validated.limit,
      validateSku: false,
    });

    if (exactResult.items.length > 0) {
      // Convert items to SKUInfo
      return this.convertItemsToSKUInfo(exactResult.items);
    }

    // If no results and suggest alternatives is enabled, try fuzzy matching
    if (validated.suggestAlternatives && (validated.service || validated.serviceFamily)) {
      return await this.findSimilarServices(
        validated.service,
        validated.serviceFamily,
        validated.skuName,
        validated.currencyCode,
        validated.limit
      );
    }

    return [];
  }

  /**
   * Calculate customer discount (returns default 10% discount)
   */
  async calculateDiscount(params: CustomerDiscountInput): Promise<PricingItem[]> {
    const validated = CustomerDiscountSchema.parse(params);
    
    this.logger.info('Calculating customer discount', { params: validated });

    // For now, return a default 10% discount
    // This method returns the discount info, not applied to specific items
    // The discount is applied in other methods via the discountPercentage parameter
    
    // Return empty array as this method should return pricing items with discount applied
    // In a real implementation, this would fetch customer-specific pricing
    return [];
  }

  /**
   * Get customer discount information
   */
  async getCustomerDiscount(params: CustomerDiscountInput): Promise<CustomerDiscount> {
    const validated = CustomerDiscountSchema.parse(params);
    
    this.logger.info('Getting customer discount', { params: validated });

    return {
      customerId: validated.customerId || 'default',
      discountPercentage: 10.0,
      discountType: 'standard',
      description: 'Standard customer discount',
      validUntil: undefined,
      applicableServices: 'all',
      note: 'This is a default discount applied to all customers. Contact sales for enterprise discounts.',
    };
  }

  /**
   * Make HTTP request with retry logic
   */
  private async makeRequestWithRetry<T>(
    params: Record<string, string>,
    attempt = 0
  ): Promise<T> {
    try {
      const response = await this.client.get<T>('', { params });
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError;

      // Handle rate limiting (429)
      if (axiosError.response?.status === 429) {
        const waitTime = 5 * (attempt + 1); // 5, 10, 15 seconds
        if (attempt < this.maxRetries) {
          this.logger.warn(
            `Rate limited (429). Retrying in ${waitTime} seconds... (attempt ${attempt + 1}/${this.maxRetries + 1})`
          );
          await this.sleep(waitTime * 1000);
          return this.makeRequestWithRetry<T>(params, attempt + 1);
        } else {
          throw new RateLimitError('Rate limit exceeded', waitTime);
        }
      }

      // Handle other HTTP errors with retry
      if (axiosError.response && attempt < this.maxRetries) {
        const waitTime = Math.pow(2, attempt) * 1000; // Exponential backoff: 1s, 2s, 4s
        this.logger.warn(
          `Request failed with status ${axiosError.response.status}. Retrying in ${waitTime}ms... (attempt ${attempt + 1}/${this.maxRetries + 1})`
        );
        await this.sleep(waitTime);
        return this.makeRequestWithRetry<T>(params, attempt + 1);
      }

      // Handle network errors (no response) with retry
      if (!axiosError.response && attempt < this.maxRetries) {
        const waitTime = Math.pow(2, attempt) * 1000; // Exponential backoff: 1s, 2s, 4s
        this.logger.warn(
          `Network error. Retrying in ${waitTime}ms... (attempt ${attempt + 1}/${this.maxRetries + 1})`
        );
        await this.sleep(waitTime);
        return this.makeRequestWithRetry<T>(params, attempt + 1);
      }

      // No more retries or non-retryable error
      throw error;
    }
  }

  /**
   * Validate SKU name and suggest alternatives
   */
  private async validateAndSuggestSKUs(
    service: string | undefined,
    skuName: string,
    currencyCode: string
  ) {
    const suggestions: SKUInfo[] = [];

    if (service) {
      const broadSearch = await this.searchPricing({
        service,
        currencyCode,
        limit: 100,
        validateSku: false,
      });

      const skuLower = skuName.toLowerCase();
      for (const item of broadSearch.items) {
        if (!item.skuName) continue;

        const itemSkuLower = item.skuName.toLowerCase();
        const words = skuLower.split(' ').filter(w => w);

        if (
          skuLower === itemSkuLower ||
          itemSkuLower.includes(skuLower) ||
          skuLower.includes(itemSkuLower) ||
          words.some(word => itemSkuLower.includes(word))
        ) {
          suggestions.push({
            skuName: item.skuName,
            armSkuName: item.armSkuName,
            productName: item.productName,
            samplePrice: item.retailPrice,
            unitOfMeasure: item.unitOfMeasure,
            meterName: item.meterName,
            sampleRegion: item.armRegionName,
            availableRegions: [item.armRegionName],
          });

          if (suggestions.length >= 5) break;
        }
      }
    }

    return {
      originalSku: skuName,
      found: false,
      message: `SKU '${skuName}' not found${service ? ` in service '${service}'` : ''}`,
      suggestions,
    };
  }

  /**
   * Apply discount to pricing items
   */
  private applyDiscountToItems(
    items: PricingItem[],
    discountPercentage: number
  ): PricingItem[] {
    return items.map(item => {
      const discountedItem = { ...item };

      // Apply to retail price
      if (item.retailPrice !== undefined) {
        discountedItem.originalPrice = item.retailPrice;
        discountedItem.retailPrice = this.roundPrice(
          item.retailPrice * (1 - discountPercentage / 100)
        );
      }

      // Apply to savings plans
      if (item.savingsPlan && Array.isArray(item.savingsPlan)) {
        discountedItem.savingsPlan = item.savingsPlan.map(plan => ({
          ...plan,
          originalPrice: plan.retailPrice,
          retailPrice: this.roundPrice(
            plan.retailPrice * (1 - discountPercentage / 100)
          ),
        }));
      }

      return discountedItem;
    });
  }

  /**
   * Convert pricing items to SKU info
   */
  private convertItemsToSKUInfo(items: PricingItem[]): SKUInfo[] {
    const skusMap = new Map<string, SKUInfo>();

    for (const item of items) {
      if (!item.skuName) continue;

      if (!skusMap.has(item.skuName)) {
        skusMap.set(item.skuName, {
          skuName: item.skuName,
          armSkuName: item.armSkuName,
          productName: item.productName,
          samplePrice: item.retailPrice,
          unitOfMeasure: item.unitOfMeasure,
          meterName: item.meterName,
          sampleRegion: item.armRegionName,
          availableRegions: item.armRegionName ? [item.armRegionName] : [],
        });
      } else if (item.armRegionName) {
        const sku = skusMap.get(item.skuName)!;
        if (!sku.availableRegions.includes(item.armRegionName)) {
          sku.availableRegions.push(item.armRegionName);
        }
      }
    }

    return Array.from(skusMap.values());
  }

  /**
   * Find similar services using fuzzy matching
   */
  private async findSimilarServices(
    service: string | undefined,
    serviceFamily: string | undefined,
    skuName: string | undefined,
    currencyCode: string,
    limit: number
  ): Promise<SKUInfo[]> {
    // Try broader search
    const result = await this.searchPricing({
      service,
      serviceFamily,
      currencyCode,
      limit,
      validateSku: false,
    });

    return this.convertItemsToSKUInfo(result.items);
  }

  /**
   * Round price to specified decimal places
   */
  private roundPrice(price: number, decimals = 6): number {
    return Math.round(price * Math.pow(10, decimals)) / Math.pow(10, decimals);
  }

  /**
   * Sleep helper
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
