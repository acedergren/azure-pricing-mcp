# API Reference

Complete reference for the Azure Pricing MCP Server tools and methods.

## MCP Tools

### azure_price_search

Search Azure retail prices with flexible filtering options.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `service_name` | string | No | - | Name of Azure service (e.g., "Virtual Machines") |
| `service_family` | string | No | - | Service family (e.g., "Compute") |
| `region` | string | No | - | Azure region (e.g., "eastus", "westeurope") |
| `sku_name` | string | No | - | SKU name (e.g., "D2s v3") |
| `price_type` | string | No | - | Price type: "Consumption", "Reservation", "Savings Plan" |
| `currency_code` | string | No | "USD" | Currency code (USD, EUR, GBP, etc.) |
| `limit` | integer | No | 50 | Maximum results to return (1-1000) |
| `discount_percentage` | number | No | - | Apply discount percentage (0-100) |
| `validate_sku` | boolean | No | true | Validate SKU names and suggest corrections |

**Returns:**

```json
{
  "count": 10,
  "items": [
    {
      "service_name": "Virtual Machines",
      "product_name": "Virtual Machines Dsv3 Series",
      "sku_name": "D2s v3",
      "region": "eastus",
      "location": "US East",
      "retail_price": 0.096,
      "unit": "1 Hour",
      "currency": "USD",
      "price_type": "Consumption",
      "meter_id": "...",
      "savings_plans": []
    }
  ],
  "applied_filters": {
    "service_name": "Virtual Machines",
    "region": "eastus"
  },
  "next_page": null
}
```

**Example Usage:**

```
"Find prices for D2s v3 VMs in East US"
"Search for Azure Storage prices in West Europe"
"Show me GPU VM pricing with 20% discount"
```

---

### azure_price_compare

Compare Azure prices across different regions or SKUs.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `service_name` | string | Yes | - | Name of Azure service |
| `sku_name` | string | No | - | Specific SKU to compare |
| `regions` | array[string] | No | - | List of regions to compare |
| `currency_code` | string | No | "USD" | Currency code |
| `discount_percentage` | number | No | - | Apply discount percentage |

**Returns:**

```json
{
  "service_name": "Virtual Machines",
  "sku_name": "D2s v3",
  "currency": "USD",
  "comparison_type": "regions",
  "comparisons": [
    {
      "region": "eastus",
      "location": "US East",
      "price": 0.096,
      "unit": "1 Hour"
    },
    {
      "region": "westeurope",
      "location": "West Europe",
      "price": 0.106,
      "unit": "1 Hour"
    }
  ],
  "cheapest": {
    "region": "eastus",
    "price": 0.096
  },
  "price_difference": {
    "min": 0.096,
    "max": 0.106,
    "difference": 0.010,
    "percentage": 10.42
  }
}
```

**Example Usage:**

```
"Compare D2s v3 VM prices between East US and West Europe"
"Show storage price differences across all US regions"
```

---

### azure_cost_estimate

Estimate monthly costs based on usage patterns.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `service_name` | string | Yes | - | Name of Azure service |
| `sku_name` | string | Yes | - | SKU to estimate costs for |
| `region` | string | Yes | - | Azure region |
| `hours_per_month` | number | No | 730 | Hours of usage per month (max 744) |
| `currency_code` | string | No | "USD" | Currency code |
| `discount_percentage` | number | No | - | Apply discount percentage |

**Returns:**

```json
{
  "service_name": "Virtual Machines",
  "sku_name": "D2s v3",
  "region": "eastus",
  "product_name": "Virtual Machines Dsv3 Series",
  "unit_of_measure": "1 Hour",
  "currency": "USD",
  "on_demand_pricing": {
    "hourly_rate": 0.096,
    "daily_cost": 2.30,
    "monthly_cost": 70.08,
    "yearly_cost": 840.96
  },
  "usage_assumptions": {
    "hours_per_month": 730,
    "hours_per_day": 24.0
  },
  "savings_plans": [
    {
      "term": "1 Year",
      "hourly_rate": 0.068,
      "monthly_cost": 49.64,
      "savings_percentage": 29.17
    }
  ]
}
```

**Example Usage:**

```
"Estimate costs for running a D4s v3 VM 12 hours per day"
"Calculate monthly cost for B2s VM running 24/7"
```

---

### azure_discover_skus

Discover available SKUs for an Azure service.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `service_name` | string | Yes | - | Name of Azure service |
| `region` | string | No | - | Filter by specific region |
| `price_type` | string | No | "Consumption" | Type of pricing |
| `currency_code` | string | No | "USD" | Currency code |

**Returns:**

```json
{
  "service_name": "Virtual Machines",
  "skus": [
    {
      "sku_name": "D2s v3",
      "arm_sku_name": "Standard_D2s_v3",
      "product_name": "Virtual Machines Dsv3 Series",
      "sample_price": 0.096,
      "unit_of_measure": "1 Hour",
      "meter_name": "D2s v3",
      "sample_region": "eastus",
      "available_regions": ["eastus", "westus", "westeurope"]
    }
  ],
  "total_skus": 150,
  "price_type": "Consumption",
  "region_filter": null
}
```

**Example Usage:**

```
"Show all VM SKUs available in East US"
"List Azure SQL Database service tiers"
"What App Service plans are available?"
```

