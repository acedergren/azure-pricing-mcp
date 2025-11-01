"""Integration tests for Azure Pricing MCP Server API interactions."""

import pytest
from azure_pricing_server import AzurePricingServer


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_search():
    """Test actual API call to Azure Pricing API."""
    async with AzurePricingServer() as server:
        result = await server.search_azure_prices(
            service_name="Virtual Machines",
            region="eastus",
            limit=5
        )
        
        assert result is not None
        assert "count" in result
        assert "items" in result
        assert isinstance(result["items"], list)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_compare():
    """Test actual price comparison via API."""
    async with AzurePricingServer() as server:
        result = await server.compare_prices(
            service_name="Virtual Machines",
            sku_name="D2s v3",
            regions=["eastus", "westus"]
        )
        
        assert result is not None
        assert "comparisons" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_estimate():
    """Test actual cost estimation via API."""
    async with AzurePricingServer() as server:
        result = await server.estimate_costs(
            service_name="Virtual Machines",
            sku_name="D2s v3",
            region="eastus",
            hours_per_day=8,
            days_per_month=20
        )
        
        assert result is not None
        assert "monthly_cost" in result
        assert result["monthly_cost"] > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_discover_skus():
    """Test actual SKU discovery via API."""
    async with AzurePricingServer() as server:
        result = await server.discover_skus(
            service_name="Virtual Machines",
            region="eastus"
        )
        
        assert result is not None
        assert "skus" in result
        assert len(result["skus"]) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_rate_limiting():
    """Test that API handles rate limiting gracefully."""
    async with AzurePricingServer() as server:
        # Make multiple rapid requests
        for _ in range(3):
            result = await server.search_azure_prices(
                service_name="Virtual Machines",
                limit=5
            )
            assert result is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_pagination():
    """Test handling of paginated results from real API."""
    async with AzurePricingServer() as server:
        result = await server.search_azure_prices(
            service_name="Virtual Machines",
            limit=150
        )
        
        assert result is not None
        assert result["count"] >= 0
