import {
  CurrencyCodeSchema,
  PriceTypeSchema,
  PricingSearchSchema,
  PricingCompareSchema,
  CostEstimateSchema,
  DiscoverSKUsSchema,
  SKUDiscoverySchema,
  CustomerDiscountSchema
} from './pricing.models';

describe('CurrencyCodeSchema', () => {
  it('validates supported currency codes', () => {
    expect(() => CurrencyCodeSchema.parse('USD')).not.toThrow();
    expect(() => CurrencyCodeSchema.parse('EUR')).not.toThrow();
    expect(() => CurrencyCodeSchema.parse('GBP')).not.toThrow();
  });

  it('rejects invalid currency codes', () => {
    expect(() => CurrencyCodeSchema.parse('INVALID')).toThrow();
    expect(() => CurrencyCodeSchema.parse('usd')).toThrow();
  });
});

describe('PriceTypeSchema', () => {
  it('validates supported price types', () => {
    expect(() => PriceTypeSchema.parse('Consumption')).not.toThrow();
    expect(() => PriceTypeSchema.parse('Reservation')).not.toThrow();
    expect(() => PriceTypeSchema.parse('DevTestConsumption')).not.toThrow();
  });

  it('rejects invalid price types', () => {
    expect(() => PriceTypeSchema.parse('Invalid')).toThrow();
  });
});

describe('PricingSearchSchema', () => {
  it('validates minimal valid input', () => {
    const input = {};
    const result = PricingSearchSchema.parse(input);
    expect(result.currency_code).toBe('USD');
    expect(result.limit).toBe(50);
    expect(result.validate_sku).toBe(true);
  });

  it('validates complete valid input', () => {
    const input = {
      service_name: 'Virtual Machines',
      service_family: 'Compute',
      region: 'eastus',
      sku_name: 'Standard_D2s_v3',
      price_type: 'Consumption' as const,
      currency_code: 'EUR' as const,
      limit: 100,
      discount_percentage: 10,
      validate_sku: false
    };
    expect(() => PricingSearchSchema.parse(input)).not.toThrow();
  });

  it('rejects limit below 1', () => {
    const input = { limit: 0 };
    expect(() => PricingSearchSchema.parse(input)).toThrow();
  });

  it('rejects limit above 1000', () => {
    const input = { limit: 1001 };
    expect(() => PricingSearchSchema.parse(input)).toThrow();
  });

  it('rejects negative discount percentage', () => {
    const input = { discount_percentage: -5 };
    expect(() => PricingSearchSchema.parse(input)).toThrow();
  });

  it('rejects discount percentage above 100', () => {
    const input = { discount_percentage: 101 };
    expect(() => PricingSearchSchema.parse(input)).toThrow();
  });

  it('rejects invalid currency code', () => {
    const input = { currency_code: 'INVALID' };
    expect(() => PricingSearchSchema.parse(input)).toThrow();
  });

  it('rejects invalid price type', () => {
    const input = { price_type: 'Invalid' };
    expect(() => PricingSearchSchema.parse(input)).toThrow();
  });

  it('rejects extra fields in strict mode', () => {
    const input = { extra_field: 'value' };
    expect(() => PricingSearchSchema.parse(input)).toThrow();
  });
});

describe('PricingCompareSchema', () => {
  it('validates minimal required input', () => {
    const input = { service_name: 'Virtual Machines' };
    const result = PricingCompareSchema.parse(input);
    expect(result.service_name).toBe('Virtual Machines');
    expect(result.currency_code).toBe('USD');
  });

  it('validates complete valid input with regions', () => {
    const input = {
      service_name: 'Storage',
      sku_name: 'Standard_LRS',
      regions: ['eastus', 'westus', 'westeurope'],
      currency_code: 'EUR' as const,
      discount_percentage: 15
    };
    expect(() => PricingCompareSchema.parse(input)).not.toThrow();
  });

  it('rejects empty service name', () => {
    const input = { service_name: '' };
    expect(() => PricingCompareSchema.parse(input)).toThrow();
  });

  it('rejects missing service name', () => {
    const input = {};
    expect(() => PricingCompareSchema.parse(input)).toThrow();
  });

  it('rejects invalid discount percentage', () => {
    const input = { service_name: 'VM', discount_percentage: 150 };
    expect(() => PricingCompareSchema.parse(input)).toThrow();
  });

  it('rejects extra fields in strict mode', () => {
    const input = { service_name: 'VM', extra: 'field' };
    expect(() => PricingCompareSchema.parse(input)).toThrow();
  });
});