---

### azure_sku_discovery

Intelligent SKU discovery with fuzzy matching and natural language support.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `service_hint` | string | Yes | - | Natural language service description |
| `region` | string | No | - | Preferred region |
| `currency_code` | string | No | "USD" | Currency code |
| `limit` | integer | No | 30 | Maximum results |

**Returns:**

```json
{
  "query": "web app hosting",
  "matched_services": [
    {
      "service_name": "Azure App Service",
      "service_family": "Compute",
      "confidence": 0.95
    }
  ],
  "skus": [
    {
      "service_name": "Azure App Service",
      "sku_name": "P1 v2",
      "price": 0.20,
      "region": "eastus",
      "description": "Premium v2 tier, 1 Core, 3.5 GB RAM"
    }
  ],
  "total_results": 25,
  "suggestions": [
    "Try: 'Azure App Service pricing'",
    "Related: 'Azure Functions', 'Container Instances'"
  ]
}
```

**Example Usage:**

```
"Find pricing for web app hosting"
"Show me database options for SQL workloads"
"What's available for container hosting?"
```

---

## Python API Reference

### AzurePricingServer Class

Main server class handling Azure Pricing API interactions.

#### Constructor

```python
server = AzurePricingServer()
```

#### Context Manager Usage

```python
async with AzurePricingServer() as server:
    result = await server.search_azure_prices(...)
```

#### Methods

##### search_azure_prices()

```python
async def search_azure_prices(
    self,
    service_name: Optional[str] = None,
    service_family: Optional[str] = None,
    region: Optional[str] = None,
    sku_name: Optional[str] = None,
    price_type: Optional[str] = None,
    currency_code: str = "USD",
    limit: int = 50,
    discount_percentage: Optional[float] = None,
    validate_sku: bool = True
) -> Dict[str, Any]
```

##### compare_prices()

```python
async def compare_prices(
    self,
    service_name: str,
    sku_name: Optional[str] = None,
    regions: Optional[List[str]] = None,
    currency_code: str = "USD",
    discount_percentage: Optional[float] = None
) -> Dict[str, Any]
```

##### estimate_costs()

```python
async def estimate_costs(
    self,
    service_name: str,
    sku_name: str,
    region: str,
    hours_per_month: float = 730,
    currency_code: str = "USD",
    discount_percentage: Optional[float] = None
) -> Dict[str, Any]
```

##### discover_skus()

```python
async def discover_skus(
    self,
    service_name: str,
    region: Optional[str] = None,
    price_type: str = "Consumption",
    currency_code: str = "USD"
) -> Dict[str, Any]
```

##### search_azure_prices_with_fuzzy_matching()

```python
async def search_azure_prices_with_fuzzy_matching(
    self,
    service_name: Optional[str] = None,
    service_family: Optional[str] = None,
    region: Optional[str] = None,
    sku_name: Optional[str] = None,
    price_type: Optional[str] = None,
    currency_code: str = "USD",
    limit: int = 50
) -> Dict[str, Any]
```

##### discover_service_skus()

```python
async def discover_service_skus(
    self,
    service_hint: str,
    region: Optional[str] = None,
    currency_code: str = "USD",
    limit: int = 30
) -> Dict[str, Any]
```

---

## Error Handling

### Error Response Format

```json
{
  "error": "Error message",
  "error_type": "ValidationError",
  "details": {
    "parameter": "sku_name",
    "value": "invalid-sku"
  }
}
```

### Common Error Codes

- **400 Bad Request**: Invalid parameters
- **404 Not Found**: No results for given filters
- **429 Too Many Requests**: Rate limit exceeded (automatically retried)
- **500 Internal Server Error**: Server-side error
- **503 Service Unavailable**: Azure API unavailable

---

## Rate Limiting

The server automatically handles rate limiting:
- **Max retries**: 3
- **Backoff strategy**: Exponential (5s, 10s, 15s)
- **Auto-retry on 429**: Yes

---

## Data Types

### Region Codes

Common Azure region codes:
- `eastus` - East US
- `eastus2` - East US 2
- `westus` - West US
- `westus2` - West US 2
- `centralus` - Central US
- `westeurope` - West Europe
- `northeurope` - North Europe
- `uksouth` - UK South
- `ukwest` - UK West
- `southeastasia` - Southeast Asia
- `eastasia` - East Asia

### Currency Codes

Supported currencies (ISO 4217):
- `USD` - US Dollar
- `EUR` - Euro
- `GBP` - British Pound
- `CAD` - Canadian Dollar
- `AUD` - Australian Dollar
- `JPY` - Japanese Yen
- `INR` - Indian Rupee
- And more...

### Price Types

- `Consumption` - Pay-as-you-go pricing
- `Reservation` - Reserved instances (1 or 3 years)
- `Savings Plan` - Savings plan pricing

---

## Pagination

Results are automatically paginated:
- **Default page size**: 100 items per request
- **Max limit**: 1000 items
- **Next page**: Handled automatically

---

## Best Practices

1. **Use specific filters** for faster results
2. **Enable SKU validation** to catch typos
3. **Cache results** when possible
4. **Handle errors gracefully**
5. **Use regions close to users** for better performance

---

For more examples, see [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md).
