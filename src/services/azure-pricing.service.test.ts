import axios from 'axios';
import { AzurePricingService } from './azure-pricing.service';
import { Logger } from 'winston';
import { AzureAPIError, RateLimitError } from '../utils/errors';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Create a mock logger
const createMockLogger = (): Logger => {
  return {
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
    debug: jest.fn(),
  } as unknown as Logger;
};

// Mock pricing item
const createMockPricingItem = (overrides = {}) => ({
  currencyCode: 'USD',
  tierMinimumUnits: 0,
  retailPrice: 0.096,
  unitPrice: 0.096,
  armRegionName: 'eastus',
  location: 'US East',
  effectiveStartDate: '2023-01-01T00:00:00Z',
  meterId: 'test-meter-id',
  meterName: 'D2s v3',
  productId: 'test-product-id',
  skuId: 'test-sku-id',
  productName: 'Virtual Machines Dsv3 Series',
  skuName: 'D2s v3',
  serviceName: 'Virtual Machines',
  serviceId: 'test-service-id',
  serviceFamily: 'Compute',
  unitOfMeasure: '1 Hour',
  type: 'Consumption',
  isPrimaryMeterRegion: true,
  armSkuName: 'Standard_D2s_v3',
  ...overrides,
});

describe('AzurePricingService', () => {
  let service: AzurePricingService;
  let mockLogger: Logger;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let mockAxiosInstance: any;

  beforeEach(() => {
    mockLogger = createMockLogger();
    
    // Mock axios.create
    mockAxiosInstance = {
      get: jest.fn(),
    };
    mockedAxios.create = jest.fn().mockReturnValue(mockAxiosInstance);

    service = new AzurePricingService({ logger: mockLogger });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('searchPricing', () => {
    it('should search pricing with valid params', async () => {
      const mockResponse = {
        Items: [createMockPricingItem()],
        Count: 1,
        NextPageLink: null,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.searchPricing({
        service: 'Virtual Machines',
        region: 'eastus',
      });

      expect(result.items).toHaveLength(1);
      expect(result.count).toBe(1);
      expect(result.hasMore).toBe(false);
      expect(result.currency).toBe('USD');
      expect(mockLogger.info).toHaveBeenCalled();
    });

    it('should apply filters correctly', async () => {
      const mockResponse = {
        Items: [createMockPricingItem()],
        Count: 1,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      await service.searchPricing({
        service: 'Virtual Machines',
        region: 'eastus',
        skuName: 'D2s',
        priceType: 'Consumption',
      });

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('', {
        params: expect.objectContaining({
          '$filter': expect.stringContaining("serviceName eq 'Virtual Machines'"),
        }),
      });
    });

    it('should apply discount when provided', async () => {
      const mockResponse = {
        Items: [createMockPricingItem({ retailPrice: 100 })],
        Count: 1,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.searchPricing({
        service: 'Virtual Machines',
        discountPercentage: 10,
      });

      expect(result.items[0].retailPrice).toBe(90);
      expect(result.items[0].originalPrice).toBe(100);
      expect(result.discountApplied).toBeDefined();
      expect(result.discountApplied?.percentage).toBe(10);
    });

    it('should handle pagination info', async () => {
      const mockResponse = {
        Items: [createMockPricingItem()],
        Count: 1,
        NextPageLink: 'https://prices.azure.com/api/retail/prices?$skip=100',
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.searchPricing({
        service: 'Virtual Machines',
      });

      expect(result.hasMore).toBe(true);
      expect(result.nextLink).toBeDefined();
    });

    it('should throw AzureAPIError on request failure', async () => {
      jest.useFakeTimers();
      mockAxiosInstance.get.mockRejectedValue(new Error('Network error'));

      const promise = service.searchPricing({ service: 'Virtual Machines' });
      
      // Advance timers and expect the rejection
      const expectPromise = expect(promise).rejects.toThrow(AzureAPIError);
      await jest.runAllTimersAsync();
      await expectPromise;

      expect(mockLogger.error).toHaveBeenCalled();
      jest.useRealTimers();
    });

    it('should validate input with Zod', async () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      await expect(
        service.searchPricing({ limit: 2000 } as any)
      ).rejects.toThrow();
    });

    it('should provide SKU clarification when many results found', async () => {
      const mockItems = Array(15).fill(null).map((_, i) => 
        createMockPricingItem({ skuName: `D${i}s v3` })
      );

      const mockResponse = {
        Items: mockItems,
        Count: 15,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.searchPricing({
        service: 'Virtual Machines',
        skuName: 'D',
      });

      expect(result.clarification).toBeDefined();
      expect(result.clarification?.message).toContain('Consider being more specific');
    });

    it('should provide SKU validation when no results found', async () => {
      const mockResponse = {
        Items: [],
        Count: 0,
      };

      mockAxiosInstance.get
        .mockResolvedValueOnce({ data: mockResponse })
        .mockResolvedValueOnce({
          data: {
            Items: [createMockPricingItem({ skuName: 'Similar SKU' })],
            Count: 1,
          },
        });

      const result = await service.searchPricing({
        service: 'Virtual Machines',
        skuName: 'InvalidSKU',
        validateSku: true,
      });

      expect(result.skuValidation).toBeDefined();
      expect(result.skuValidation?.found).toBe(false);
      expect(result.skuValidation?.originalSku).toBe('InvalidSKU');
    });

    it('should handle SKU validation without service name', async () => {
      const mockResponse = {
        Items: [],
        Count: 0,
      };

      mockAxiosInstance.get.mockResolvedValueOnce({ data: mockResponse });

      const result = await service.searchPricing({
        skuName: 'InvalidSKU',
        validateSku: true,
      });

      expect(result.skuValidation).toBeDefined();
      expect(result.skuValidation?.suggestions).toHaveLength(0);
    });
  });

  describe('comparePricing', () => {
    it('should compare prices across regions', async () => {
      const mockResponse1 = {
        Items: [createMockPricingItem({ armRegionName: 'eastus', retailPrice: 0.096 })],
        Count: 1,
      };
      const mockResponse2 = {
        Items: [createMockPricingItem({ armRegionName: 'westus', retailPrice: 0.110 })],
        Count: 1,
      };

      mockAxiosInstance.get
        .mockResolvedValueOnce({ data: mockResponse1 })
        .mockResolvedValueOnce({ data: mockResponse2 });

      const result = await service.comparePricing({
        service: 'Virtual Machines',
        regions: ['eastus', 'westus'],
      });

      expect(result.comparisons).toHaveLength(2);
      expect(result.comparisonType).toBe('regions');
      expect(result.comparisons[0].retailPrice).toBeLessThanOrEqual(result.comparisons[1].retailPrice);
    });

    it('should compare SKUs within a service', async () => {
      const mockResponse = {
        Items: [
          createMockPricingItem({ skuName: 'D2s v3', retailPrice: 0.096 }),
          createMockPricingItem({ skuName: 'D4s v3', retailPrice: 0.192 }),
        ],
        Count: 2,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.comparePricing({
        service: 'Virtual Machines',
      });

      expect(result.comparisons).toHaveLength(2);
      expect(result.comparisonType).toBe('skus');
    });

    it('should apply discount to comparisons', async () => {
      const mockResponse = {
        Items: [createMockPricingItem({ retailPrice: 100 })],
        Count: 1,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.comparePricing({
        service: 'Virtual Machines',
        regions: ['eastus'],
        discountPercentage: 20,
      });

      expect(result.comparisons[0].retailPrice).toBe(80);
      expect(result.comparisons[0].originalPrice).toBe(100);
    });

    it('should handle region comparison failures gracefully', async () => {
      jest.useFakeTimers();
      mockAxiosInstance.get
        .mockResolvedValueOnce({ data: { Items: [createMockPricingItem()], Count: 1 } })
        .mockRejectedValueOnce(new Error('Region not available'));

      const promise = service.comparePricing({
        service: 'Virtual Machines',
        regions: ['eastus', 'invalidregion'],
      });

      await jest.runAllTimersAsync();
      const result = await promise;

      expect(result.comparisons).toHaveLength(1);
      expect(mockLogger.warn).toHaveBeenCalled();
      jest.useRealTimers();
    });
  });

  describe('estimateCost', () => {
    it('should estimate monthly costs', async () => {
      const mockResponse = {
        Items: [createMockPricingItem({ retailPrice: 0.096 })],
        Count: 1,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.estimateCost({
        service: 'Virtual Machines',
        skuName: 'D2s v3',
        region: 'eastus',
        hoursPerMonth: 730,
      });

      expect(result.onDemandPricing.hourlyRate).toBe(0.096);
      expect(result.onDemandPricing.monthlyCost).toBeCloseTo(70.08, 2);
      expect(result.onDemandPricing.yearlyCost).toBeCloseTo(840.96, 2);
      expect(result.usageAssumptions.hoursPerMonth).toBe(730);
    });

    it('should include savings plans in estimates', async () => {
      const mockResponse = {
        Items: [
          createMockPricingItem({
            retailPrice: 0.096,
            savingsPlan: [
              { term: '1 Year', retailPrice: 0.065 },
              { term: '3 Year', retailPrice: 0.051 },
            ],
          }),
        ],
        Count: 1,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.estimateCost({
        service: 'Virtual Machines',
        skuName: 'D2s v3',
        region: 'eastus',
      });

      expect(result.savingsPlans).toHaveLength(2);
      expect(result.savingsPlans[0].term).toBe('1 Year');
      expect(result.savingsPlans[0].savingsPercent).toBeGreaterThan(0);
    });

    it('should apply discount to estimates', async () => {
      const mockResponse = {
        Items: [createMockPricingItem({ retailPrice: 1.0 })],
        Count: 1,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.estimateCost({
        service: 'Virtual Machines',
        skuName: 'D2s v3',
        region: 'eastus',
        hoursPerMonth: 100,
        discountPercentage: 10,
      });

      expect(result.onDemandPricing.hourlyRate).toBe(0.9);
      expect(result.onDemandPricing.originalHourlyRate).toBe(1.0);
      expect(result.discountApplied).toBeDefined();
    });

    it('should throw error when no pricing found', async () => {
      const mockResponse = {
        Items: [],
        Count: 0,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      await expect(
        service.estimateCost({
          service: 'Virtual Machines',
          skuName: 'InvalidSKU',
          region: 'eastus',
        })
      ).rejects.toThrow(AzureAPIError);
    });
  });

  describe('discoverSKUs', () => {
    it('should discover available SKUs', async () => {
      const mockResponse = {
        Items: [
          createMockPricingItem({ skuName: 'D2s v3' }),
          createMockPricingItem({ skuName: 'D4s v3' }),
        ],
        Count: 2,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.discoverSKUs({
        service: 'Virtual Machines',
      });

      expect(result.skus).toHaveLength(2);
      expect(result.totalSkus).toBe(2);
      expect(result.service).toBe('Virtual Machines');
    });

    it('should deduplicate SKUs', async () => {
      const mockResponse = {
        Items: [
          createMockPricingItem({ skuName: 'D2s v3', armRegionName: 'eastus' }),
          createMockPricingItem({ skuName: 'D2s v3', armRegionName: 'westus' }),
        ],
        Count: 2,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.discoverSKUs({
        service: 'Virtual Machines',
      });

      expect(result.skus).toHaveLength(1);
      expect(result.skus[0].availableRegions).toHaveLength(2);
    });

    it('should filter by region', async () => {
      const mockResponse = {
        Items: [createMockPricingItem()],
        Count: 1,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      await service.discoverSKUs({
        service: 'Virtual Machines',
        region: 'eastus',
      });

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('', {
        params: expect.objectContaining({
          '$filter': expect.stringContaining("armRegionName eq 'eastus'"),
        }),
      });
    });
  });

  describe('intelligentSKUDiscovery', () => {
    it('should return exact matches when found', async () => {
      const mockResponse = {
        Items: [createMockPricingItem({ skuName: 'D2s v3' })],
        Count: 1,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.intelligentSKUDiscovery({
        service: 'Virtual Machines',
        skuName: 'D2s',
      });

      expect(result).toHaveLength(1);
      expect(result[0].skuName).toBe('D2s v3');
    });

    it('should return empty array when no matches and suggest disabled', async () => {
      const mockResponse = {
        Items: [],
        Count: 0,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.intelligentSKUDiscovery({
        service: 'Virtual Machines',
        skuName: 'InvalidSKU',
        suggestAlternatives: false,
      });

      expect(result).toHaveLength(0);
    });

    it('should suggest alternatives when no exact matches', async () => {
      mockAxiosInstance.get
        .mockResolvedValueOnce({ data: { Items: [], Count: 0 } })
        .mockResolvedValueOnce({
          data: {
            Items: [createMockPricingItem({ skuName: 'D2s v3' })],
            Count: 1,
          },
        });

      await service.intelligentSKUDiscovery({
        service: 'Virtual Machines',
        skuName: 'D2',
        suggestAlternatives: true,
      });

      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(2);
    });
  });

  describe('calculateDiscount', () => {
    it('should return empty array for now', async () => {
      const result = await service.calculateDiscount({
        customerId: 'test-customer',
      });

      expect(result).toEqual([]);
      expect(mockLogger.info).toHaveBeenCalled();
    });
  });

  describe('getCustomerDiscount', () => {
    it('should return default discount information', async () => {
      const result = await service.getCustomerDiscount({
        customerId: 'test-customer',
      });

      expect(result.customerId).toBe('test-customer');
      expect(result.discountPercentage).toBe(10.0);
      expect(result.discountType).toBe('standard');
    });

    it('should use default customer ID when not provided', async () => {
      const result = await service.getCustomerDiscount({});

      expect(result.customerId).toBe('default');
    });
  });

  describe('retry logic', () => {
    beforeEach(() => {
      jest.useFakeTimers();
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should retry on network error', async () => {
      mockAxiosInstance.get
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          data: { Items: [createMockPricingItem()], Count: 1 },
        });

      const promise = service.searchPricing({
        service: 'Virtual Machines',
      });

      // Fast-forward timers
      await jest.runAllTimersAsync();
      const result = await promise;

      expect(result.items).toHaveLength(1);
      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(2);
    });

    it('should handle rate limiting (429) with backoff', async () => {
      const rateLimitError = {
        response: { status: 429 },
        isAxiosError: true,
      };

      mockAxiosInstance.get
        .mockRejectedValueOnce(rateLimitError)
        .mockResolvedValueOnce({
          data: { Items: [createMockPricingItem()], Count: 1 },
        });

      const promise = service.searchPricing({
        service: 'Virtual Machines',
      });

      // Fast-forward timers
      await jest.runAllTimersAsync();
      const result = await promise;

      expect(result.items).toHaveLength(1);
      expect(mockLogger.warn).toHaveBeenCalledWith(
        expect.stringContaining('Rate limited')
      );
    });

    it('should throw RateLimitError after max retries', async () => {
      const rateLimitError = {
        response: { status: 429 },
        isAxiosError: true,
      };

      mockAxiosInstance.get.mockRejectedValue(rateLimitError);

      const promise = service.searchPricing({ service: 'Virtual Machines' });

      // Fast-forward timers and expect the rejection
      const expectPromise = expect(promise).rejects.toThrow(RateLimitError);
      await jest.runAllTimersAsync();
      await expectPromise;

      expect(mockAxiosInstance.get).toHaveBeenCalledTimes(4); // Initial + 3 retries
    });

    it('should use exponential backoff for non-429 errors', async () => {
      const serverError = {
        response: { status: 500 },
        isAxiosError: true,
      };

      mockAxiosInstance.get
        .mockRejectedValueOnce(serverError)
        .mockResolvedValueOnce({
          data: { Items: [createMockPricingItem()], Count: 1 },
        });

      const promise = service.searchPricing({
        service: 'Virtual Machines',
      });

      // Fast-forward timers
      await jest.runAllTimersAsync();
      const result = await promise;

      expect(result.items).toHaveLength(1);
      expect(mockLogger.warn).toHaveBeenCalledWith(
        expect.stringContaining('Request failed')
      );
    });
  });

  describe('edge cases', () => {
    it('should handle empty Items array', async () => {
      const mockResponse = {
        Items: [],
        Count: 0,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.searchPricing({
        service: 'NonExistent Service',
      });

      expect(result.items).toHaveLength(0);
      expect(result.count).toBe(0);
    });

    it('should handle missing optional fields in pricing items', async () => {
      const mockResponse = {
        Items: [
          {
            retailPrice: 0.096,
            skuName: 'D2s v3',
            serviceName: 'Virtual Machines',
            // Missing many optional fields
          },
        ],
        Count: 1,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.searchPricing({
        service: 'Virtual Machines',
      });

      expect(result.items).toHaveLength(1);
    });

    it('should handle very large discount percentages', async () => {
      const mockResponse = {
        Items: [createMockPricingItem({ retailPrice: 100 })],
        Count: 1,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      await expect(
        service.searchPricing({
          service: 'Virtual Machines',
          discountPercentage: 101,
        })
      ).rejects.toThrow();
    });

    it('should handle zero pricing', async () => {
      const mockResponse = {
        Items: [createMockPricingItem({ retailPrice: 0 })],
        Count: 1,
      };

      mockAxiosInstance.get.mockResolvedValue({ data: mockResponse });

      const result = await service.estimateCost({
        service: 'Virtual Machines',
        skuName: 'Free Tier',
        region: 'eastus',
      });

      expect(result.onDemandPricing.hourlyRate).toBe(0);
      expect(result.onDemandPricing.monthlyCost).toBe(0);
    });
  });

  describe('configuration', () => {
    it('should accept custom timeout', () => {
      const customService = new AzurePricingService({
        logger: mockLogger,
        timeout: 60000,
      });

      expect(customService).toBeDefined();
    });

    it('should accept custom max retries', () => {
      const customService = new AzurePricingService({
        logger: mockLogger,
        maxRetries: 5,
      });

      expect(customService).toBeDefined();
    });

    it('should accept cache instance', () => {
      const mockCache = {};
      const customService = new AzurePricingService({
        logger: mockLogger,
        cache: mockCache,
      });

      expect(customService).toBeDefined();
    });
  });
});