describe('CostEstimateSchema', () => {
  it('validates required fields with defaults', () => {
    const input = {
      service_name: 'Virtual Machines',
      sku_name: 'Standard_D2s_v3',
      region: 'eastus'
    };
    const result = CostEstimateSchema.parse(input);
    expect(result.hours_per_month).toBe(730);
    expect(result.currency_code).toBe('USD');
  });

  it('validates complete valid input', () => {
    const input = {
      service_name: 'Virtual Machines',
      sku_name: 'Standard_D4s_v3',
      region: 'westeurope',
      hours_per_month: 160,
      currency_code: 'GBP' as const,
      discount_percentage: 20
    };
    expect(() => CostEstimateSchema.parse(input)).not.toThrow();
  });

  it('rejects empty service name', () => {
    const input = { service_name: '', sku_name: 'SKU', region: 'eastus' };
    expect(() => CostEstimateSchema.parse(input)).toThrow();
  });

  it('rejects empty sku name', () => {
    const input = { service_name: 'VM', sku_name: '', region: 'eastus' };
    expect(() => CostEstimateSchema.parse(input)).toThrow();
  });

  it('rejects empty region', () => {
    const input = { service_name: 'VM', sku_name: 'SKU', region: '' };
    expect(() => CostEstimateSchema.parse(input)).toThrow();
  });

  it('rejects negative hours per month', () => {
    const input = {
      service_name: 'VM',
      sku_name: 'SKU',
      region: 'eastus',
      hours_per_month: -10
    };
    expect(() => CostEstimateSchema.parse(input)).toThrow();
  });

  it('rejects hours per month above 744', () => {
    const input = {
      service_name: 'VM',
      sku_name: 'SKU',
      region: 'eastus',
      hours_per_month: 745
    };
    expect(() => CostEstimateSchema.parse(input)).toThrow();
  });

  it('accepts maximum hours per month of 744', () => {
    const input = {
      service_name: 'VM',
      sku_name: 'SKU',
      region: 'eastus',
      hours_per_month: 744
    };
    expect(() => CostEstimateSchema.parse(input)).not.toThrow();
  });

  it('rejects extra fields in strict mode', () => {
    const input = {
      service_name: 'VM',
      sku_name: 'SKU',
      region: 'eastus',
      extra: 'field'
    };
    expect(() => CostEstimateSchema.parse(input)).toThrow();
  });
});

describe('DiscoverSKUsSchema', () => {
  it('validates required fields with defaults', () => {
    const input = { service_name: 'Virtual Machines' };
    const result = DiscoverSKUsSchema.parse(input);
    expect(result.service_name).toBe('Virtual Machines');
    expect(result.price_type).toBe('Consumption');
    expect(result.limit).toBe(100);
  });

  it('validates complete valid input', () => {
    const input = {
      service_name: 'Storage',
      region: 'eastus',
      price_type: 'Reservation' as const,
      limit: 50
    };
    expect(() => DiscoverSKUsSchema.parse(input)).not.toThrow();
  });

  it('rejects empty service name', () => {
    const input = { service_name: '' };
    expect(() => DiscoverSKUsSchema.parse(input)).toThrow();
  });

  it('rejects missing service name', () => {
    const input = {};
    expect(() => DiscoverSKUsSchema.parse(input)).toThrow();
  });

  it('rejects limit below 1', () => {
    const input = { service_name: 'VM', limit: 0 };
    expect(() => DiscoverSKUsSchema.parse(input)).toThrow();
  });

  it('rejects limit above 1000', () => {
    const input = { service_name: 'VM', limit: 1001 };
    expect(() => DiscoverSKUsSchema.parse(input)).toThrow();
  });

  it('rejects invalid price type', () => {
    const input = { service_name: 'VM', price_type: 'Invalid' };
    expect(() => DiscoverSKUsSchema.parse(input)).toThrow();
  });

  it('rejects extra fields in strict mode', () => {
    const input = { service_name: 'VM', extra: 'field' };
    expect(() => DiscoverSKUsSchema.parse(input)).toThrow();
  });
});

describe('SKUDiscoverySchema', () => {
  it('validates required fields with defaults', () => {
    const input = { service_hint: 'app service' };
    const result = SKUDiscoverySchema.parse(input);
    expect(result.service_hint).toBe('app service');
    expect(result.currency_code).toBe('USD');
    expect(result.limit).toBe(30);
  });

  it('validates complete valid input', () => {
    const input = {
      service_hint: 'web app',
      region: 'westus',
      currency_code: 'EUR' as const,
      limit: 50
    };
    expect(() => SKUDiscoverySchema.parse(input)).not.toThrow();
  });

  it('rejects empty service hint', () => {
    const input = { service_hint: '' };
    expect(() => SKUDiscoverySchema.parse(input)).toThrow();
  });

  it('rejects missing service hint', () => {
    const input = {};
    expect(() => SKUDiscoverySchema.parse(input)).toThrow();
  });

  it('rejects limit below 1', () => {
    const input = { service_hint: 'vm', limit: 0 };
    expect(() => SKUDiscoverySchema.parse(input)).toThrow();
  });

  it('rejects limit above 100', () => {
    const input = { service_hint: 'vm', limit: 101 };
    expect(() => SKUDiscoverySchema.parse(input)).toThrow();
  });

  it('rejects invalid currency code', () => {
    const input = { service_hint: 'vm', currency_code: 'INVALID' };
    expect(() => SKUDiscoverySchema.parse(input)).toThrow();
  });

  it('rejects extra fields in strict mode', () => {
    const input = { service_hint: 'vm', extra: 'field' };
    expect(() => SKUDiscoverySchema.parse(input)).toThrow();
  });
});

describe('CustomerDiscountSchema', () => {
  it('validates empty input', () => {
    const input = {};
    expect(() => CustomerDiscountSchema.parse(input)).not.toThrow();
  });

  it('validates with customer_id', () => {
    const input = { customer_id: 'customer-123' };
    expect(() => CustomerDiscountSchema.parse(input)).not.toThrow();
  });

  it('rejects extra fields in strict mode', () => {
    const input = { customer_id: 'customer-123', extra: 'field' };
    expect(() => CustomerDiscountSchema.parse(input)).toThrow();
  });
});
