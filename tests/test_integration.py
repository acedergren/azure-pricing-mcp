"""Integration tests for Azure Pricing MCP Server.

These tests may make actual API calls and should be run separately.
Mark them with @pytest.mark.integration to skip during regular test runs.
"""

import pytest

from azure_pricing_server import AzurePricingServer


@pytest.mark.integration
class TestAzurePricingIntegration:
    """Integration tests that make real API calls."""

    @pytest.mark.asyncio
    async def test_real_api_search(self):
        """Test actual API search (requires network)."""
        async with AzurePricingServer() as server:
            result = await server.search_azure_prices(
                service_name="Virtual Machines", region="eastus", limit=5
            )

            assert result is not None
            assert "items" in result
            assert "count" in result
            # We can't guarantee results, but the call should succeed
            assert result["count"] >= 0

    @pytest.mark.asyncio
    async def test_real_api_compare(self):
        """Test actual API price comparison (requires network)."""
        async with AzurePricingServer() as server:
            result = await server.compare_prices(
                service_name="Virtual Machines", sku_name="D2s v3", regions=["eastus", "westus"]
            )

            assert result is not None
            assert "comparisons" in result

    @pytest.mark.asyncio
    async def test_real_api_estimate(self):
        """Test actual API cost estimation (requires network)."""
        async with AzurePricingServer() as server:
            result = await server.estimate_costs(
                service_name="Virtual Machines",
                sku_name="D2s v3",
                region="eastus",
                hours_per_month=730,
            )

            assert result is not None
            assert "on_demand_pricing" in result
            assert "monthly_cost" in result["on_demand_pricing"]
