import axios, { AxiosInstance } from 'axios';
import type { Logger } from 'winston';
import {
  PricingSearchInput,
  AzurePricingResponse,
  AzurePricingResponseSchema,
} from '../schemas/pricing.schema.js';

/**
 * Service for interacting with Azure Retail Prices API
 */
export class AzurePricingService {
  private readonly apiBaseUrl = 'https://prices.azure.com/api/retail/prices';
  private readonly apiVersion = '2023-01-01-preview';
  private readonly client: AxiosInstance;

  constructor(private readonly logger: Logger) {
    this.client = axios.create({
      baseURL: this.apiBaseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Search Azure pricing based on filters
   */
  async searchPricing(input: PricingSearchInput): Promise<AzurePricingResponse> {
    try {
      this.logger.info('Searching Azure pricing', { input });

      // Build OData filter query
      const filters: string[] = [];

      if (input.service) {
        filters.push(`contains(tolower(serviceName), '${input.service.toLowerCase()}')`);
      }

      if (input.region) {
        filters.push(`armRegionName eq '${input.region}'`);
      }

      if (input.armRegionName) {
        filters.push(`armRegionName eq '${input.armRegionName}'`);
      }

      if (input.location) {
        filters.push(`location eq '${input.location}'`);
      }

      if (input.meterId) {
        filters.push(`meterId eq '${input.meterId}'`);
      }

      if (input.meterName) {
        filters.push(`contains(tolower(meterName), '${input.meterName.toLowerCase()}')`);
      }

      if (input.productName) {
        filters.push(`contains(tolower(productName), '${input.productName.toLowerCase()}')`);
      }

      if (input.skuName) {
        filters.push(`contains(tolower(skuName), '${input.skuName.toLowerCase()}')`);
      }

      if (input.serviceName) {
        filters.push(`contains(tolower(serviceName), '${input.serviceName.toLowerCase()}')`);
      }

      if (input.serviceFamily) {
        filters.push(`serviceFamily eq '${input.serviceFamily}'`);
      }

      if (input.priceType) {
        filters.push(`priceType eq '${input.priceType}'`);
      }

      if (input.armSkuName) {
        filters.push(`armSkuName eq '${input.armSkuName}'`);
      }

      const filterQuery = filters.length > 0 ? filters.join(' and ') : undefined;

      // Build query parameters
      const params: Record<string, string> = {
        'api-version': this.apiVersion,
        currencyCode: input.currencyCode || 'USD',
      };

      if (filterQuery) {
        params.$filter = filterQuery;
      }

      // Set top parameter for limit
      params.$top = Math.min(input.limit || 10, 1000).toString();

      this.logger.debug('Executing Azure API request', { params });

      // Make API request
      const response = await this.client.get('', { params });

      // Validate and parse response
      const validatedResponse = AzurePricingResponseSchema.parse(response.data);

      this.logger.info('Azure pricing search completed', {
        itemCount: validatedResponse.Items.length,
        hasNextPage: !!validatedResponse.NextPageLink,
      });

      return validatedResponse;
    } catch (error) {
      this.logger.error('Error searching Azure pricing', { error });
      throw error;
    }
  }
}
