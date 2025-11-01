import type { Logger } from 'winston';
import { AzurePricingService } from '../services/azure-pricing.service.js';
import {
  PricingSearchSchema,
  MCPResult,
} from '../schemas/pricing.schema.js';
import { ZodError } from 'zod';

/**
 * Controller for handling MCP tool requests
 */
export class MCPController {
  constructor(
    private readonly azurePricingService: AzurePricingService,
    private readonly logger: Logger
  ) {}

  /**
   * Handle azure_price_search tool call
   */
  async handlePriceSearch(args: unknown): Promise<MCPResult> {
    try {
      this.logger.info('Handling price search request', { args });

      // Validate input with Zod
      const validated = PricingSearchSchema.parse(args);

      // Call Azure service
      const result = await this.azurePricingService.searchPricing(validated);

      // Format response for MCP
      const formattedResult = {
        summary: {
          itemCount: result.Items.length,
          currency: result.BillingCurrency,
          hasMore: !!result.NextPageLink,
        },
        items: result.Items.map((item) => ({
          service: item.serviceName,
          product: item.productName,
          sku: item.skuName,
          region: item.armRegionName,
          location: item.location,
          price: {
            retail: item.retailPrice,
            unit: item.unitPrice,
            currency: item.currencyCode,
            unitOfMeasure: item.unitOfMeasure,
          },
          meter: {
            id: item.meterId,
            name: item.meterName,
          },
          effectiveDate: item.effectiveStartDate,
          priceType: item.type,
        })),
      };

      this.logger.info('Price search completed successfully', {
        itemCount: result.Items.length,
      });

      // Return MCP-formatted response
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(formattedResult, null, 2),
          },
        ],
      };
    } catch (error) {
      this.logger.error('Error handling price search', { error });

      if (error instanceof ZodError) {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(
                {
                  error: 'Validation error',
                  details: error.errors,
                },
                null,
                2
              ),
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(
              {
                error: 'Internal error',
                message: error instanceof Error ? error.message : 'Unknown error',
              },
              null,
              2
            ),
          },
        ],
      };
    }
  }
}
